from direct.actor.Actor import Actor

from panda3d.core import Quat, Vec3

from .utils.actor_utils import map_joints, create_lines, match_pose, filter_joints
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

    def getJointPositions(self):
        return np.concatenate([node.getPos(parent) if parent is not None else node.getPos() for node, parent in self.exposed_joints])

    def getJointRotations(self):
        return np.concatenate([node.getHpr(parent) if parent is not None else node.getHpr() for node, parent in self.exposed_joints])
