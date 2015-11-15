import numpy as np

from direct.actor.Actor import Actor

from panda3d.core import NodePath, Vec3, RigidBodyCombiner
from pandac.PandaModules import CharacterJoint

from .utils.actor_utils import walk_joints, map_joints, create_lines, filter_joints
from .config import excluded_joints

class ExposedJointRig:

    def __init__(self, model_name, animations):
        self.actor = Actor(model_name, animations)
        # self.actor.update(force=True)

        exposed_joint_gen = self.mapJoints(self.actor.getPartBundle('modelRoot'))

        self.exposed_joints = list(exposed_joint_gen)
        # self.exposed_joints = filter_joints(exposed_joint_gen, excluded_joints)

    def mapJoints(self, part, prev=None):
        if isinstance(part, CharacterJoint):
            # curr = self.actor.exposeJoint(None, 'modelRoot', part.getName())
            if prev is not None:
                curr = self.actor.exposeJoint(None, 'modelRoot', part.getName())
            else:
                curr = self.actor.controlJoint(None, 'modelRoot', part.getName())

            yield curr, prev
            prev = curr

        for part_child in part.getChildren():
            for next_curr, next_prev in self.mapJoints(part_child, prev):
                yield next_curr, next_prev

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

    def play(self, animation_name):
        self.actor.play(animation_name)

    def loop(self, animation_name):
        self.actor.loop(animation_name)
