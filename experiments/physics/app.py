# from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase

from panda3d.core import VBase4, Vec3, PerspectiveLens, ClockObject, DirectionalLight, AmbientLight
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode

from ..exposed_joint_rig import ExposedJointRig
from ..control_joint_rig import ControlJointRig
from ..rigid_body_rig import RigidBodyRig

# TEMP
from direct.actor.Actor import Actor
from panda3d.core import LineSegs
from pandac.PandaModules import CharacterJoint

def draw_joints(joint_list, color):
    for node, parent in joint_list:
        if parent is not None:
            lines = LineSegs()
            lines.setThickness(5.0)
            lines.setColor(*color)
            lines.moveTo(0, 0, 0)
            lines.drawTo(node.getPos(parent))

            np = parent.attachNewNode(lines.create())
            np.setDepthWrite(False)
            np.setDepthTest(False)

def walk_joints(actor, part, joint_list, parent, node_fn):
    if isinstance(part, CharacterJoint):
        node = node_fn(actor, part)
        joint_list.append((node, parent))
        parent = node

    for child in part.get_children():
        walk_joints(actor, child, joint_list, parent, node_fn)

class App(ShowBase):

    def __init__(self, width, height):
        ShowBase.__init__(self)

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        self.setBackgroundColor(0.9, 0.9, 0.9)
        self.createLighting()
        self.setupCamera(width, height)

        # self.world = BulletWorld()
        # self.world.setGravity(Vec3(0, 0, -9.81))
        # self.setupDebug()
        # self.createPlane()

        actor = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        actor.reparentTo(self.render)
        actor.setPos(0, 0, 0)

        exposed_joints = []
        exposed_joint_gen = walk_joints(actor, actor.getPartBundle('modelRoot'), exposed_joints, None, \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        draw_joints(exposed_joints, (0.5, 0.75, 1.0, 1.0))

        actor.pose('walk', 0)
        actor.update(force=True)

        # exposed_rig = ExposedJointRig('walking', { 'walk': 'walking-animation.egg' }, VBase4(0.5, 0.75, 1.0, 1.0))
        # exposed_rig.reparentTo(self.render)
        # exposed_rig.actor.loop('walk')

        # control_rig = ControlJointRig('walking', VBase4(1.0, 0.75, 0.5, 1.0))
        # control_rig.reparentTo(self.render)

        self.accept('escape', sys.exit)
        # self.taskMgr.add(self.update, 'update')

    def setupDebug(self):
        node = BulletDebugNode('Debug')
        node.showWireframe(True)
        self.world.setDebugNode(node)
        np = self.render.attachNewNode(node)
        np.show()

    def createLens(self, aspect_ratio):
        lens = PerspectiveLens()
        lens.setFov(60)
        lens.setAspectRatio(aspect_ratio)
        lens.setNearFar(1.0, 1000.0)
        return lens

    def setupCamera(self, width, height):
        self.cam.setPos(0, -200, 0)
        self.cam.lookAt(0, 0, 0)
        self.cam.node().setLens(self.createLens(width / height))

    def createLighting(self):
        light = DirectionalLight('light')
        light.set_color(VBase4(0.2, 0.2, 0.2, 1))

        np = self.render.attach_new_node(light)
        np.setPos(0, -200, 0)
        np.lookAt(0, 0, 0)

        self.render.set_light(np)

        light = AmbientLight('ambient')
        light.set_color(VBase4(0.4, 0.4, 0.4, 1))

        np = self.render.attachNewNode(light)

        self.render.setLight(np)

    def createPlane(self):
        rb = BulletRigidBodyNode('Ground')
        rb.addShape(BulletPlaneShape(Vec3(0, 0, 1), 1))
        rb.setFriction(1.0)

        np = self.render.attachNewNode(rb)
        np.setPos(Vec3(0, 0, -100))

        self.world.attachRigidBody(rb)

        return np

    def update(self, task):
        # dt = globalClock.getDt()
        # self.world.doPhysics(dt, 10, 1.0 / 60.0)
        return task.cont
