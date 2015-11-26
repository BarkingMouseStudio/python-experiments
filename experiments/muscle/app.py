from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase
from direct.filter.CommonFilters import CommonFilters

from panda3d.core import VBase4, Vec3, PerspectiveLens, TransformState, ClockObject, DirectionalLight, AmbientLight, BitMask32, AntialiasAttrib, Spotlight, Point3, NodePath, LineSegs
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode, BulletBoxShape, BulletHingeConstraint

from ..utils.math_utils import get_angle_vec
from ..utils.keras_utils import load_model

class Muscle:

    def __init__(self, F_max):
        self.F_max = F_max

    def drawLineSeg(self, loader, parent, start, end):
        lines = LineSegs()
        lines.setThickness(5.0)
        lines.setColor(VBase4(1, 0.5, 0.5, 1.0))
        lines.moveTo(start)
        lines.drawTo(end)

        np = parent.attachNewNode(lines.create())
        np.setDepthWrite(True)
        np.setDepthTest(True)

    def drawTestCube(self, loader, parent, pos):
        cube = loader.loadModel('cube')
        cube.reparentTo(parent)
        cube.setPos(pos)
        cube.setScale(Vec3(0.1, 0.1, 0.1))
        cube.setColor(VBase4(1, 0.5, 0.5, 1.0))

    def setupDebug(self, loader):
        self.drawTestCube(loader, self.a, self.a_pos)
        self.drawTestCube(loader, self.b, self.b_pos)
        self.drawTestCube(loader, self.a, self.joint_pos)

    def setA(self, a, a_pos):
        self.a = a
        self.a_pos = a_pos

    def setB(self, b, b_pos):
        self.b = b
        self.b_pos = b_pos

    def setJointCenter(self, joint_pos):
        self.joint_pos = joint_pos

    def getAttachmentA(self):
        return self.a.getTransform().compose(TransformState.makePos(self.a_pos)).getPos()

    def getAttachmentB(self):
        return self.b.getTransform().compose(TransformState.makePos(self.b_pos)).getPos()

    def getJointCenter(self):
        return self.a.getTransform().compose(TransformState.makePos(self.joint_pos)).getPos()

    def getMomentArm(self):
        d = self.getAttachmentB() - self.getAttachmentA()
        v = self.getAttachmentA() - self.getJointCenter()
        r = v.cross(d)
        return r

    def apply(self, u):
        F = u * self.F_max
        r = self.getMomentArm()

        self.applyTorque(self.a, +F, r)
        self.applyTorque(self.b, -F, r)

    def applyTorque(self, np, F, r):
        T = r * F
        np.node().applyTorque(T)

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        width = args['--width']
        height = args['--height']

        globalClock.setMode(ClockObject.MNonRealTime)
        globalClock.setDt(0.02) # 20ms per frame

        self.setBackgroundColor(0.9, 0.9, 0.9)
        self.createLighting()
        self.setupCamera(width, height, Vec3(0, -10, 10), Vec3(0, 0, 0))
        self.render.setShaderAuto()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        # self.setupDebug()

        self.createPlane(Vec3(0, 0, -1), Vec3(10, 10, 1))

        box_a = self.createBox(1.5, Vec3(2, 0, 1), Vec3(2, 1, 1), VBase4(0.5, 1, 0.5, 1.0))
        box_b = self.createBox(1.0, Vec3(-2, 0, 1), Vec3(2, 1, 1), VBase4(0.5, 0.5, 1, 1.0))

        constraint = BulletHingeConstraint(box_a.node(), box_b.node(), \
            Vec3(-2, 0, 0), Vec3(2, 0, 0), \
            Vec3(0, 1, 0), Vec3(0, 1, 0))
        self.world.attachConstraint(constraint, linked_collision=True)

        self.muscle = Muscle(30)
        self.muscle.setA(box_a, Vec3(-1, 0, 1))
        self.muscle.setB(box_b, Vec3(1, 0, 1))
        self.muscle.setJointCenter(Vec3(-2, 0, 0))
        # self.muscle.setupDebug(self.loader)

        self.disableCollisions()

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def disableCollisions(self):
        for i in range(32):
            self.world.setGroupCollisionFlag(i, i, False)
        self.world.setGroupCollisionFlag(0, 1, True)

    def setupDebug(self):
        node = BulletDebugNode('Debug')
        node.showWireframe(True)

        self.world.setDebugNode(node)

        np = self.render.attachNewNode(node)
        np.show()

    def createLens(self, aspect_ratio, fov=60.0, near=1.0, far=1000.0):
        lens = PerspectiveLens()
        lens.setFov(fov)
        lens.setAspectRatio(aspect_ratio)
        lens.setNearFar(near, far)
        return lens

    def setupCamera(self, width, height, pos, look):
        self.cam.setPos(pos)
        self.cam.lookAt(look)
        self.cam.node().setLens(self.createLens(width / height))

    def createLighting(self):
        light = DirectionalLight('light')
        light.setColor(VBase4(0.6, 0.6, 0.6, 1))
        light.setShadowCaster(True, 1024, 1024)
        light.getLens().setNearFar(1.0, 40.0)
        light.getLens().setFilmSize(40, 40)
        # light.showFrustum()

        np = self.render.attachNewNode(light)
        np.setPos(10, -10, 20)
        np.lookAt(0, 0, 0)

        self.render.setLight(np)

        light = AmbientLight('ambient')
        light.setColor(VBase4(0.4, 0.4, 0.4, 1))

        np = self.render.attachNewNode(light)

        self.render.setLight(np)

    def createBox(self, mass, pos, scale, color):
        rb = BulletRigidBodyNode('box')
        rb.addShape(BulletBoxShape(scale))
        rb.setMass(mass)
        rb.setLinearDamping(0.2)
        rb.setAngularDamping(0.9)
        rb.setFriction(1.0)
        rb.setAnisotropicFriction(1.0)
        rb.setRestitution(0.0)

        self.world.attachRigidBody(rb)

        np = self.render.attachNewNode(rb)
        np.setPos(pos)
        np.setCollideMask(BitMask32.bit(1))

        cube = self.loader.loadModel('cube')
        cube.setScale(scale)
        cube.setColor(color)
        cube.reparentTo(np)

        return np

    def createPlane(self, pos, scale):
        rb = BulletRigidBodyNode('plane')
        rb.addShape(BulletPlaneShape(Vec3(0, 0, 1), 1))
        rb.setFriction(1.0)
        rb.setAnisotropicFriction(1.0)
        rb.setRestitution(1.0)

        self.world.attachRigidBody(rb)

        np = self.render.attachNewNode(rb)
        np.setPos(pos)
        np.setCollideMask(BitMask32.bit(0))

        plane = self.loader.loadModel('cube')
        plane.setScale(scale)
        plane.setPos(Vec3(0, 0, 0))
        plane.setColor(VBase4(0.8, 0.8, 0.8, 1.0))
        plane.reparentTo(np)

        return np

    def update(self, task):
        self.muscle.apply(1.0)
        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)
        return task.cont
