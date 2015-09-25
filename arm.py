import math
import random
import numpy as np

from panda3d.core import NodePath

from actuator import Actuator

def get_target_direction(direction):
    direction.normalize()
    angle = math.atan2(direction.z, direction.x)
    return math.degrees(angle)

def get_angle(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle

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

        self.target = NodePath("target")
        self.target.reparent_to(self.arm_pivot)
        self.target.set_pos(0, 0, 10)

        model_upper = loader.loadModel("box_segment.egg")
        model_lower = loader.loadModel("box_segment.egg")
        model_effector = loader.loadModel("icosphere.egg")
        model_target = loader.loadModel("icosphere.egg")

        model_target.reparent_to(self.target)
        model_target.setScale(0.5, 0.5, 0.5)

        model_upper.reparent_to(self.shoulder_pivot)
        model_upper.set_pos(0, 0, 2.5)

        model_lower.reparent_to(self.elbow_pivot)
        model_lower.set_pos(0, 0, 2.5)

        model_effector.reparent_to(self.end_effector)
        model_effector.setScale(0.5, 0.5, 0.5)

        self.actuator = Actuator()
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
        self.elbow_pivot.set_r(self.elbow_pivot.get_r() + dr)

    def rotate_shoulder(self, dr):
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
        if self.shoulder_output:
            self.rotate_shoulder(self.shoulder_output)
        if self.elbow_output:
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
            self.interval_train()

            if self.interval_time < self.training_interval_duration:
                self.interval_time += dt
            else:
                self.interval_time = 0.0
                self.interval_mode = 1

        if self.interval_mode == 1: # resting interval
            self.shoulder_rot_input = None
            self.elbow_rot_input = None
            self.shoulder_vel_input = None
            self.elbow_vel_input = None
            self.target_dir_input = None
            self.shoulder_output = None
            self.elbow_output = None

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

        print (self.actuator.shoulder_rot_input.err, self.actuator.elbow_rot_input.err, self.actuator.shoulder_vel_input.err, self.actuator.elbow_vel_input.err, self.actuator.target_dir_input.err, self.actuator.shoulder_output.err, self.actuator.elbow_output.err)

    def evaluate(self):
        curr_shoulder_rot = get_angle(self.shoulder_pivot.get_r())
        curr_elbow_rot = get_angle(self.elbow_pivot.get_r())

        if self.prev_shoulder_rot is None or self.prev_elbow_rot is None:
            self.shoulder_pivot.set_r(0.0)
            self.elbow_pivot.set_r(0.0)

            self.prev_shoulder_rot = curr_shoulder_rot
            self.prev_elbow_rot = curr_elbow_rot

        self.actuator.shoulder_rot_input.input_value = get_angle(self.shoulder_pivot.get_r())
        self.actuator.elbow_rot_input.input_value = get_angle(self.elbow_pivot.get_r())
        self.actuator.shoulder_vel_input.input_value = curr_shoulder_rot - self.prev_shoulder_rot
        self.actuator.elbow_vel_input.input_value = curr_elbow_rot - self.prev_elbow_rot
        self.actuator.target_dir_input.input_value = get_target_direction(self.target.get_pos(self.arm_pivot) - self.end_effector.get_pos(self.arm_pivot))

        self.actuator.tick(False)

        self.shoulder_output = self.actuator.shoulder_output.output_value
        self.elbow_output = self.actuator.elbow_output.output_value

        print (self.actuator.shoulder_rot_input.err, self.actuator.elbow_rot_input.err, self.actuator.shoulder_vel_input.err, self.actuator.elbow_vel_input.err, self.actuator.target_dir_input.err)

        if self.shoulder_output:
            self.rotate_shoulder(self.shoulder_output)
        if self.elbow_output:
            self.rotate_elbow(self.elbow_output)

        self.prev_shoulder_rot = curr_shoulder_rot
        self.prev_elbow_rot = curr_elbow_rot

    def tick(self, dt):
        if self.is_training:
            self.train(dt)

            # save weights
            for i, synapse_group in enumerate(self.actuator.synapse_groups):
                np.savetxt('weights_%d.out' % i, synapse_group.weight.get_value(), delimiter=',')
        else:
            self.evaluate()
