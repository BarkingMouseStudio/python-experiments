from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys
import progressbar

from direct.showbase.ShowBase import ShowBase

from panda3d.core import VBase4, Vec3, PerspectiveLens, TransformState, ClockObject, DirectionalLight, AmbientLight, BitMask32
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode

from ..exposed_joint_rig import ExposedJointRig
from ..control_joint_rig import ControlJointRig
from ..rigid_body_rig import RigidBodyRig

from ..utils.math_utils import get_angle_vec

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        self.save_path = args['<save_path>']

        globalClock.setMode(ClockObject.MNonRealTime)
        globalClock.setDt(0.02) # 20ms per frame

        self.setBackgroundColor(0.9, 0.9, 0.9)
        self.createLighting()

        if not headless:
            self.setupCamera(width, height, Vec3(0, -200, 0), Vec3(0, 0, 0))

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81 * 100.0))
        # self.world.setGravity(Vec3(0, 0, 0))
        self.setupDebug()
        self.createPlane(Vec3(0, 0, -100))

        self.animated_rig = ExposedJointRig('walking', { 'walk': 'walking-animation.egg' })
        self.animated_rig.reparentTo(self.render)
        self.animated_rig.setPos(0, 0, 0)
        # self.animated_rig.createLines(VBase4(0.5, 0.75, 1.0, 1.0))

        self.physical_rig = RigidBodyRig()
        self.physical_rig.reparentTo(self.render)
        self.physical_rig.setPos(0, 0, 0)
        self.physical_rig.createColliders(self.animated_rig)
        self.physical_rig.createConstraints()
        self.physical_rig.setCollideMask(BitMask32.bit(1))
        self.physical_rig.attachRigidBodies(self.world)
        self.physical_rig.attachConstraints(self.world)

        self.disableCollisions()
        # self.setAnimationFrame(0)
        self.physical_rig.matchPose(self.animated_rig)

        self.frame_count = self.animated_rig.getNumFrames('walk')
        self.babble_count = 10

        self.train_count = self.frame_count * self.babble_count * 1000
        self.test_count = self.frame_count * self.babble_count * 100

        widgets = [
            progressbar.SimpleProgress(), ' ',
            progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ',
            progressbar.FileTransferSpeed(format='%(scaled)5.1f/s'), ' ',
            progressbar.ETA(), ' ',
            progressbar.Timer(format='Elapsed: %(elapsed)s'),
        ]
        self.progressbar = progressbar.ProgressBar(widgets=widgets, max_value=self.train_count+self.test_count)
        self.progressbar.start()

        self.X_train = []
        self.Y_train = []

        self.X_test = []
        self.Y_test = []

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

    def save(self):
        data = ((self.X_train, self.Y_train), (self.X_test, self.Y_test))

        f = open(self.save_path, 'wb')
        pickle.dump(data, f)
        f.close()

        self.progressbar.finish()

    def setAnimationFrame(self, frame):
        self.animated_rig.pose('walk', frame)
        self.physical_rig.matchPose(self.animated_rig)

    def generate(self, count):
        if count % self.babble_count == 0:
            # self.setAnimationFrame(int(count / self.babble_count))
            self.physical_rig.matchPose(self.animated_rig)

        joint_positions = self.physical_rig.getJointPositions()
        joint_rotations = self.physical_rig.getJointRotations()

        linear_velocities = self.physical_rig.getLinearVelocities()
        angular_velocities = self.physical_rig.getAngularVelocities()

        Y = self.physical_rig.babble()
        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)

        next_joint_positions = self.physical_rig.getJointPositions()
        next_joint_rotations = self.physical_rig.getJointRotations()

        target_directions = next_joint_positions - joint_positions
        target_rotations = get_angle_vec(next_joint_rotations - joint_rotations)

        X = np.concatenate([
            joint_positions,
            joint_rotations,
            linear_velocities,
            angular_velocities,
            target_directions,
            target_rotations
        ])

        return X, Y

    def update(self, task):
        # if globalClock.getFrameCount() % 100 == 0:
        #     self.setAnimationFrame(globalClock.getFrameCount() / 100)
        # self.physical_rig.babble()
        # self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)
        # return task.cont

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

        self.progressbar.update(curr_train_count + curr_test_count)

        return task.cont
