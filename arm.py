from panda3d.core import NodePath

class Arm:

    def __init__(self):
        self.arm_pivot = NodePath("arm_pivot")
        self.arm_pivot.set_pos(0, 0, 0)

        self.shoulder_pivot = NodePath("shoulder_pivot")
        self.shoulder_pivot.reparent_to(self.arm_pivot)
        self.shoulder_pivot.set_pos(0, 0, 0)
        self.shoulder_pivot.set_hpr(0, 0, -45)

        self.elbow_pivot = NodePath("elbow_pivot")
        self.elbow_pivot.reparent_to(self.shoulder_pivot)
        self.elbow_pivot.set_pos(0, 0, 5)
        self.elbow_pivot.set_hpr(0, 0, -280)

        self.end_effector = NodePath("end_effector")
        self.end_effector.reparent_to(self.elbow_pivot)
        self.end_effector.set_pos(0, 0, 5)

        model_upper = loader.loadModel("box_segment.egg")
        model_lower = loader.loadModel("box_segment.egg")
        model_effector = loader.loadModel("icosphere.egg")

        model_upper.reparent_to(self.shoulder_pivot)
        model_upper.set_pos(0, 0, 2.5)

        model_lower.reparent_to(self.elbow_pivot)
        model_lower.set_pos(0, 0, 2.5)

        model_effector.reparent_to(self.end_effector)
        model_effector.setScale(0.5, 0.5, 0.5)

    def rotate_elbow(self, dr):
        self.elbow_pivot.set_r(self.elbow_pivot.get_r() + dr)

    def rotate_shoulder(self, dr):
        self.shoulder_pivot.set_r(self.shoulder_pivot.get_r() + dr)
