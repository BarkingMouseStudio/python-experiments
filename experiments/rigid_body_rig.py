import math
import random
import numpy as np

from panda3d.core import NodePath, Vec3, RigidBodyCombiner
from pandac.PandaModules import CharacterJoint

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletSphericalConstraint, BulletHingeConstraint, BulletConeTwistConstraint
from pandac.PandaModules import CharacterJoint

from .utils.physics_utils import create_constraints, create_colliders, get_joint_pairs
from .utils.actor_utils import match_pose, walk_joints
from .utils.math_utils import get_angle_vec, random_spherical
from .config import joints_config, excluded_joints

class RigidBodyRig:

    def __init__(self):
        self.root = NodePath('root')

    def createColliders(self, pose_rig):
        self.colliders = list(create_colliders(self.root, pose_rig, joints_config))

    def createConstraints(self):
        self.constraints = list(create_constraints(self.root, get_joint_pairs(self.root, joints_config)))

    def setPos(self, *pos):
        self.root.setPos(*pos)

    def babble(self):
        F_all = [random.uniform(-100.0, 100.0) for collider in self.colliders]
        r_all = [random_spherical() for collider in self.colliders]

        # r_world_all = []
        for collider, F, r in zip(self.colliders, F_all, r_all):
            r = Vec3(1, 0, 0)
            r_world = collider.getQuat(self.root).xform(r) # TODO: is root necessary?
            # r_world_all.append(r_world)

            collider.node().applyTorqueImpulse(r_world * F)

        # return np.concatenate([np.array(F_all), np.concatenate(r_world_all)])
        return np.array(F_all)

    def matchPose(self, pose_rig):
        for node, parent in pose_rig.exposed_joints:
            if node.getName() not in joints_config:
                continue

            joint_config = joints_config[node.getName()]
            if 'joints' not in joint_config:
                continue

            joints = joint_config['joints']
            if len(joints) == 0:
                continue

            box_np = self.root.find(node.getName())

            if len(joints) > 1:
                pos = node.getPos(pose_rig.actor)
                hpr = node.getHpr(pose_rig.actor)
                box_np.setPosHpr(self.root, pos, hpr)
            else:
                joint = joints.keys()[0]
                child_node, child_parent = next((child_node, child_parent) for child_node, child_parent in pose_rig.exposed_joints if child_node.getName() == joint)
                box_np.setPos(child_parent, child_node.getPos(child_parent) / 2.0)
                box_np.lookAt(child_parent, child_node.getPos(child_parent))

            box_np.node().setLinearVelocity(Vec3.zero())
            box_np.node().setAngularVelocity(Vec3.zero())

    def setPos(self, *pos):
        self.root.setPos(*pos)

    def reparentTo(self, other):
        self.root.reparentTo(other)

    def setCollideMask(self, mask):
        for child in self.root.getChildren():
            child.setCollideMask(mask)

    def attachRigidBodies(self, world):
        for collider in self.colliders:
            world.attachRigidBody(collider.node())

    def attachConstraints(self, world):
        for constraint in self.constraints:
            world.attachConstraint(constraint, linked_collision=True)

    def getJointPositions(self):
        return np.concatenate([collider.getPos(self.root) for collider in self.colliders]) # TODO: is root necessary?

    def getJointRotations(self):
        return np.concatenate([collider.getHpr(self.root) for collider in self.colliders]) # TODO: is root necessary?

    def getLinearVelocities(self):
        return np.concatenate([collider.node().getLinearVelocity() for collider in self.colliders])

    def getAngularVelocities(self):
        return np.concatenate([collider.node().getAngularVelocity() for collider in self.colliders])
