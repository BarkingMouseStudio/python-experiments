import math
import random
import numpy as np

from panda3d.core import NodePath, Vec3, RigidBodyCombiner, lookAt, Quat, TransformState
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

    def createConstraints(self, offset_scale):
        self.constraints = list(create_constraints(self.root, get_joint_pairs(self.root, joints_config), offset_scale))

    def clearMasses(self):
        [collider.node().setMass(0) for collider in self.colliders]

    def attachCubes(self, loader):
        for collider in self.colliders:
            for i in range(collider.node().getNumShapes()):
                shape = collider.node().getShape(i)
                mat = collider.node().getShapeMat(i)
                scale = shape.getHalfExtentsWithMargin()

                transform = TransformState.makeMat(mat)

                cube = loader.loadModel("cube.egg")
                cube.setTransform(transform)
                cube.setScale(scale)
                cube.reparentTo(collider)

    def setScale(self, *scale):
        self.root.setScale(*scale)

    def setPos(self, *pos):
        self.root.setPos(*pos)

    def babble(self):
        F_all = []

        for collider in self.colliders:
            collider_name = collider.getName()
            if collider_name == "Hips":
                continue

            F = random.uniform(-1.0, 1.0) * joints_config[collider_name].get("F_max", 4000.0)
            F_all.append(F)

            r = Vec3(*joints_config[collider_name].get("axis", (1, 0, 0)))
            r_world = collider.getQuat(self.root).xform(r)
            T = r_world * F

            collider.node().applyTorqueImpulse(T)

        return np.array(F_all)

    def apply_forces(self, F_all):
        i = 0
        for collider in self.colliders:
            if collider.getName() == "Hips":
                continue

            F = F_all[i]

            r = Vec3(1, 0, 0)
            r_world = collider.getQuat(self.root).xform(r)
            T = r_world * F

            collider.node().applyTorqueImpulse(T)
            i += 1

    def compareTo(self, target):
        positions = self.getJointPositions()
        rotations = self.getJointRotations()

        target_positions = target.getJointPositions()
        target_rotations = target.getJointRotations()

        err_pos = np.abs((positions - target_positions) / 200.0).sum()
        err_hpr = np.abs((rotations - target_rotations) / 180.0).sum()

        return err_pos + err_hpr

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

                quat = Quat()
                lookAt(quat, child_node.getPos(child_parent), Vec3.up())
                box_np.setQuat(child_parent, quat)

            box_np.node().clearForces()

    def clearForces(self):
        for collider in self.colliders:
            collider.node().clearForces()

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
        return get_angle_vec(np.concatenate([collider.node().getAngularVelocity() for collider in self.colliders]))
