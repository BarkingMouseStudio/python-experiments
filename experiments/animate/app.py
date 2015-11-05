from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from panda3d.core import VBase4, Vec3, Quat, PerspectiveLens, ClockObject, DirectionalLight
from pandac.PandaModules import CharacterJoint, LineSegs

from ..utils.actor_utils import map_joints, create_lines

class App(ShowBase):

    def __init__(self, width, height, model_path, animation_path):
        ShowBase.__init__(self)

        globalClock.setMode(ClockObject.MNonRealTime)
        globalClock.setDt(0.02) # 20ms per frame

        self.cam.setPos(0, -200, 100)
        self.cam.lookAt(0, 0, 100)
        self.cam.node().setLens(self.createLens(width / height))

        if animation_path:
            self.actor = Actor(model_path, { 'animation': animation_path })
            self.actor.pose('animation', 0)
        else:
            self.actor = Actor(model_path)

        self.actor.reparentTo(self.render)

        exposed_joint_gen = map_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.getName()))
        exposed_joints = list(exposed_joint_gen)

        create_lines(exposed_joints, VBase4(0.5, 0.75, 1.0, 1.0))

        self.accept('escape', sys.exit)

    def createLens(self, aspect_ratio, fov=60.0, near=1.0, far=1000.0):
        lens = PerspectiveLens()
        lens.setFov(fov)
        lens.setAspectRatio(aspect_ratio)
        lens.setNearFar(near, far)
        return lens
