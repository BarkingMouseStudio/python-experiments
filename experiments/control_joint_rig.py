from direct.actor.Actor import Actor

from panda3d.core import Quat, Vec3

from .utils.actor_utils import walk_joints, create_lines, match_pose, filter_joints
from .config import excluded_joints

class ControlJointRig:
    def __init__(self, model_name):
        self.actor = Actor(model_name)

        exposed_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.getName()))
        control_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.controlJoint(None, 'modelRoot', part.getName()))

        self.exposed_joints = filter_joints(exposed_joint_gen, excluded_joints)
        self.control_joints = filter_joints(control_joint_gen, excluded_joints)

    def createLines(self, color):
        create_lines(self.exposed_joints, color)

    def setRoot(self, name):
        self.root = [node for node, parent in self.control_joints if node.getName() == name][0]

    def setPos(self, x, y, z):
        self.actor.setPos(x, y, z)

    def reparentTo(self, other):
        self.actor.reparentTo(other)

    def matchRoot(self, pose_rig):
        self.root.setPosHpr(pose_rig.root.getPos(self.actor), \
            pose_rig.root.getHpr(self.actor))

    def matchPose(self, pose_rig):
        match_pose(pose_rig.exposed_joints, self.control_joints, True)

    def matchPhysicalPose(self, render, loader, physical_rig):
        match_pose(physical_rig.collider_parents, self.control_joints, True)

    def getJointPositions(self):
        return np.concatenate([node.getPos(parent) if parent is not None else node.getPos() for node, parent in self.exposed_joints])

    def getJointRotations(self):
        return np.concatenate([node.getHpr(parent) if parent is not None else node.getHpr() for node, parent in self.exposed_joints])
