from __future__ import division

import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d import bullet
from panda3d.core import Point2, PerspectiveLens, ClockObject, DirectionalLight

from arm import Arm
from actuator import Actuator

def create_lens(aspect_ratio):
    lens = PerspectiveLens()
    lens.setFov(60)
    lens.setAspectRatio(aspect_ratio)
    return lens

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        width = args['--width']
        height = args['--height']

        save_interval = args['--save-interval']
        save_path = args['--save']
        load_path = args['--load']

        print save_interval, save_path, load_path

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        # self.toggleWireframe()
        self.disableMouse() # just disables camera movement with mouse

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        self.cam.set_pos(0, -20, 0)
        self.cam.look_at(0, 0, 0)
        self.cam.node().set_lens(create_lens(width / height))

        self.actuator = Actuator()

        self.arm = Arm(self.actuator)
        self.arm.arm_pivot.reparent_to(self.render)

        self.accept('escape', sys.exit)
        self.accept('x', self.arm.toggle_training)

        self.taskMgr.add(self.update, 'update')

        if save_path is not None:
            self.taskMgr.doMethodLater(save_interval, self.save, 'save', extraArgs=[save_path])

        if load_path is not None:
            self.load(load_path)

        # print self.render.ls() # print tree

    def save(self, save_path):
        self.actuator.save_weights(save_path)
        return Task.again

    def load(self, load_path):
        self.actuator.load_weights(load_path)

    def get_mouse_pos(self):
        if self.mouseWatcherNode.hasMouse():
            return self.mouseWatcherNode.getMouse()
        else:
            return Point2()

    def update(self, task):
        self.arm.tick(globalClock.get_dt(), self.get_mouse_pos())
        return task.cont
