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
        self.constraints = list(create_constraints(self.root, get_joint_pairs(self.root, joints_config)))
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
        for pose_joint_pair, control_joint_pair in zip(pose_joints, control_joints):
            pose_joint, pose_joint_parent = pose_joint_pair
            control_joint, control_joint_parent = control_joint_pair

            if pose_joint_parent is None:
                # get target pose position and orientation in local space
                pose_pos = pose_joint.getPos()
                pose_hpr = pose_joint.getHpr()

                # apply to control joint
                control_joint.setPosHpr(pose_pos, pose_hpr)
                continue

            if is_relative:
                # get target pose position and orientation in local space
                pose_pos = pose_joint.getPos(pose_joint_parent)
                pose_hpr = pose_joint.getHpr(pose_joint_parent)
            else:
                pose_pos = pose_joint.getPos()
                pose_hpr = pose_joint.getHpr()

            # apply to control joint
            control_joint.setPosHpr(pose_pos, pose_hpr)
            match_pose(pose_rig.exposed_joints, self.collider_parents)

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
