from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor

from panda3d.core import Vec3, Quat, PerspectiveLens, ClockObject, DirectionalLight
from pandac.PandaModules import CharacterJoint, LineSegs

from ..utils import create_lens, walk_joints, draw_joints, match_pose, apply_control_joints, filter_joints, load_model, flatten_vectors, rotate_node, measure_error

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        if not headless:
            self.cam.set_pos(0, -300, 100)
            self.cam.look_at(0, 0, 100)
            self.cam.node().set_lens(create_lens(width / height))

        # inputs
        self.accept('escape', sys.exit)

        # animated rig (cannot have control joints)
        self.animated_rig = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.animated_rig.reparent_to(self.render)
        self.animated_rig.set_pos(-50, 0, 0)
        self.animated_rig.pose('walk', 0)

        self.num_frames = self.animated_rig.getNumFrames('walk')

        self.animated_joint_list = []
        walk_joints(self.animated_rig, self.animated_rig.getPartBundle('modelRoot'), self.animated_joint_list, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        draw_joints(self.animated_joint_list)

        # rig with control joints (prevents animation)
        self.control_rig = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.control_rig.reparent_to(self.render)
        self.control_rig.set_pos(50, 0, 0)

        self.joint_list = []
        walk_joints(self.control_rig, self.control_rig.getPartBundle('modelRoot'), self.joint_list, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        draw_joints(self.joint_list)

        self.control_joint_list = []
        walk_joints(self.control_rig, self.control_rig.getPartBundle('modelRoot'), self.control_joint_list, None, lambda actor, part: actor.controlJoint(None, 'modelRoot', part.get_name()))
        match_pose(self.animated_joint_list, self.control_joint_list)
        apply_control_joints(self.control_joint_list, self.joint_list)

        self.animated_joint_list = filter_joints(self.animated_joint_list, 'RightUpLeg')
        self.control_joint_list = filter_joints(self.control_joint_list, 'RightUpLeg')
        self.joint_list = filter_joints(self.joint_list, 'RightUpLeg')

        self.prev_joint_positions = [node.get_pos(self.control_rig) for node, parent in self.joint_list]
        self.prev_joint_rotations = [node.get_hpr(self.control_rig) for node, parent in self.joint_list]

        self.model = load_model('model.json', 'weights.hdf5')
        self.err_sum = 0.0
        self.err_mse = 0.0

        self.taskMgr.add(self.update, 'update')

    def update(self, task):
        frame_count = globalClock.getFrameCount()
        self.animated_rig.pose('walk', frame_count % self.num_frames)

        joint_positions = [node.get_pos(self.control_rig) for node, parent in self.joint_list]
        joint_rotations = [node.get_hpr(self.control_rig) for node, parent in self.joint_list]

        linear_velocities = [joint_position - prev_joint_position for joint_position, prev_joint_position in zip(joint_positions, self.prev_joint_positions)]
        angular_velocities = [joint_rotation - prev_joint_rotation for joint_rotation, prev_joint_rotation in zip(joint_rotations, self.prev_joint_rotations)]

        next_joint_positions = [node.get_pos(self.animated_rig) for node, parent in self.animated_joint_list]
        next_joint_rotations = [node.get_hpr(self.animated_rig) for node, parent in self.animated_joint_list]

        target_directions = [next_joint_position - joint_position for next_joint_position, joint_position in zip(next_joint_positions, joint_positions)]
        target_rotations = [next_joint_rotation - joint_rotation for next_joint_rotation, joint_rotation in zip(next_joint_rotations, joint_rotations)]

        position = flatten_vectors(joint_positions) / 200.0
        rotation = flatten_vectors(joint_rotations) / 180.0
        linear_velocity = flatten_vectors(linear_velocities) / 50.0
        angular_velocity = flatten_vectors(angular_velocities, angle=True) / 180.0
        target_direction = flatten_vectors(target_directions) / 50.0
        target_rotation = flatten_vectors(target_rotations, angle=True) / 180.0

        X = np.concatenate([position, rotation, linear_velocity, angular_velocity, target_direction, target_rotation])
        Y = self.model.predict(np.array([X]))[0]

        for i, joint_pair in enumerate(self.control_joint_list):
            node, parent = joint_pair
            start = i * 3
            end = start + 3
            local_rotation = Y[start:end]
            rotate_node(node, *local_rotation)
        apply_control_joints(self.control_joint_list, self.joint_list)

        self.prev_joint_positions = joint_positions
        self.prev_joint_rotations = joint_rotations

        err = measure_error(self.control_joint_list, self.animated_joint_list)
        self.err_sum += math.pow(err, 2.0)
        self.err_mse = self.err_sum / frame_count

        print self.err_mse

        return task.cont
