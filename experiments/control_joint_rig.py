import numpy as np

from direct.actor.Actor import Actor

from panda3d.core import Quat, Vec3

from .utils.actor_utils import map_joints, create_lines, match_pose, filter_joints, apply_control_joints
from .utils.math_utils import get_angle_vec
from .config import excluded_joints

class ControlJointRig:
    def __init__(self, model_name):
        self.actor = Actor(model_name)

        exposed_joint_gen = map_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.getName()))
        control_joint_gen = map_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.controlJoint(None, 'modelRoot', part.getName()))

        self.exposed_joints = filter_joints(exposed_joint_gen, excluded_joints)
        self.control_joints = filter_joints(control_joint_gen, excluded_joints)

    def createLines(self, color):
        create_lines(self.exposed_joints, color)

    def setPos(self, *pos):
        self.actor.setPos(*pos)

    def reparentTo(self, other):
        self.actor.reparentTo(other)

    def matchPose(self, pose_rig):
        match_pose(pose_rig.exposed_joints, self.control_joints, True)
        apply_control_joints(self.control_joints, self.exposed_joints)

    def matchPhysicalPose(self, physical_rig):
        for node, parent in self.control_joints:
            collider = physical_rig.root.find(node.getName())

            if not collider:
                continue

            if parent is not None:
                collider_parent = physical_rig.root.find(parent.getName())
                node.setHpr(collider.getHpr(collider_parent))
            else:
                node.setPosHpr(collider.getPos(), collider.getHpr())
        apply_control_joints(self.control_joints, self.exposed_joints)

    def babble(self):
        rotations = [Vec3(*np.random.uniform(-5.0, 5.0, size=3)) for node, parent in self.control_joints]
        for node_parent, rotation in zip(self.control_joints, rotations):
            node, parent = node_parent

            # dq = Quat()
            # dq.setHpr(rotation)

            # q = node.getQuat()
            # node.setQuat(q * dq)

            hpr = node.getHpr()
            node.setHpr(hpr + rotation)

        apply_control_joints(self.control_joints, self.exposed_joints)
        return np.concatenate(rotations)

    def getJointPositions(self):
        return np.concatenate([node.getPos(parent) if parent is not None else node.getPos() for node, parent in self.exposed_joints])

    def getJointRotations(self):
        return np.concatenate([node.getHpr(parent) if parent is not None else node.getHpr() for node, parent in self.exposed_joints])

    def getLinearVelocities(self, joint_positions, prev_joint_positions):
        return joint_positions - prev_joint_positions

    def getAngularVelocities(self, joint_rotations, prev_joint_rotations):
        return get_angle_vec(joint_rotations - prev_joint_rotations)

    def getTargetDirections(self, next_joint_positions, joint_positions):
        return next_joint_positions - joint_positions

    def getTargetRotations(self, next_joint_rotations, joint_rotations):
        return get_angle_vec(next_joint_rotations - joint_rotations)
