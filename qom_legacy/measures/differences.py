#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Modules to calculate difference measures."""

__name__    = 'qom_legacy.measures.differences'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-08-24'
__updated__ = '2021-01-06'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

def calculate(V, meas_params):
    """Wrapper function to switch functions for calculation of measures.
    
    Parameters
    ----------
    V : list
        Values of the variables.
    meas_params : dict
        Parameters for the calculation.

    Returns
    -------
    M : float
        Measures calculated.
    """

    # extract frequently used variables
    meas_code   = meas_params['code']
    mode_i      = meas_params['mode_i']
    mode_j      = meas_params['mode_j']
    arg_str     = 'pos'
    if 'arg_str' in meas_params:
        arg_str = meas_params['arg_str']

    # measures calculated
    return globals()[meas_code](V, mode_i, mode_j, arg_str)

def phase_match_cos(V, mode_i, mode_j, quad='mode'):
    """Function to calculate the wrapped phase difference between two modes given their values.

    Parameters
    ----------
    V : list
        Values of the variables.
    mode_i : int
        Position of ith mode.
    mode_j : int
        Position of jth mode.
    quad : str
        Option of the quadrature selection:
            * 'mode':   Default mode.
            * 'pos' :   Position quadrature.
            * 'mom' :   Momentum quadrature.

    Returns
    -------
    M : float
        Phase difference measures using cosine matching.
    """

    # initialize variables
    prev_i  = 0
    prev_j  = 0
    incr_i  = True
    incr_j  = True
    per_i   = [0]
    per_j   = [0]
    phase_i = [0]
    phase_j = [0]

    # for variation in V
    for k in range(len(V)):
        # calculate progress
        progress = float(k) / float(len(V)) * 100
        # display progress
        logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

        if quad == 'mode':
            curr_i = np.abs(V[k][mode_i])
            curr_j = np.abs(V[k][mode_j])
        elif quad == 'pos':
            curr_i = np.real(V[k][mode_i] * np.sqrt(2))
            curr_j = np.real(V[k][mode_j] * np.sqrt(2))
        elif quad == 'mom':
            curr_i = np.imag(V[k][mode_i] * np.sqrt(2))
            curr_j = np.imag(V[k][mode_j] * np.sqrt(2))

        # if first curve changes monotonicity
        if prev_i > curr_i and incr_i:
            incr_i = False
            phase_i += np.linspace((len(per_i) - 1) * 2 * np.pi, len(per_i) * 2 * np.pi, k - per_i[-1] + 1).tolist()[1:]
            per_i.append(k)
        elif prev_i <= curr_i and not incr_i:
            incr_i = True

        # if second curve changes monotonicity
        if prev_j > curr_j and incr_j:
            incr_j = False
            phase_j += np.linspace((len(per_j) - 1) * 2 * np.pi, len(per_j) * 2 * np.pi, k - per_j[-1] + 1).tolist()[1:]
            per_j.append(k)
        elif prev_j <= curr_j and not incr_j:
            incr_j = True

        # update values
        prev_i = curr_i
        prev_j = curr_j

    # adjust beginnings
    phase_i[per_i[0]:per_i[1]] = np.linspace(3 * np.pi / 2, 2 * np.pi, per_i[1] - per_i[0] + 1).tolist()[:-1]
    phase_j[per_j[0]:per_j[1]] = np.linspace(3 * np.pi / 2, 2 * np.pi, per_j[1] - per_j[0] + 1).tolist()[:-1]

    # adjust endings
    phase_i += [2 * np.pi + val for val in phase_i[per_i[-2] + 1:per_i[-2] + len(V) - per_i[-1]]]
    phase_j += [2 * np.pi + val for val in phase_j[per_j[-2] + 1:per_j[-2] + len(V) - per_j[-1]]]

    return ((np.array(phase_j) - np.array(phase_i)) % (2 * np.pi)) * 180 / np.pi

        