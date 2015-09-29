from __future__ import division

import math
import numpy as np
import theano
import theano.tensor as T

from neural.neuron_group import NeuronGroup
from neural.synapse_group import SynapseGroup
from scalar_population import ScalarPopulation

floatX = theano.config.floatX

def normalize(x, mn, mx):
    return (x - mn) / (mx - mn)

def denormalize(x, mn, mx):
    return (x * (mx - mn)) + mn

def connect(N_src, N_snk, mn, mx):
    stdev = (mx - mn) / 3.0 # +-3 sigmas
    mean = (abs(mx) - abs(mn)) / 2.0

    synapse_group = SynapseGroup(N_src, N_snk, mn, mx)
    weight = np.clip(np.random.randn(N_src.size, N_snk.size).astype(floatX) * stdev + mean, mn, mx)
    synapse_group.weight.set_value(weight)
    synapse_group.delay = 1
    return synapse_group

class Actuator:

    def __init__(self):
        self.synapse_groups = []

        dt = 1.0 / 1000.0 # 1 ms

        self.noise_rate_ms = 5.0 * dt
        self.weight_max = 4.0
        self.weight_min = -4.0
        self.ticks_per_frame = 20
        self.now = 0

        self.shoulder_rot_input = ScalarPopulation(NeuronGroup(100), -180, 180)
        self.elbow_rot_input = ScalarPopulation(NeuronGroup(100), -180, 180)
        self.shoulder_vel_input = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.elbow_vel_input = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.target_dir_input = ScalarPopulation(NeuronGroup(100), -180, 180)
        self.shoulder_output = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.elbow_output = ScalarPopulation(NeuronGroup(100), -5, 5)

        self.connect_many(self.shoulder_rot_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.elbow_rot_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.shoulder_vel_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.elbow_vel_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.target_dir_input.N, self.shoulder_output.N, self.elbow_output.N)

    def connect_many(self, N_src, *args):
        for N_snk in args:
            S_exc = connect(N_src, N_snk, 0.0, self.weight_max)
            S_inh = connect(N_src, N_snk, self.weight_min, 0.0)
            self.synapse_groups.append(S_exc)
            self.synapse_groups.append(S_inh)

    def tick(self, is_training):
        noise_rate_ms = self.noise_rate_ms if is_training else 0.0

        err_sum = 0.0

        for i in range(0, self.ticks_per_frame):
            self.shoulder_rot_input.tick(self.now, noise_rate_ms)
            self.elbow_rot_input.tick(self.now, noise_rate_ms)
            self.shoulder_vel_input.tick(self.now, noise_rate_ms)
            self.elbow_vel_input.tick(self.now, noise_rate_ms)
            self.target_dir_input.tick(self.now, noise_rate_ms)
            self.shoulder_output.tick(self.now, noise_rate_ms)
            self.elbow_output.tick(self.now, noise_rate_ms)

            for synapse_group in self.synapse_groups:
                synapse_group.tick(self.now, is_training, not is_training)

            err = 0.0
            err += self.shoulder_rot_input.err
            err += self.elbow_rot_input.err
            err += self.shoulder_vel_input.err
            err += self.elbow_vel_input.err
            err += self.target_dir_input.err
            err += self.shoulder_output.err
            err += self.elbow_output.err
            err_sum += math.pow(err, 2)

            self.now += 1

        # clear input
        self.shoulder_rot_input.input_value = None
        self.elbow_rot_input.input_value = None
        self.shoulder_vel_input.input_value = None
        self.elbow_vel_input.input_value = None
        self.target_dir_input.input_value = None
        self.shoulder_output.input_value = None
        self.elbow_output.input_value = None

        self.err_mse = err_sum / self.ticks_per_frame
