from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase

from panda3d.core import VBase4, Vec3, PerspectiveLens, ClockObject, DirectionalLight, AmbientLight, BitMask32
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode

from ..exposed_joint_rig import ExposedJointRig
from ..control_joint_rig import ControlJointRig
from ..rigid_body_rig import RigidBodyRig

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        self.save_path = args['<save_path>']

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        if not headless:
            self.cam.set_pos(-300, -100, 100)
            self.cam.look_at(0, -100, 100)
            self.cam.node().set_lens(create_lens(width / height))

        # inputs
        self.accept('escape', sys.exit)

        # animated rig (cannot have control joints)
        self.animated_rig = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.animated_rig.reparent_to(self.render)
        self.animated_rig.set_pos(0, 0, 0)

        self.frame_count = self.animated_rig.getNumFrames('walk')
        self.babble_count = 10

        self.train_count = self.frame_count * self.babble_count * 300
        self.test_count = self.frame_count * self.babble_count * 10

        print self.train_count, self.test_count

        self.animated_joint_list = []
        walk_joints(self.animated_rig, self.animated_rig.getPartBundle('modelRoot'), self.animated_joint_list, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        self.animated_joint_list = [(node, parent) for node, parent in self.animated_joint_list if node.get_name() not in excluded_joints]
        draw_joints(self.animated_joint_list, (0.5, 0.75, 1.0))

        self.max_joint_angles = np.array(get_max_joint_angles(self.animated_rig, self.animated_joint_list, 'walk'))
        print 'max joint angle', self.max_joint_angles.max()

        # rig with control joints (prevents animation)
        self.control_rig = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.control_rig.reparent_to(self.render)
        self.control_rig.set_pos(0, 0, 0)

        self.exposed_joint_list = []
        walk_joints(self.control_rig, self.control_rig.getPartBundle('modelRoot'), self.exposed_joint_list, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        self.exposed_joint_list = [(node, parent) for node, parent in self.exposed_joint_list if node.get_name() not in excluded_joints]
        draw_joints(self.exposed_joint_list, (1.0, 0.75, 0.5))

        self.control_joint_list = []
        walk_joints(self.control_rig, self.control_rig.getPartBundle('modelRoot'), self.control_joint_list, None, lambda actor, part: actor.controlJoint(None, 'modelRoot', part.get_name()))
        self.control_joint_list = [(node, parent) for node, parent in self.control_joint_list if node.get_name() not in excluded_joints]

        self.animated_rig.pose('walk', 0)
        self.animated_rig.update(force=True)
        match_pose(self.animated_joint_list, self.control_joint_list)
        apply_control_joints(self.control_joint_list, self.exposed_joint_list)

        self.X_train = []
        self.Y_train = []

        self.X_test = []
        self.Y_test = []

        self.taskMgr.add(self.update, 'update')

    def save(self):
        print 'saving...', self.save_path
        data = ((self.X_train, self.Y_train), (self.X_test, self.Y_test))

        f = open(self.save_path, 'wb')
        pickle.dump(data, f)
        f.close()

    def generate(self, count):
        if count % self.babble_count == 0:
            self.animated_rig.pose('walk', int(count / self.babble_count) % self.num_frames)
            self.animated_rig.update(force=True)
            match_pose(self.animated_joint_list, self.control_joint_list)
            apply_control_joints(self.control_joint_list, self.exposed_joint_list)

            self.prev_joint_positions = [node.get_pos(parent) if parent is not None else node.get_pos() for node, parent in self.exposed_joint_list]
            self.prev_joint_rotations = [node.get_hpr(parent) if parent is not None else node.get_hpr() for node, parent in self.exposed_joint_list]

        joint_positions = [node.get_pos(parent) if parent is not None else node.get_pos() for node, parent in self.exposed_joint_list]
        joint_rotations = [node.get_hpr(parent) if parent is not None else node.get_hpr() for node, parent in self.exposed_joint_list]

        linear_velocities = [joint_position - prev_joint_position for joint_position, prev_joint_position in zip(joint_positions, self.prev_joint_positions)]
        angular_velocities = [joint_rotation - prev_joint_rotation for joint_rotation, prev_joint_rotation in zip(joint_rotations, self.prev_joint_rotations)]

        rotations = []
        for i, node_parent in enumerate(self.control_joint_list):
            node, parent = node_parent
            max_joint_angle = self.max_joint_angles[i]

            local_rotation = np.random.uniform(-max_joint_angle, max_joint_angle, 3)

            rotate_node(node, *local_rotation)
            rotations.append(local_rotation)
        apply_control_joints(self.control_joint_list, self.exposed_joint_list)

        next_joint_positions = [node.get_pos(parent) if parent is not None else node.get_pos() for node, parent in self.exposed_joint_list]
        next_joint_rotations = [node.get_hpr(parent) if parent is not None else node.get_hpr() for node, parent in self.exposed_joint_list]

        target_directions = [next_joint_position - joint_position for next_joint_position, joint_position in zip(next_joint_positions, joint_positions)]
        target_rotations = [next_joint_rotation - joint_rotation for next_joint_rotation, joint_rotation in zip(next_joint_rotations, joint_rotations)]

        joint_positions = flatten_vectors(joint_positions) / 20.0
        joint_rotations = flatten_vectors(joint_rotations) / 180.0
        linear_velocities = flatten_vectors(linear_velocities) / 20.0
        angular_velocities = get_angle_vec(flatten_vectors(angular_velocities)) / 180.0
        target_directions = flatten_vectors(target_directions) / 1.0
        target_rotations = get_angle_vec(flatten_vectors(target_rotations)) / 180.0

        X = np.concatenate([joint_positions, joint_rotations, linear_velocities, angular_velocities, target_directions, target_rotations])
        Y = np.concatenate(rotations) / self.max_joint_angles.max()

        self.prev_joint_positions = joint_positions
        self.prev_joint_rotations = joint_rotations

        return X, Y

    def update(self, task):
        curr_train_count = len(self.X_train)
        curr_test_count = len(self.X_test)

        train_complete = curr_train_count == self.train_count
        test_complete = curr_test_count == self.test_count

        if not train_complete: # motor babbling
            X, Y = self.generate(curr_train_count)
            self.X_train.append(X)
            self.Y_train.append(Y)
        elif not test_complete: # move positions
            X, Y = self.generate(curr_test_count)
            self.X_test.append(X)
            self.Y_test.append(Y)

        if train_complete and test_complete:
            self.save()
            sys.exit()
            return task.done

        total_completed = curr_train_count + curr_test_count
        total_count = self.train_count + self.test_count

        print 'progress: %f%%' % ((total_completed / total_count) * 100.0)

        return task.cont
