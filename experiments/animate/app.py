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
from ..exposed_joint_rig import ExposedJointRig

class App(ShowBase):

    def __init__(self, width, height, model_path, animation_path):
        ShowBase.__init__(self)

        globalClock.setMode(ClockObject.MNonRealTime)
        globalClock.setDt(0.02) # 20ms per frame

        self.cam.setPos(0, -300, 100)
        self.cam.lookAt(0, 0, 100)
        self.cam.node().setLens(self.createLens(width / height))

        if animation_path:
            self.animation = ExposedJointRig(model_path, { 'animation': animation_path })
            self.animation.play('animation')
        else:
            self.animation = ExposedJointRig(model_path, {})
        self.animation.createLines(VBase4(1.0, 0.75, 0.5, 1.0))
        self.animation.reparentTo(self.render)

        self.canonical = ExposedJointRig(model_path, { 'animation': 'models/walking-animation.egg' })
        self.canonical.play('animation')
        self.canonical.reparentTo(self.render)
        self.canonical.createLines(VBase4(0.5, 0.75, 1.0, 1.0))

        self.num_frames = self.canonical.getNumFrames('animation')
        self.setAnimationFrame(0)

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def createLens(self, aspect_ratio, fov=60.0, near=1.0, far=1000.0):
        lens = PerspectiveLens()
        lens.setFov(fov)
        lens.setAspectRatio(aspect_ratio)
        lens.setNearFar(near, far)
        return lens

    def setAnimationFrame(self, frame):
        self.animation.pose('animation', frame)
        self.canonical.pose('animation', frame)

    def update(self, task):
        frame_count = globalClock.getFrameCount()
        self.setAnimationFrame(frame_count % self.num_frames)
        return task.cont
