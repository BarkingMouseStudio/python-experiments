from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase

from panda3d.core import VBase4, Vec3, PerspectiveLens, TransformState, ClockObject, DirectionalLight, AmbientLight, BitMask32
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode

from ..exposed_joint_rig import ExposedJointRig
from ..control_joint_rig import ControlJointRig
from ..rigid_body_rig import RigidBodyRig

from ..utils.keras_utils import load_model

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        self.setBackgroundColor(0.9, 0.9, 0.9)
        self.createLighting()

        if not headless:
            self.setupCamera(width, height)

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81 * 10.0))
        self.setupDebug()
        self.createPlane()

        self.animated_rig = ExposedJointRig('walking', { 'walk': 'walking-animation.egg' })
        self.animated_rig.reparentTo(self.render)
        self.animated_rig.setPos(0, 0, -98)
        self.animated_rig.createLines(VBase4(0.5, 0.75, 1.0, 1.0))
        self.animated_rig.pose('walk', 0)

        self.physical_rig = RigidBodyRig()
        self.physical_rig.reparentTo(self.render)
        self.physical_rig.setPos(0, 0, -98)
        self.physical_rig.createColliders(self.animated_rig)
        self.physical_rig.createConstraints()
        self.physical_rig.setCollideMask(BitMask32.bit(1))
        self.physical_rig.attachRigidBodies(self.world)
        self.physical_rig.attachConstraints(self.world)
        self.physical_rig.matchPose(self.animated_rig)

        self.target_physical_rig = RigidBodyRig()
        self.target_physical_rig.reparentTo(self.render)
        self.target_physical_rig.setPos(0, 0, -98)
        self.target_physical_rig.createColliders(self.animated_rig)
        self.target_physical_rig.createConstraints()
        self.target_physical_rig.setCollideMask(BitMask32.bit(2))
        self.target_physical_rig.attachRigidBodies(self.world)
        self.target_physical_rig.attachConstraints(self.world)
        self.target_physical_rig.matchPose(self.animated_rig)

        self.control_rig = ControlJointRig('walking')
        self.control_rig.reparentTo(self.render)
        self.control_rig.setPos(0, 0, -98)
        self.control_rig.createLines(VBase4(1.0, 0.75, 0.5, 1.0))
        self.control_rig.matchPhysicalPose(self.physical_rig)

        self.disableCollisions()

        self.frame_count = self.animated_rig.getNumFrames('walk')

        self.model = load_model('model.json', 'weights.hdf5')
        self.err_sum = 0.0

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

    def setupCamera(self, width, height):
        self.cam.setPos(-200, -100, 0)
        self.cam.lookAt(0, -100, 0)
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
        np.setCollideMask(BitMask32.bit(0))

        self.world.attachRigidBody(rb)

        return np

    def update(self, task):
        frame = globalClock.getFrameCount()

        joint_positions = self.physical_rig.getJointPositions()
        joint_rotations = self.physical_rig.getJointRotations()

        linear_velocities = self.physical_rig.getLinearVelocities()
        angular_velocities = self.physical_rig.getAngularVelocities()

        self.animated_rig.pose('walk', frame % self.frame_count)
        self.target_physical_rig.matchPose(self.animated_rig)

        next_joint_positions = self.target_physical_rig.getJointPositions()
        next_joint_rotations = self.target_physical_rig.getJointRotations()

        target_directions = next_joint_positions - joint_positions
        target_rotations = next_joint_rotations - joint_rotations

        X = np.concatenate([
            joint_positions,
            joint_rotations,
            linear_velocities,
            angular_velocities,
            target_directions,
            target_rotations
        ])

        Y = self.model.predict(np.array([X]))

        self.physical_rig.apply_forces(Y[0] * 100.0)
        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)

        err = self.target_physical_rig.compareTo(self.physical_rig)
        self.err_sum += math.pow(err, 2.0)

        err_rmse = math.sqrt(self.err_sum / frame)
        print err_rmse

        if err_rmse > 40:
            self.physical_rig.matchPose(self.animated_rig)

        return task.cont
