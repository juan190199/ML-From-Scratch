import numpy as np


class Loss(object):
    def loss(self, y, y_pred):
        return NotImplementedError()

    def gradient(self, y, y_pred):
        return NotImplementedError()

    def acc(self, y, y_pred):
        return NotImplementedError()


class SquareLoss(Loss):
    def __init__(self): pass

    def loss(self, y, y_pred):
        return 0.5 * np.power((y - y_pred), axis=2)

    def gradient(self, y, y_pred):
        return -(y - y_pred)
