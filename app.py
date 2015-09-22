from __future__ import division

from arm import Arm
from direct.showbase.ShowBase import ShowBase

from panda3d import bullet
from panda3d.core import Vec3, Point3, PerspectiveLens, WindowProperties

def create_lens(aspect_ratio):
    lens = PerspectiveLens()
    lens.setFov(60)
    lens.setAspectRatio(aspect_ratio)
    return lens

class App(ShowBase):

    def __init__(self, width, height):
        ShowBase.__init__(self)

        self.toggleWireframe()

        self.cam.setPos(0, -20, 0)
        self.cam.lookAt(0, 0, 0)
        self.cam.node().setLens(create_lens(width / height))

        self.arm = Arm()
        self.arm.arm_pivot.reparentTo(self.render)

        self.taskMgr.add(self.update, 'update')

    def update(self, task):
        dt = globalClock.getDt()
        self.arm.rotate_elbow(-5.0 * dt)
        self.arm.rotate_shoulder(5.0 * dt)
        return task.cont
