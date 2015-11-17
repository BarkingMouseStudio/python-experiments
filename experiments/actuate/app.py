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

from ..utils.math_utils import get_angle_vec
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
            self.setupCamera(width, height, Vec3(200, -100, -100), Vec3(0, 0, -100))

        self.world = BulletWorld()
        # self.world.setGravity(Vec3(0, 0, -9.81 * 10.0))
        self.world.setGravity(Vec3(0, 0, 0))
        self.setupDebug()
        self.createPlane(Vec3(0, 0, -200))

        self.animated_rig = ExposedJointRig('walking', { 'walk': 'walking-animation.egg' })
        self.animated_rig.reparentTo(self.render)
        self.animated_rig.setPos(0, 0, -98)
        self.animated_rig.createLines(VBase4(0.5, 0.75, 1.0, 1.0))

        self.physical_rig = RigidBodyRig()
        self.physical_rig.reparentTo(self.render)
        self.physical_rig.setPos(0, 0, -98)
        self.physical_rig.createColliders(self.animated_rig)
        self.physical_rig.createConstraints()
        self.physical_rig.setCollideMask(BitMask32.bit(1))
        self.physical_rig.attachRigidBodies(self.world)
        self.physical_rig.attachConstraints(self.world)

        self.target_physical_rig = RigidBodyRig()
        self.target_physical_rig.reparentTo(self.render)
        self.target_physical_rig.setPos(0, 0, -98)
        self.target_physical_rig.createColliders(self.animated_rig)
        self.target_physical_rig.createConstraints()
        self.target_physical_rig.setCollideMask(BitMask32.bit(2))
        self.target_physical_rig.attachRigidBodies(self.world)
        self.target_physical_rig.attachConstraints(self.world)
        self.target_physical_rig.clearMasses()

        self.animated_rig.pose('walk', 0)

        self.physical_rig.matchPose(self.animated_rig)
        self.target_physical_rig.matchPose(self.animated_rig)

        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)

        self.physical_rig.clearForces()
        self.target_physical_rig.clearForces()

        self.num_frames = self.animated_rig.getNumFrames('walk')

        self.model = load_model('model.json', 'weights.hdf5')
        self.err_sum = 0.0

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def disableCollisions(self):
        for i in range(32):
            self.world.setGroupCollisionFlag(i, i, False)
        self.world.setGroupCollisionFlag(0, 1, True)
        self.world.setGroupCollisionFlag(0, 2, True)

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
        light.setColor(VBase4(0.2, 0.2, 0.2, 1))

        np = self.render.attachNewNode(light)
        np.setPos(0, -200, 0)
        np.lookAt(0, 0, 0)

        self.render.setLight(np)

        light = AmbientLight('ambient')
        light.setColor(VBase4(0.4, 0.4, 0.4, 1))

        np = self.render.attachNewNode(light)

        self.render.setLight(np)

    def createPlane(self, pos):
        rb = BulletRigidBodyNode('Ground')
        rb.addShape(BulletPlaneShape(Vec3(0, 0, 1), 1))
        rb.setFriction(1.0)
        rb.setAnisotropicFriction(1.0)
        rb.setRestitution(0.0)

        np = self.render.attachNewNode(rb)
        np.setPos(pos)
        np.setCollideMask(BitMask32.bit(0))

        self.world.attachRigidBody(rb)

        return np

    def update(self, task):
        frame_count = globalClock.getFrameCount()

        joint_positions = self.physical_rig.getJointPositions()
        joint_rotations = self.physical_rig.getJointRotations()

        linear_velocities = self.physical_rig.getLinearVelocities()
        angular_velocities = self.physical_rig.getAngularVelocities()

        pause_count = 100
        if frame_count % pause_count == 0:
            self.animated_rig.pose('walk', int(frame_count / pause_count) % self.num_frames)
            self.target_physical_rig.matchPose(self.animated_rig)

        next_joint_positions = self.target_physical_rig.getJointPositions()
        next_joint_rotations = self.target_physical_rig.getJointRotations()

        target_directions = next_joint_positions - joint_positions
        target_rotations = get_angle_vec(next_joint_rotations - joint_rotations)

        joint_positions /= np.fabs(joint_positions).max()
        joint_rotations /= np.fabs(joint_rotations).max()
        linear_velocities /= np.fabs(linear_velocities).max()
        angular_velocities /= np.fabs(angular_velocities).max()
        target_directions /= np.fabs(target_directions).max()
        target_rotations /= np.fabs(target_rotations).max()

        X = np.concatenate([
            joint_positions,
            joint_rotations,
            linear_velocities,
            angular_velocities,
            target_directions,
            target_rotations
        ])

        Y = self.model.predict(np.array([X]))

        self.physical_rig.apply_forces(Y[0])

        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)

        err = self.target_physical_rig.compareTo(self.physical_rig)
        self.err_sum += math.pow(err, 2.0)

        err_rmse = math.sqrt(self.err_sum / frame_count)
        print err_rmse

        return task.cont
