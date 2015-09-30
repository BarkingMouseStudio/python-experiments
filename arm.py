import math
import random
import numpy as np

from panda3d.core import NodePath, Vec3

def get_target_direction(direction):
    direction = Vec3(direction)
    direction.normalize()
    return math.degrees(math.atan2(direction.z, direction.x))

def get_angle(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle

ASCII_BACKGROUND = "\033[7m]"
ASCII_END = '\033[0m'

class Arm:

    def __init__(self, actuator):
        self.actuator = actuator

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

        self.target = NodePath("target")
        self.target.reparent_to(self.arm_pivot)
        self.target.set_pos(0, 0, 10)

        self.direction = NodePath("direction")
        self.direction.reparent_to(self.end_effector)
        self.direction.set_pos(0, 0, 0)

        model_upper = loader.loadModel("box_segment.egg")
        model_lower = loader.loadModel("box_segment.egg")
        model_effector = loader.loadModel("icosphere.egg")
        model_target = loader.loadModel("icosphere.egg")
        model_arrow = loader.loadModel("arrow.egg")

        model_arrow.reparent_to(self.direction)
        model_arrow.set_pos(0.0, 1.5, 0.0)

        model_target.reparent_to(self.target)
        model_target.set_scale(0.5, 0.5, 0.5)

        model_upper.reparent_to(self.shoulder_pivot)
        model_upper.set_pos(0.0, 0.0, 2.5)

        model_lower.reparent_to(self.elbow_pivot)
        model_lower.set_pos(0.0, 0.0, 2.5)

        model_effector.reparent_to(self.end_effector)
        model_effector.set_scale(0.5, 0.5, 0.5)

        self.home_position = [0, -45, 45, -90, 90]

        self.interval_mode = 1 # start resting
        self.interval_count = 0
        self.interval_time = 0.0

        self.training_interval_duration = 0.02
        self.resting_inteval_duration = 0.05

        self.prev_shoulder_rot = None
        self.prev_elbow_rot = None
        self.shoulder_rot_input = None
        self.elbow_rot_input = None
        self.shoulder_vel_input = None
        self.elbow_vel_input = None
        self.target_dir_input = None
        self.shoulder_output = None
        self.elbow_output = None

        self.is_training = True

    def toggle_training(self):
        self.is_training = not self.is_training

    def set_home_position(self):
        self.shoulder_pivot.set_r(random.choice(self.home_position))
        self.elbow_pivot.set_r(random.choice(self.home_position))

    def rotate_elbow(self, dr):
        if dr is not None:
            self.elbow_pivot.set_r(self.elbow_pivot.get_r() + dr)

    def rotate_shoulder(self, dr):
        if dr is not None:
            self.shoulder_pivot.set_r(self.shoulder_pivot.get_r() + dr)

    def interval_train(self):
        self.actuator.shoulder_rot_input.input_value = self.shoulder_rot_input
        self.actuator.elbow_rot_input.input_value = self.elbow_rot_input
        self.actuator.shoulder_vel_input.input_value = self.shoulder_vel_input
        self.actuator.elbow_vel_input.input_value = self.elbow_vel_input
        self.actuator.target_dir_input.input_value = self.target_dir_input
        self.actuator.shoulder_output.input_value = self.shoulder_output
        self.actuator.elbow_output.input_value = self.elbow_output

    def interval_rest(self):
        # set end effector position before applying movements
        prev_end_effector_pos = self.end_effector.get_pos(self.arm_pivot)
        prev_shoulder_rot = get_angle(self.shoulder_pivot.get_r())
        prev_elbow_rot = get_angle(self.elbow_pivot.get_r())

        # generate random motor commands (erg)
        self.shoulder_output = random.uniform(-5.0, 5.0)
        self.elbow_output = random.uniform(-5.0, 5.0)

        # move joints randomly
        self.rotate_shoulder(self.shoulder_output)
        self.rotate_elbow(self.elbow_output)

        self.shoulder_rot_input = get_angle(self.shoulder_pivot.get_r())
        self.elbow_rot_input = get_angle(self.elbow_pivot.get_r())
        self.shoulder_vel_input = get_angle(self.shoulder_rot_input - prev_shoulder_rot)
        self.elbow_vel_input = get_angle(self.elbow_rot_input - prev_elbow_rot)
        self.target_dir_input = get_target_direction(self.end_effector.get_pos(self.arm_pivot) - prev_end_effector_pos)

    def train(self, dt):
        self.prev_shoulder_rot = None
        self.prev_elbow_rot = None

        if self.interval_mode == 0: # training interval
            if self.interval_time < self.training_interval_duration:
                self.interval_train()
                self.interval_time += dt
            else:
                self.interval_time = 0.0
                self.interval_mode = 1

        if self.interval_mode == 1: # resting interval
            if self.interval_time < self.resting_inteval_duration:
                self.interval_time += dt
            else:
                self.interval_time = 0.0
                self.interval_mode = 0
                self.interval_count += 1

                # every fourth interval, change home position
                if self.interval_count % 4 == 0:
                    self.set_home_position()

                self.interval_rest()

        self.actuator.tick(True)

        if self.actuator.err_mse > 1e-1:
            print ASCII_BACKGROUND, "testing", "err", self.actuator.err_mse, "shoulder_rot_input", self.actuator.shoulder_rot_input.err, "elbow_rot_input", self.actuator.elbow_rot_input.err, "shoulder_vel_input", self.actuator.shoulder_vel_input.err, "elbow_vel_input", self.actuator.elbow_vel_input.err, "target_dir_input", self.actuator.target_dir_input.err, "shoulder_output", self.actuator.shoulder_output.err, "elbow_output", self.actuator.elbow_output.err, ASCII_END
        else:
            print "testing", "err", self.actuator.err_mse, "shoulder_rot_input", self.actuator.shoulder_rot_input.err, "elbow_rot_input", self.actuator.elbow_rot_input.err, "shoulder_vel_input", self.actuator.shoulder_vel_input.err, "elbow_vel_input", self.actuator.elbow_vel_input.err, "target_dir_input", self.actuator.target_dir_input.err, "shoulder_output", self.actuator.shoulder_output.err, "elbow_output", self.actuator.elbow_output.err

    def evaluate(self, mouse_pos):
        self.target.set_pos(Vec3(mouse_pos.x, 0.0, mouse_pos.y) * 10.0)

        curr_target_pos = self.target.get_pos(self.arm_pivot)
        curr_end_effector_pos = self.end_effector.get_pos(self.arm_pivot)
        curr_shoulder_rot = get_angle(self.shoulder_pivot.get_r())
        curr_elbow_rot = get_angle(self.elbow_pivot.get_r())

        if self.prev_shoulder_rot is None or self.prev_elbow_rot is None:
            self.prev_shoulder_rot = curr_shoulder_rot
            self.prev_elbow_rot = curr_elbow_rot

        self.target_dir_input = get_target_direction(curr_target_pos - curr_end_effector_pos)

        self.actuator.shoulder_rot_input.input_value = curr_shoulder_rot
        self.actuator.elbow_rot_input.input_value = curr_elbow_rot
        self.actuator.shoulder_vel_input.input_value = curr_shoulder_rot - self.prev_shoulder_rot
        self.actuator.elbow_vel_input.input_value = curr_elbow_rot - self.prev_elbow_rot
        self.actuator.target_dir_input.input_value = self.target_dir_input

        self.actuator.tick(False)

        self.shoulder_output = self.actuator.shoulder_output.output_value
        self.elbow_output = self.actuator.elbow_output.output_value

        self.rotate_shoulder(self.shoulder_output)
        self.rotate_elbow(self.elbow_output)

        prev_end_effector_pos = curr_end_effector_pos
        curr_end_effector_pos = self.end_effector.get_pos(self.arm_pivot)

        direction_moved = get_target_direction(curr_end_effector_pos - prev_end_effector_pos)
        direction_err = abs(self.target_dir_input - direction_moved)

        print "evaluation", "err", direction_err, "shoulder_rot_input", self.actuator.shoulder_rot_input.err, "elbow_rot_input", self.actuator.elbow_rot_input.err, "shoulder_vel_input", self.actuator.shoulder_vel_input.err, "elbow_vel_input", self.actuator.elbow_vel_input.err, "target_dir_input", self.actuator.target_dir_input.err, "shoulder_output", self.actuator.shoulder_output.output_value, "elbow_output", self.actuator.elbow_output.output_value

        self.prev_shoulder_rot = curr_shoulder_rot
        self.prev_elbow_rot = curr_elbow_rot

    def tick(self, dt, mouse_pos):
        if self.is_training:
            self.train(dt)
        else:
            self.evaluate(mouse_pos)

        self.direction.look_at(self.target)
