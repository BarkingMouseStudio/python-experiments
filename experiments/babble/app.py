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

from panda3d.bullet import get_bullet_version, BulletBoxShape

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        self.save_path = args['<save_path>']

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

        self.control_rig = ControlJointRig('walking')
        self.control_rig.reparentTo(self.render)
        self.control_rig.setPos(0, 0, -98)
        self.control_rig.createLines(VBase4(1.0, 0.75, 0.5, 1.0))
        self.control_rig.matchPose(self.animated_rig)

        self.disable_collisions()

        self.animated_rig.pose('walk', globalClock.getFrameCount() * 0.5)
        self.physical_rig.matchPose(self.animated_rig)
        self.control_rig.matchPhysicalPose(self.physical_rig)
        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)

        self.frame_count = self.animated_rig.getNumFrames('walk')
        self.babble_count = 10

        self.train_count = self.frame_count * self.babble_count * 300
        self.test_count = self.frame_count * self.babble_count * 10

        print self.train_count, self.test_count

        self.X_train = []
        self.Y_train = []

        self.X_test = []
        self.Y_test = []

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def disable_collisions(self):
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

    def save(self):
        print 'saving...', self.save_path
        data = ((self.X_train, self.Y_train), (self.X_test, self.Y_test))

        f = open(self.save_path, 'wb')
        pickle.dump(data, f)
        f.close()

    def generate(self, count):
        if count % self.babble_count == 0:
            self.animated_rig.pose('walk', int(count / self.babble_count))
            self.physical_rig.matchPose(self.animated_rig)
            self.control_rig.matchPhysicalPose(self.physical_rig)

            self.prev_joint_positions = self.control_rig.getJointPositions()
            self.prev_joint_rotations = self.control_rig.getJointRotations()
        else:
            self.control_rig.matchPhysicalPose(self.physical_rig)

        joint_positions = self.control_rig.getJointPositions()
        joint_rotations = self.control_rig.getJointRotations()

        linear_velocities = self.control_rig.getLinearVelocities(self.prev_joint_positions)
        angular_velocities = self.control_rig.getAngularVelocities(self.prev_joint_rotations)

        Y = self.physical_rig.babble()

        self.world.doPhysics(globalClock.getDt(), 10, 1.0 / 180.0)
        self.control_rig.matchPhysicalPose(self.physical_rig)

        target_directions = self.control_rig.getLinearVelocities(joint_positions)
        target_rotations = self.control_rig.getAngularVelocities(joint_rotations)

        X = np.concatenate([joint_positions, joint_rotations, linear_velocities, angular_velocities, target_directions, target_rotations])

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
