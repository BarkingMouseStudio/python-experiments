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

def connect(mn, mx, N_src, N_snk):
    S = SynapseGroup(N_src, N_snk)
    weights = np.random.rand(N_src.size, N_snk.size).astype(floatX)
    weights = denormalize(weights, mn, mx)
    S.W.set_value(weights)
    return S

class Actuator:

    def __init__(self):
        self.synapse_groups = []

        dt = 1.0 / 1000.0 # 1 ms

        self.noise_rate_ms = 5.0 * dt
        self.weight_min = -4.0
        self.weight_max = 4.0
        self.ticks_per_frame = 20
        self.now = 0

        self.shoulder_rot_input = ScalarPopulation(NeuronGroup(100), -180, 180)
        self.elbow_rot_input = ScalarPopulation(NeuronGroup(100), -180, 180)
        self.shoulder_vel_input = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.elbow_vel_input = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.target_dir_input = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.shoulder_output = ScalarPopulation(NeuronGroup(100), -5, 5)
        self.elbow_output = ScalarPopulation(NeuronGroup(100), -5, 5)

        self.connect_many(self.shoulder_rot_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.elbow_rot_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.shoulder_vel_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.elbow_vel_input.N, self.shoulder_output.N, self.elbow_output.N)
        self.connect_many(self.target_dir_input.N, self.shoulder_output.N, self.elbow_output.N)

    def connect_many(self, N_src, *args):
        for N_snk in args:
            S_inh = connect(self.weight_min, 0.0, N_src, N_snk)
            S_exc = connect(0.0, self.weight_max, N_src, N_snk)
            self.synapse_groups.append(S_inh)
            self.synapse_groups.append(S_exc)

    def tick(self, is_training):
        noise_rate_ms = self.noise_rate_ms if is_training else 0.0

        for i in range(0, self.ticks_per_frame):
            self.shoulder_rot_input.tick(self.now, noise_rate_ms)
            self.elbow_rot_input.tick(self.now, noise_rate_ms)
            self.shoulder_vel_input.tick(self.now, noise_rate_ms)
            self.elbow_vel_input.tick(self.now, noise_rate_ms)
            self.target_dir_input.tick(self.now, noise_rate_ms)
            self.shoulder_output.tick(self.now, noise_rate_ms)
            self.elbow_output.tick(self.now, noise_rate_ms)

            for synapse_group in self.synapse_groups:
                synapse_group.set_training(is_training)
                synapse_group.tick(self.now)

            self.now += 1
