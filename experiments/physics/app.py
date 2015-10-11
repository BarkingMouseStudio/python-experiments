# from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase

from direct.task import Task
from direct.actor.Actor import Actor

from panda3d.core import Vec3, Quat, PerspectiveLens, ClockObject, DirectionalLight
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletBoxShape, BulletRigidBodyNode, BulletDebugNode
from pandac.PandaModules import CharacterJoint

from ..utils import create_lens, walk_joints, draw_joints, match_pose, apply_control_joints, filter_joints, load_model, flatten_vectors, rotate_node, measure_error, get_angle_vec

excluded_joints = ['LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3']

class App(ShowBase):

    def __init__(self, width, height):
        ShowBase.__init__(self)

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        self.cam.set_pos(-300, -100, 100)
        self.cam.look_at(0, -100, 100)
        self.cam.node().set_lens(create_lens(width / height))

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        self.setup_debug()

        # self.create_plane(Vec3(0, 0, -1), Vec3(10, 10, 10))

        self.rig = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.rig.reparent_to(self.render)
        self.rig.set_pos(0, 0, 0)
        self.rig.set_bin('background', 1)

        self.num_frames = self.rig.getNumFrames('walk')

        self.joints = []
        walk_joints(self.rig, self.rig.getPartBundle('modelRoot'), self.joints, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        self.joints = [(node, parent) for node, parent in self.joints if node.get_name() not in excluded_joints]

        self.walk_joints(self.rig, self.rig.getPartBundle('modelRoot'), [])
        self.rig.setPlayRate(0.5, 'walk')
        self.rig.loop('walk')

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def walk_joints(self, actor, part, parents):
        parents = list(parents)

        if isinstance(part, CharacterJoint):
            node = actor.exposeJoint(None, 'modelRoot', part.get_name())

            if len(parents) > 0:
                parent = parents[-1]

                max_mass = 5.0
                min_mass = 0.0
                parents_multiplier = 1.0
                parents_factor = 2.0
                mass = min(max_mass * (parents_factor / (len(parents) * parents_multiplier)) + min_mass, max_mass)

                pos = node.get_pos(parent)
                m = pos / 2.0
                l = pos.length() / 2.0
                scale = Vec3(mass, l, mass)

                # box_rb = BulletRigidBodyNode('Box')
                # box_rb.setMass(1.0)
                # box_rb.addShape(BulletBoxShape(scale))
                # box_rb.setKinematic(True)
                #
                # self.world.attachRigidBody(box_rb)

                # box_np = parent.attachNewNode(box_rb)
                # box_np.setPos(m)
                # box_np.lookAt(node)

                model = self.loader.loadModel('cube.egg')
                model.flattenLight()
                model.reparentTo(parent)
                model.setPos(m)
                model.lookAt(node)
                model.setScale(Vec3(scale))

            parent = node
            parents.append(parent)

        for child in part.get_children():
            self.walk_joints(actor, child, parents)

    def create_box(self, mass, pos, scale):
        node = BulletRigidBodyNode('Box')
        node.setMass(mass)
        node.addShape(BulletBoxShape(scale))
        node.setKinematic(True)
        np = self.render.attachNewNode(node)
        np.setPos(pos)
        self.world.attachRigidBody(node)
        return np

    def create_plane(self, pos, scale):
        node = BulletRigidBodyNode('Ground')
        node.addShape(BulletPlaneShape(Vec3(0, 0, 1), 1))
        np = self.render.attachNewNode(node)
        np.setPos(pos)
        np.setScale(scale)
        self.world.attachRigidBody(node)
        return np

    def setup_debug(self):
        node = BulletDebugNode('Debug')
        node.showWireframe(True)
        np = self.render.attachNewNode(node)
        np.show()
        self.world.setDebugNode(node)
        return np

    def update(self, task):
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 1, 1.0 / 60.0)
        return task.cont
