from __future__ import division

import sys

from arm import Arm
from direct.showbase.ShowBase import ShowBase

from panda3d import bullet
from panda3d.core import Vec3, Point3, PerspectiveLens, WindowProperties, ClockObject

def create_lens(aspect_ratio):
    lens = PerspectiveLens()
    lens.setFov(60)
    lens.setAspectRatio(aspect_ratio)
    return lens

class App(ShowBase):

    def __init__(self, width, height):
        ShowBase.__init__(self)

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        self.toggleWireframe()

        self.cam.set_pos(0, -20, 0)
        self.cam.look_at(0, 0, 0)
        self.cam.node().set_lens(create_lens(width / height))

        self.arm = Arm()
        self.arm.arm_pivot.reparent_to(self.render)

        self.accept('escape', sys.exit)
        self.accept('x', self.arm.toggle_training)

        self.taskMgr.add(self.update, 'update')

    def update(self, task):
        self.arm.tick(globalClock.get_dt())
        return task.cont
