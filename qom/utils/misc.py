#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module for miscellaneous utility functions."""

__name__    = 'qom.utils.misc'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-27'
__updated__ = '2020-09-27'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# TODO: Verify `get_limits` function.

def get_index_monotonic_mean(values):
    """Function to calculate the position of the mid points of monotonicity for given function data.
    
    Parameters
    ----------
        values : list
            Values of the data.

    Returns
    -------
        idx : list
            Indices of the mid points.
    """
    
    # list of signum values
    sgn = [1 if ele >= 0 else -1 for ele in values]
    # list of mid points of same sign
    idx = []
    # sign of element
    sign = sgn[0]
    # start index
    i = 0
    for j in range(1, len(sgn)):
        # if sign changes
        if sgn[j] != sign:
            # mark mid value of previous cluster
            idx.append((int) ((i + j - 1) / 2))
            sign = sgn[j]
            i = j
    idx.append((int) ((i + len(sgn) - 1) / 2))

    return idx

def get_index_monotonic_max_min(values):
    """Function to calculate the position of the local maximas/minimas of monotonicity for given function data.
    
    Parameters
    ----------
        values : list
            Values of the data.

    Returns
    -------
        idx : list
            Indices of the local maximas points.
    """
    
    # list of signum values
    sgn = [1 if ele >= 0 else -1 for ele in values]
    # list of local maxima/minima points of same sign
    idx = []
    # sign of element
    sign = sgn[0]
    # start index
    i = 0
    for j in range(1, len(sgn)):
        # if sign changes
        if sgn[j] != sign:
            # mark max value of previous cluster
            idx.append(np.abs(np.asarray(values[i:j - 1])).argmax() + i)
            sign = sgn[j]
            i = j
    idx.append(np.abs(np.asarray(values[i:j - 1])).argmax() + i)

    return idx

def get_index_threshold(values, thres_mode='max_min'):
    """Function to obtain the indices of threshold for a given mode.

    Parameters
    ----------
        values : list
            Values of the variable.

        thres_mode : str
            Mode of threshold index calculation:
                min_min : Minimum index where minimum is observed.
                min_max : Maximum index where minimum is observed.
                max_min : Minimum index where minimum is observed.
                max_max : Maximum index where minimum is observed.

    Returns
    -------
        res : list
            Indices of the threshold.
    """

    # indices of minimas and maximas
    idx_min = np.argwhere(np.array(values) == np.amin(values)).flatten().tolist()
    idx_max = np.argwhere(np.array(values) == np.amax(values)).flatten().tolist()

    # handle 1D array
    _dim = len(np.shape(values))
    idx_min = [idx_min[2 * i : 2 * i + _dim] for i in range(int(len(idx_min) / _dim))]
    idx_max = [idx_max[2 * i : 2 * i + _dim] for i in range(int(len(idx_max) / _dim))]

    # required threshold
    res = {
        'min_min': idx_min[0],
        'min_max': idx_min[-1],
        'max_min': idx_max[0],
        'max_max': idx_max[-1]
    }

    return res[thres_mode]

def get_limits(mini, maxi, res=2):
    """Function to get limits from the minimum and maximum values of an array upto a certain resolution.

    Parameters
    ----------
        mini : list  
            Minimum value of the array.
        
        maxi : list  
            Maximum value of the array.

        res : int
            Resolution after the first significant digit in the decimal number system.

    Returns
    -------
        mini : float
            Formatted minimum value.

        maxi : float
            Formatted maximum value.

        prec : int
            Precision of rounding off.
    """

    # get minimum maximum
    _mini = mini
    _maxi = maxi
    _mult_min = 10**res
    _mult_max = 10**res

    # handle negative values
    if _mini < 0:
        _mini *= - 1
    if _maxi < 0:
        _maxi *= - 1

    # update multiplier
    if _mini != 0 and np.log10(_mini) < res:
        _mult_min = 10**(np.ceil(-np.log10(_mini)) + res - 1)
    if _maxi != 0 and np.log10(_maxi) < res:
        _mult_max = 10**(np.ceil(-np.log10(_maxi)) + res - 1)
    _mult = max(10**res, min(_mult_min, _mult_max))

    # round off
    _mini = np.round(mini * _mult) / _mult
    _maxi = np.round(maxi * _mult) / _mult
    _prec = int(np.round(np.log10(_mult)))

    return _mini, _maxi, _prec


