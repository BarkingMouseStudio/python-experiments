from __future__ import division

import numpy as np
import theano

from neural.com_estimator import COMEstimator

floatX = theano.config.floatX

def normalize(x, mn, mx):
    return (x - mn) / (mx - mn)

def denormalize(x, mn, mx):
    return (x * (mx - mn)) + mn

class ScalarPopulation:

    def __init__(self, N, mn, mx):
        self.N = N
        self.encoding = COMEstimator(self.N.size, 3.0, 3.0)
        self.output_value = None
        self.input_value = None
        self.err = None
        self.min = mn
        self.max = mx

    def tick(self, now, noise_rate_ms):
        if noise_rate_ms > 0.0:
            input_vec = (np.random.rand(self.N.size) < noise_rate_ms).astype(floatX) * 125.0
        else:
            input_vec = np.zeros(self.N.size).astype(floatX)

        if self.input_value is not None:
            input_norm = normalize(self.input_value, self.min, self.max)
            self.encoding.encode(input_vec, input_norm)

        self.N.tick(now, input_vec)

        output_norm = self.encoding.decode(self.N.rate.get_value())
        if output_norm is not None:
            self.output_value = denormalize(output_norm, self.min, self.max)
        else:
            self.output_value = None

        if self.input_value is not None and self.output_value is not None:
            input_norm = normalize(self.input_value, self.min, self.max)
            self.err = abs(input_norm - output_norm)
        else:
            self.err = None
