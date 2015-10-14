from direct.actor.Actor import Actor

from .utils.actor_utils import walk_joints, create_lines

class ControlJointRig:

    def __init__(self, model_name, color):
        self.actor = Actor(model_name)

        exposed_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        control_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.controlJoint(None, 'modelRoot', part.get_name()))

        self.exposed_joints = [joint for joint in exposed_joint_gen]
        self.control_joints = [joint for joint in control_joint_gen]

        create_lines(self.exposed_joints, color)

    def reparentTo(self, other):
        self.actor.reparentTo(other)
