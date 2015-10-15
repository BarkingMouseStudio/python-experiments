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

from ..utils import create_lens, walk_joints, draw_joints

class App(ShowBase):

    def __init__(self, width, height):
        ShowBase.__init__(self)

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        self.cam.set_pos(0, -200, 0)
        self.cam.look_at(0, 0, 0)
        self.cam.node().set_lens(create_lens(width / height))

        self.actor = Actor('walking.egg', { 'walk': 'walking-animation.egg' })
        self.actor.reparentTo(self.render)

        self.animated_joint_list = []
        walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), self.animated_joint_list, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        draw_joints(self.animated_joint_list, (0.5, 0.75, 1.0))

        self.actor.loop('walk')

        self.accept('escape', sys.exit)
