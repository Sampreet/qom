#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module containing calculator functions."""

__name__    = 'qom_legacy.numerics.calculators'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-27'
__updated__ = '2021-01-06'

# dependencies
import logging
import numpy as np

# dev dependencies 
from qom_legacy.utils import misc

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle single parameter case for `get_grad`.

def get_grad(ys, xs, grad_params):
    """Function to calculate the gradient of a dataset at a particular position.
    
    Parameters
    ----------
    ys : list
        Values of the dataset.
    xs : list
        Positions of the dataset.
    grad_params : dict
        Options for the position.

    Returns
    -------
    grad : float
        Value of the gradient at the position.
    """

    # calculate gradients
    temp = np.gradient(ys, xs)

    # if position is specified
    if grad_params['mode'] == 'at_position':
        index = abs(np.asarray(xs) - grad_params['position']).argmin()

    # if vicinity is specified
    if grad_params['mode'] == 'near_position':
        # list of indices for mean of monotonic behaviour
        list_idx = misc.get_index_monotonic_mean(temp)

        # index of gradient position
        temp_index = abs(np.asarray(xs) - grad_params['position']).argmin()

        # get minimum index
        index = list_idx[abs(np.asarray(list_idx) - temp_index).argmin()]

    # if monotonocity mid position is specified
    if grad_params['mode'] == 'at_mono_mid':
        # list of indices for mean of monotonic behaviour
        list_idx = misc.get_index_monotonic_mean(temp)

        # get minimum index
        index = list_idx[grad_params['mono_id'] - 1]

    # if monotonocity local maxima/minima value is specified
    if grad_params['mode'] == 'at_mono_max_min':
        # list of indices for mean of monotonic behaviour
        list_idx = misc.get_index_monotonic_mean(temp)

        # get minimum index
        index = list_idx[grad_params['mono_id'] - 1]
    
    grad = temp[index]
    if 'divisor' in grad_params:
        grad /= grad_params['divisor']

    return grad


