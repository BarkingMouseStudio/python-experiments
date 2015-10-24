import random
import numpy as np

from panda3d.core import NodePath, Vec3
from pandac.PandaModules import CharacterJoint

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletSphericalConstraint, BulletHingeConstraint, BulletConeTwistConstraint
from pandac.PandaModules import CharacterJoint

from .utils.physics_utils import create_constraints, create_colliders, get_joint_pairs
from .utils.actor_utils import match_pose
from .utils.math_utils import get_angle_vec
from .config import joints_config, excluded_joints

class RigidBodyRig:

    def __init__(self, pose_rig):
        self.root = NodePath('root')

        self.colliders = list(create_colliders(self.root, pose_rig.exposed_joints, joints_config))
        # self.constraints = list(create_constraints(self.root, get_joint_pairs(self.root, joints_config)))
        self.collider_parents = list(self.parentColliders(pose_rig.exposed_joints))

    def parentColliders(self, exposed_joints):
        for node, parent in exposed_joints:
            node_collider = self.root.find(node.getName())
            if parent is not None:
                parent_collider = self.root.find(parent.getName())
                yield node_collider, parent_collider
            else:
                yield node_collider, None

    def attachCubes(self, loader):
        for collider in self.colliders:
            scale = collider.node().getShape(0).getHalfExtentsWithMargin()
            model = loader.loadModel('cube.egg')
            model.reparentTo(collider)
            model.setScale(scale)

    def babble(self):
        # TODO: restrict torque as a function of mass
        torques = [np.random.uniform(-5000.0, 5000.0, size=3) for collider in self.colliders]
        for collider, T_raw in zip(self.colliders, torques):
            T_local = Vec3(*T_raw)
            T_world = collider.getQuat(self.root).xform(T_local)
            collider.node().applyTorque(T_world)
        return np.concatenate(torques)

    def matchPose(self, pose_rig):
        for node_parent_pair, collider_parent_pair in zip(pose_rig.exposed_joints, self.collider_parents):
            node, node_parent = node_parent_pair
            collider, collider_parent = collider_parent_pair

            if node_parent is not None:
                midpoint = node.getPos(node_parent) / 2.0
                endpoint = node.getPos(node_parent)

                collider.setPos(node_parent, midpoint)
                collider.lookAt(node_parent, endpoint)
            else:
                collider.setPosHpr(node.getPos(), node.getHpr())

    def reparentTo(self, other):
        self.root.reparentTo(other)

    def setCollideMask(self, mask):
        for child in self.root.getChildren():
            child.setCollideMask(mask)

    def attachRigidBodies(self, world):
        for collider in self.colliders:
            world.attachRigidBody(collider.node())

    def attachConstraints(self, world):
        # for constraint in self.constraints:
        #     world.attachConstraint(constraint, linked_collision=True)
        pass
