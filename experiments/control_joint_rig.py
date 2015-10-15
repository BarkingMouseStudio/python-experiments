from direct.actor.Actor import Actor

from .utils.actor_utils import walk_joints, create_lines, match_pose, filter_joints
from .config import excluded_joints

class ControlJointRig:

    def __init__(self, model_name, color):
        self.actor = Actor(model_name)

        exposed_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.getName()))
        control_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.controlJoint(None, 'modelRoot', part.getName()))

        self.exposed_joints = filter_joints(exposed_joint_gen, excluded_joints)
        self.control_joints = filter_joints(control_joint_gen, excluded_joints)

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
