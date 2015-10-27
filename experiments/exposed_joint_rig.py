from direct.actor.Actor import Actor

from .utils.actor_utils import walk_joints, map_joints, create_lines, filter_joints
from .config import excluded_joints

class ExposedJointRig:

    def __init__(self, model_name, animations):
        self.actor = Actor(model_name, animations)

        exposed_joint_gen = map_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.getName()))
        self.exposed_joints = filter_joints(exposed_joint_gen, excluded_joints)

    def createLines(self, color):
        create_lines(self.exposed_joints, color)

    def getNumFrames(self, animation_name):
        return self.actor.getNumFrames(animation_name)

    def setPlayRate(self, play_rate, animation_name):
        self.actor.setPlayRate(play_rate, animation_name)

    def setPos(self, x, y, z):
        self.actor.setPos(x, y, z)

    def reparentTo(self, other):
        self.actor.reparentTo(other)

    def pose(self, animation_name, frame):
        self.actor.pose(animation_name, frame)
        self.actor.update(force=True)
