from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from keras.models import model_from_json

from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d import bullet
from panda3d.core import Vec3, PerspectiveLens, ClockObject, DirectionalLight

from arm import Arm

def create_lens(aspect_ratio):
    lens = PerspectiveLens()
    lens.setFov(60)
    lens.setAspectRatio(aspect_ratio)
    return lens

def get_angle(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle

get_angle_vec = np.vectorize(get_angle)

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        # self.toggleWireframe()
        self.disableMouse() # just disables camera movement with mouse

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        if not headless:
            self.cam.set_pos(0, -20, 0)
            self.cam.look_at(0, 0, 0)
            self.cam.node().set_lens(create_lens(width / height))

        self.model = self.load_model()

        self.model_arm = Arm(self.render, (1, 1, 1, 1))
        self.target_arm = Arm(self.render, (0.5, 0.5, 1, 1))

        home_positions = np.arange(0.0, 360.0, 45.0)
        pose_duration = 3.0
        poses = []

        for shoulder_home_position in home_positions:
            for elbow_home_position in home_positions:
                shoulder_pose = self.target_arm.shoulder_pivot.hprInterval(pose_duration, Vec3(0, 0, shoulder_home_position))
                elbow_pose = self.target_arm.elbow_pivot.hprInterval(pose_duration, Vec3(0, 0, elbow_home_position))
                poses.append(Parallel(shoulder_pose, elbow_pose))
                poses.append(Func(self.pose_complete))
                poses.append(Wait(1.0))

        poses.append(Func(self.done))

        print 'poses', len(poses)

        pose_sequence = Sequence(*poses)
        pose_sequence.start()

        self.prev_joint_positions = [joint.get_pos(self.model_arm.arm_pivot) for joint in self.model_arm.joints]
        self.prev_joint_rotations = [joint.get_hpr(self.model_arm.arm_pivot) for joint in self.model_arm.joints]

        self.err_sum = 0.0
        self.err_mse = 0.0
        self.next_switch = 0.0
        self.switch_interval = 0.1
        self.pose_index = 0
        self.should_stop = False

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def pose_complete(self):
        print 'pose complete', self.err_mse

    def done(self):
        print 'done', self.err_mse
        self.should_stop = True

    def load_model(self):
        json = open('model.json', 'r').read()
        model = model_from_json(json)
        model.load_weights('weights.hdf5')
        return model

    def flatten_vectors(self, arr, angle=False):
        res = np.array([[v.get_x(), v.get_y(), v.get_z()] for v in arr]).flatten()
        return get_angle_vec(res) if angle else res

    def update(self, task):
        joint_positions = [joint.get_pos(self.model_arm.arm_pivot) for joint in self.model_arm.joints]
        joint_rotations = [joint.get_hpr(self.model_arm.arm_pivot) for joint in self.model_arm.joints]
        linear_velocities = [joint_position - self.prev_joint_positions[i] for i, joint_position in enumerate(joint_positions)]
        angular_velocities = [joint_rotation - self.prev_joint_rotations[i] for i, joint_rotation in enumerate(joint_rotations)]

        next_joint_positions = [joint.get_pos(self.target_arm.arm_pivot) for joint in self.target_arm.joints]
        next_joint_rotations = [joint.get_hpr(self.target_arm.arm_pivot) for joint in self.target_arm.joints]

        target_directions = [next_joint_position - joint_positions[i] for i, next_joint_position in enumerate(next_joint_positions)]
        target_rotations = [next_joint_rotation - joint_rotations[i] for i, next_joint_rotation in enumerate(next_joint_rotations)]

        position = self.flatten_vectors(joint_positions) / 10.0
        rotation = self.flatten_vectors(joint_rotations) / 180.0
        linear_velocity = self.flatten_vectors(linear_velocities) / 5.0
        angular_velocity = self.flatten_vectors(angular_velocities, angle=True) / 180.0
        target_direction = self.flatten_vectors(target_directions) / 5.0
        target_rotation = self.flatten_vectors(target_rotations, angle=True) / 180.0

        X = np.concatenate([position, rotation, linear_velocity, angular_velocity, target_direction, target_rotation])
        Y = self.model.predict(np.array([X]))[0] * 5.0

        self.model_arm.rotate_shoulder(*Y[:3])
        self.model_arm.rotate_elbow(*Y[3:])

        err = 0.0
        for i, model_joint in enumerate(self.model_arm.joints):
            target_joint = self.target_arm.joints[i]
            diff = model_joint.get_pos(self.model_arm.arm_pivot) - target_joint.get_pos(self.target_arm.arm_pivot)
            err += diff.length()

        self.err_sum += math.pow(err, 2.0)
        self.err_mse = self.err_sum / globalClock.getFrameCount()

        self.prev_joint_positions = joint_positions
        self.prev_joint_rotations = joint_rotations

        if self.should_stop:
            sys.exit()
            return task.done

        return task.cont
