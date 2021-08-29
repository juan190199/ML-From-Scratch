import sys

import math
import numpy as np


def euclidean_distance(x1, x2):
    """
    :param x1: ndarray of shape (n_samples1, n_features)
    :param x2:ndarray of shape (n_samples2, n_features)
    :return:
    """
    distance = np.sqrt(np.sum(np.square(np.subtract(x1[:, None, :], x2)), axis=2))
    return distance
