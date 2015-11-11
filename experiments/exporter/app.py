from __future__ import print_function
from __future__ import division

import sys

from direct.showbase.ShowBase import ShowBase

from panda3d.core import VBase4, PerspectiveLens, ClockObject

from ..exposed_joint_rig import ExposedJointRig
from ..control_joint_rig import ControlJointRig
from .fbx_manager import FBXManager

class App(ShowBase):

    def __init__(self, width, height, model_path, animation_path):
        ShowBase.__init__(self)

        globalClock.setMode(ClockObject.MNonRealTime)
        globalClock.setDt(0.02) # 20ms per frame

        self.cam.setPos(0, -200, 100)
        self.cam.lookAt(0, 0, 100)
        self.cam.node().setLens(self.createLens(width / height))

        self.animated_rig = ExposedJointRig(model_path, { 'animation': animation_path })
        self.animated_rig.reparentTo(self.render)
        self.animated_rig.createLines(VBase4(0.5, 0.75, 1.0, 1.0))

        self.control_rig = ControlJointRig(model_path)
        self.control_rig.reparentTo(self.render)
        self.control_rig.createLines(VBase4(1.0, 0.75, 0.5, 1.0))

        self.fbx_manager = FBXManager()
        self.fbx_manager.setupJoints(self.control_rig.control_joints)

        self.num_frames = self.animated_rig.getNumFrames('animation')
        self.setAnimationFrame(0)

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def setAnimationFrame(self, frame_count):
        self.animated_rig.pose('animation', frame_count)
        self.control_rig.matchPose(self.animated_rig)
        self.fbx_manager.setKeyframe(frame_count, self.control_rig.control_joints)

    def createLens(self, aspect_ratio, fov=60.0, near=1.0, far=1000.0):
        lens = PerspectiveLens()
        lens.setFov(fov)
        lens.setAspectRatio(aspect_ratio)
        lens.setNearFar(near, far)
        return lens

    def update(self, task):
        frame_count = globalClock.getFrameCount()

        if frame_count > self.num_frames:
            self.fbx_manager.save("animation-test.fbx")
            sys.exit()
            return task.done

        self.setAnimationFrame(frame_count)

        print('progress: %f%%' % ((frame_count / self.num_frames) * 100.0))
        return task.cont
