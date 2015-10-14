from direct.actor.Actor import Actor

from .utils.actor_utils import walk_joints, create_lines

class ExposedJointRig:

    def __init__(self, model_name, animations, color):
        self.actor = Actor(model_name, animations)

        exposed_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))

        self.exposed_joints = [joint for joint in exposed_joint_gen]
        create_lines(self.exposed_joints, color)

    def reparentTo(self, other):
        self.actor.reparentTo(other)

    def pose(self, animation_name, frame):
        self.actor.pose(animation_name, frame)
        self.actor.update(force=True)
