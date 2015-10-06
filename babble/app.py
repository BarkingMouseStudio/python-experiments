from __future__ import division

import cPickle as pickle
import random
import sys
import numpy as np

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor

from panda3d import bullet
from panda3d.core import Vec3, PerspectiveLens, ClockObject, DirectionalLight
from pandac.PandaModules import CharacterJoint, LineSegs

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

def draw_joints(joints, lines=True, nodes=False):
    for node, parent in joints:
        lines = LineSegs()
        lines.set_thickness(3.0)
        lines.move_to(0, 0, 0)
        lines.draw_to(node.get_pos(parent))

        parent.attach_new_node(lines.create())

        model = loader.loadModel("icosphere.egg")
        model.reparent_to(node)

def walk_joints(actor, part, joint_list, parent=None):
    if isinstance(part, CharacterJoint):
        node = actor.exposeJoint(None, 'modelRoot', part.get_name())

        if parent and parent.get_name() != 'root':
            joint_list.append((node, parent))

        parent = node

    for child in part.get_children():
        walk_joints(actor, child, joint_list, parent)

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        self.save_path = args['<save_path>']
        self.train_count = 100000
        self.test_count = 10000
        self.iteration_count = 0

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        # self.toggleWireframe()
        # self.disableMouse() # just disables camera movement with mouse

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        if not headless:
            self.cam.set_pos(0, -200, 0)
            self.cam.look_at(0, 0, 0)
            self.cam.node().set_lens(create_lens(width / height))

        self.rig = Actor('walking.egg', {
            'walk': 'walking-animation.egg'
        })
        self.rig.reparent_to(self.render)
        self.rig.set_bin('background', 1)
        self.rig.loop('walk')

        self.joints = []
        walk_joints(self.rig, self.rig.getPartBundle('modelRoot'), self.joints, None)
        draw_joints(self.joints, lines=True, nodes=True)

        # self.arm = Arm(self.render)

        self.X_train = []
        self.Y_train = []

        self.X_test = []
        self.Y_test = []

        self.accept('escape', sys.exit)
        # self.taskMgr.add(self.update, 'update')

    def save(self):
        print 'saving...', self.save_path
        data = ((self.X_train, self.Y_train), (self.X_test, self.Y_test))

        f = open(self.save_path, 'wb')
        pickle.dump(data, f)
        f.close()

    def flatten_vectors(self, arr, angle=False):
        res = np.array([[v.get_x(), v.get_y(), v.get_z()] for v in arr]).flatten()
        return get_angle_vec(res) if angle else res

    def generate(self):
        if self.iteration_count % 100 == 0:
            shoulder_rotation = np.random.choice(self.home_position, 3)
            elbow_rotation = np.random.choice(self.home_position, 3)

            self.arm.shoulder_pivot.set_hpr(*shoulder_rotation)
            self.arm.elbow_pivot.set_hpr(*elbow_rotation)

            self.prev_joint_positions = [joint.get_pos(self.arm.arm_pivot) for joint in self.arm.joints]
            self.prev_joint_rotations = [joint.get_hpr(self.arm.arm_pivot) for joint in self.arm.joints]

            self.home_count += 1

        joint_positions = [joint.get_pos(self.arm.arm_pivot) for joint in self.arm.joints]
        joint_rotations = [joint.get_hpr(self.arm.arm_pivot) for joint in self.arm.joints]
        linear_velocities = [joint_position - self.prev_joint_positions[i] for i, joint_position in enumerate(joint_positions)]
        angular_velocities = [joint_rotation - self.prev_joint_rotations[i] for i, joint_rotation in enumerate(joint_rotations)]

        shoulder_rotation = np.random.uniform(-5.0, 5.0, 3)
        elbow_rotation = np.random.uniform(-5.0, 5.0, 3)

        self.arm.rotate_shoulder(*shoulder_rotation)
        self.arm.rotate_elbow(*elbow_rotation)

        next_joint_positions = [joint.get_pos(self.arm.arm_pivot) for joint in self.arm.joints]
        next_joint_rotations = [joint.get_hpr(self.arm.arm_pivot) for joint in self.arm.joints]

        target_directions = [next_joint_position - joint_positions[i] for i, next_joint_position in enumerate(next_joint_positions)]
        target_rotations = [next_joint_rotation - joint_rotations[i] for i, next_joint_rotation in enumerate(next_joint_rotations)]

        position = self.flatten_vectors(joint_positions) / 10.0
        rotation = self.flatten_vectors(joint_rotations) / 180.0
        linear_velocity = self.flatten_vectors(linear_velocities) / 5.0
        angular_velocity = self.flatten_vectors(angular_velocities, angle=True) / 180.0
        target_direction = self.flatten_vectors(target_directions) / 5.0
        target_rotation = self.flatten_vectors(target_rotations, angle=True) / 180.0

        X = np.concatenate([position, rotation, linear_velocity, angular_velocity, target_direction, target_rotation])

        Y = np.concatenate([shoulder_rotation, elbow_rotation]) / 5.0

        self.prev_joint_positions = joint_positions
        self.prev_joint_rotations = joint_rotations

        self.iteration_count += 1

        return X, Y

    def update(self, task):
        train_complete = len(self.X_train) == self.train_count
        test_complete = len(self.X_test) == self.test_count

        if not train_complete: # motor babbling
            X, Y = self.generate()
            self.X_train.append(X)
            self.Y_train.append(Y)
        elif not test_complete: # move positions
            X, Y = self.generate()
            self.X_test.append(X)
            self.Y_test.append(Y)

        if train_complete and test_complete:
            self.save()
            sys.exit()
            return task.done

        total_completed = len(self.X_train) + len(self.X_test)
        total_count = self.train_count + self.test_count

        print 'progress: %f%%' % ((total_completed / total_count) * 100.0)

        return task.cont
