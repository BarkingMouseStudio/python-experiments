import math
import random
import numpy as np

from panda3d.core import Quat, NodePath, Vec3

def get_angle(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle

class Arm:

    def __init__(self, parent):
        self.arm_pivot = NodePath("arm_pivot")
        self.arm_pivot.reparent_to(parent)
        self.arm_pivot.set_pos(0, 0, 0)

        self.shoulder_pivot = NodePath("shoulder_pivot")
        self.shoulder_pivot.reparent_to(self.arm_pivot)
        self.shoulder_pivot.set_pos(0, 0, 0)

        self.elbow_pivot = NodePath("elbow_pivot")
        self.elbow_pivot.reparent_to(self.shoulder_pivot)
        self.elbow_pivot.set_pos(0, 0, 5)

        self.end_effector = NodePath("end_effector")
        self.end_effector.reparent_to(self.elbow_pivot)
        self.end_effector.set_pos(0, 0, 5)

        model_upper = loader.loadModel("box_segment.egg")
        model_lower = loader.loadModel("box_segment.egg")
        model_effector = loader.loadModel("icosphere.egg")

        model_shoulder = loader.loadModel("icosphere.egg")
        model_shoulder.reparent_to(self.shoulder_pivot)
        model_shoulder.set_scale(0.75, 0.75, 0.75)

        model_elbow = loader.loadModel("icosphere.egg")
        model_elbow.reparent_to(self.elbow_pivot)
        model_elbow.set_scale(0.75, 0.75, 0.75)

        model_upper.reparent_to(self.shoulder_pivot)
        model_upper.set_pos(0.0, 0.0, 2.5)

        model_lower.reparent_to(self.elbow_pivot)
        model_lower.set_pos(0.0, 0.0, 2.5)

        model_effector.reparent_to(self.end_effector)
        model_effector.set_scale(0.75, 0.75, 0.75)

    def rotate_shoulder(self, dh, dp, dr):
        dq = Quat()
        dq.set_hpr(Vec3(dh, dp, dr))

        q = self.shoulder_pivot.get_quat()
        self.shoulder_pivot.set_quat(q * dq)

    def rotate_elbow(self, dh, dp, dr):
        dq = Quat()
        dq.set_hpr(Vec3(dh, dp, dr))

        q = self.elbow_pivot.get_quat()
        self.elbow_pivot.set_quat(q * dq)
