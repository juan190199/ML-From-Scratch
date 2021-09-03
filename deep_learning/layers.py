import math
import numpy as np

import copy

from deep_learning.activation_functions import (Sigmoid, ReLu, SoftPlus, LeakyReLu, TanH, ELU, SELU, Softmax)


class Layer(object):

    def set_input_shape(self, shape):
        """
        Sets the shape that the layer expects of the input in the forward pass method

        :param shape: tuple
            Expected shape of the input in the forward pass method

        :return:
        """
        self.input_shape = shape

    def layer_name(self):
        """
        The name of the layer. Used in model summary.
        :return:
        """
        return self.__class__.__name__

    def parameters(self):
        """
        Number of trainable parameters used by the layer
        :return:
        """
        return 0

    def forward_pass(self, X, training):
        """
        Propagates the signal forward in the network

        :param X:
        :param training:
        :return:
        """
        raise NotImplementedError

    def backward_pass(self, accum_grad):
        """
        Propogates the accumulated gradient backwards in the network.
        If it has trainable weights then these weights are also tuned in this method.
        As input (accum_grad) it receives the gradient with respect to the output of the layer and
        returns the gradient with respect to the output of the previous layer.

        :param accum_grad:
        :return:
        """
        raise NotImplementedError

    def output_shape(self):
        """
        Shape of the output produced by forward pass
        :return:
        """
        raise NotImplementedError


class Dense(Layer):
    """
    A fully-connected NN layer
    """

    def __init__(self, n_units, input_shape=None):
        """

        :param n_units: int
            Number of neurons in the layer

        :param input_shape: tuple
            Expected input shape of the layer.
            For dense layers, a single digit indicating the number of features of the input
            must be specified if it is the first layer in the network
        """
        self.layer_input = None
        self.input_shape = input_shape
        self.n_units = n_units
        self.trainable = True
        self.w = None
        self.b = None

    def initialize(self, optimizer):
        # Initialize the weights
        limit = 1 / math.sqrt(self.input.shape[0])
        self.w = np.random.uniform(-limit, limit, (self.input.shape[0], self.n_units))
        self.b = np.zeros((1, self.n_units))
        # Weight optimizers
        self.w_opt = copy.copy(optimizer)
        self.b_opt = copy.copy(optimizer)

    def parameters(self):
        return np.prod(self.w.shape) + np.prod(self.b.shape)

    def forward_pass(self, X, training):
        self.layer_input = X
        return X.dot(self.w) + self.b

    def backward_pass(self, accum_grad):
        # Save weights used during forward pass
        w = self.w

        if self.trainable:
            # Calculate gradient w.r.t. layer weights
            grad_w = self.layer_input.T.dot(accum_grad)
            grad_b = np.sum(accum_grad, axis=0, keepdims=True)

            # Update the layers weight
            # w = w - self.learning_rate * grad_w
            self.w = self.w_opt.update(self.w, grad_w)
            self.b = self.b_opt.update(self.b, grad_b)

        # Return accumulated gradient for next_layer
        # Calculated based on the weights used during the forward pass
        accum_grad = accum_grad.dot(w.T)
        return accum_grad

    def output_shape(self):
        return (self.n_units,)


class Dropout(Layer):
    """
    A layer that randomly sets a fraction p of the output units of the previous layer to zero
    """
    def __init__(self, p=0.2):
        """

        :param p: float
            Probability that unit x is set to zero.
        """
        self.p = p
        self._mask = None
        self.input_shape = None
        self.n_units = None
        self.pass_through = True
        self.trainable = True

    def forward_pass(self, X, training):
        c = (1 - self.p)
        if training:
            self._mask = np.random.uniform(size=X.shape) > self.p
            c = self._mask
            return X * c

    def backward_pass(self, accum_grad):
        return accum_grad * self._mask

    def output_shape(self):
        return self.input_shape


activation_functions = {
    'relu': ReLu,
    'sigmoid': Sigmoid,
    'selu': SELU,
    'elu': ELU,
    'softmax': Softmax,
    'leaky_relu': LeakyReLu,
    'tanh': TanH,
    'softplus': SoftPlus
}


class Activation(Layer):
    """
    A layer that applies an activation to the input
    """
    def __init__(self, name):
        """

        :param name: string
            Name of the activation function that will be used.
        """
        self.activation_name = name
        self.activation_func = activation_functions[name]()
        self.trainable = True

    def layer_name(self):
        return "Activation (%s)" % (self.activation_func.__class__.__name__)

    def forward_pass(self, X, training):
        self.layer_input = X
        return self.activation_func(X)

    def backward_pass(self, accum_grad):
        return accum_grad * self.activation_func.gradient(self.layer_input)

    def output_shape(self):
        return self.input_shape