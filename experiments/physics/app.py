# from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.task import Task
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import ShowBase

from panda3d.core import BitMask32, VBase4, Point3, Vec3, Quat, PerspectiveLens, ClockObject, DirectionalLight, AmbientLight
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletBoxShape, BulletRigidBodyNode, BulletDebugNode, BulletHingeConstraint, BulletSphericalConstraint
from pandac.PandaModules import CharacterJoint

from ..utils import create_lens, walk_joints, draw_joints, match_pose, apply_control_joints, filter_joints, load_model, flatten_vectors, rotate_node, measure_error, get_angle_vec

from ..config import joints_config

excluded_joints = ['LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandMiddle1', 'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandRing1', 'LeftHandRing2', 'LeftHandRing3', 'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3', 'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3', 'RightHandPinky1', 'RightHandPinky2', 'RightHandPinky3', 'RightHandRing1', 'RightHandRing2', 'RightHandRing3', 'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3']

def setup_debug(render, world):
    node = BulletDebugNode('Debug')
    node.showWireframe(True)
    np = render.attachNewNode(node)
    np.show()
    world.setDebugNode(node)

def get_mass(depth, min_mass, max_mass):
    depth_multiplier = 1.0
    depth_factor = 3.0
    if depth > 0:
        return min(max_mass * (depth_factor / (depth * depth_multiplier)) + min_mass, max_mass)
    else:
        return max_mass

class App(ShowBase):

    def __init__(self, width, height):
        ShowBase.__init__(self)

        self.setBackgroundColor(0.9, 0.9, 0.9)

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        light = DirectionalLight('light')
        light.set_color(VBase4(0.2, 0.2, 0.2, 1))
        light_np = self.render.attach_new_node(light)
        light_np.set_pos(0, -200, 0)
        light_np.look_at(0, 0, 0)
        self.render.set_light(light_np)

        light = AmbientLight('ambient')
        light.set_color(VBase4(0.4, 0.4, 0.4, 1))
        light_np = self.render.attachNewNode(light)
        self.render.setLight(light_np)

        self.cam.set_pos(0, -200, 0)
        self.cam.look_at(0, 0, 0)
        self.cam.node().set_lens(create_lens(width / height))

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81 * 10))

        setup_debug(self.render, self.world)

        self.floor = self.create_plane(Vec3(0, 0, -100), Vec3(1, 1, 1))

        self.rig = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.rig.reparentTo(self.render)
        self.rig.setBin('background', 1)

        # self.joints = []
        # walk_joints(self.rig, self.rig.getPartBundle('modelRoot'), self.joints, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        # self.joints = [(node, parent) for node, parent in self.joints if node.get_name() not in excluded_joints]
        # draw_joints(self.joints, (0.5, 0.75, 1.0))

        self.physical_rig = self.render.attachNewNode('physical_rig')
        self.walk_joints(self.rig, self.rig.getPartBundle('modelRoot'), [])
        self.constrain_joints(self.physical_rig, self.world)
        self.disable_collisions(self.physical_rig, self.floor, self.world)

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def constrain_joints(self, root, world):
        for joint_config, rb_parent, rb_child in self.get_joint_pairs(root):
            extents_parent = rb_parent.get_shape(0).getHalfExtentsWithMargin()
            extents_child = rb_child.get_shape(0).getHalfExtentsWithMargin()

            offset_parent = (0, 1, 0)
            if 'offset_parent' in joint_config:
                offset_parent = joint_config['offset_parent']
            offset_parent_x, offset_parent_y, offset_parent_z = offset_parent
            offset_parent = Point3(offset_parent_x * extents_parent.getX(), \
                                   offset_parent_y * extents_parent.getY(), \
                                   offset_parent_z * extents_parent.getZ())

            offset_child = (0, -1, 0)
            if 'offset_child' in joint_config:
                offset_child = joint_config['offset_child']
            offset_child_x, offset_child_y, offset_child_z = offset_child
            offset_child = Point3(offset_child_x * extents_child.getX(), \
                                  offset_child_y * extents_child.getY(), \
                                  offset_child_z * extents_child.getZ())

            cs = BulletSphericalConstraint(rb_parent, rb_child, offset_parent, offset_child)
            cs.setDebugDrawSize(3.0)
            world.attachConstraint(cs, linked_collision=True)

    def disable_collisions(self, root, floor, world):
        for i in range(32):
            world.setGroupCollisionFlag(i, i, False)

        proxy_group = BitMask32.bit(0)
        floor_group = BitMask32.bit(1)

        world.setGroupCollisionFlag(0, 1, True)

        for child in root.getChildren():
            child.setCollideMask(proxy_group)

        floor.setCollideMask(floor_group)

    def get_joint_pairs(self, root):
        for key_parent in joints_config:
            joint_config_parent = joints_config[key_parent]
            parent = root.find(key_parent)
            rb_parent = parent.node()

            if 'joints' in joint_config_parent:
                for key_child in joint_config_parent['joints']:
                    joint_config_child = joint_config_parent['joints'][key_child]
                    other = root.find(key_child)
                    rb_child = other.node()
                    yield (joint_config_child, rb_parent, rb_child)

    def walk_joints(self, actor, part, parents):
        parents = list(parents)

        if isinstance(part, CharacterJoint) and part.get_name() not in excluded_joints:
            node = actor.exposeJoint(None, 'modelRoot', part.get_name())

            parents_len = len(parents)
            if parents_len > 0:
                parent = parents[-1]

                mass = get_mass(parents_len, 1.0, 5.0)
                node_name = node.get_name()

                joint_config = joints_config[node_name] if node_name in joints_config else None
                joint_pos = node.get_pos(parent)
                joint_midpoint = joint_pos / 2.0
                joint_length = joint_pos.length()
                joint_width = joint_length / 2.0 if joint_length > 0 else mass

                if joint_config is not None and 'scale' in joint_config:
                    sx, sy, sz = joint_config['scale']
                    scale = Vec3(sx, sy if sy != -1 else joint_width, sz)
                else:
                    scale = Vec3(mass, joint_width, mass)

                box_scale = Vec3(1, joint_width, 1)
                box_scale = scale

                box_rb = BulletRigidBodyNode(node_name)
                box_rb.setMass(mass)
                box_rb.addShape(BulletBoxShape(box_scale))
                box_rb.setLinearDamping(0.2)
                box_rb.setAngularDamping(0.9)
                box_rb.setFriction(0.2)

                self.world.attachRigidBody(box_rb)

                # align rigidbody with relative position node
                np = parent.attachNewNode(box_rb)
                np.setPos(joint_midpoint)
                np.lookAt(node)

                # reparent to root
                box_np = self.physical_rig.attachNewNode(box_rb)
                np.removeNode() # cleanup relative position node

                # load model
                # model = self.loader.loadModel('cube.egg')
                # model.reparentTo(box_np)
                # model.flattenLight()
                # model.setScale(Vec3(scale))

            parents.append(node)

        for child in part.get_children():
            self.walk_joints(actor, child, parents)

    def create_plane(self, pos, scale):
        rb = BulletRigidBodyNode('Ground')
        rb.addShape(BulletPlaneShape(Vec3(0, 0, 1), 1))
        rb.setFriction(1.0)

        np = self.render.attachNewNode(rb)
        np.setPos(pos)
        np.setScale(scale)

        self.world.attachRigidBody(rb)

        return np

    def update(self, task):
        for child in self.physical_rig.getChildren():
            T_local = Vec3(0, 0, random.random() * 10000.0)
            T_world = child.getQuat(self.render).xform(T_local)
            child.node().applyTorque(T_world)

        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 1.0 / 60.0)

        return task.cont
