#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Modules to calculate quantum correlation measures."""

__name__    = 'qom.measures.correlations'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-02-26'
__updated__ = '2020-12-04'

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
    num_modes   = meas_params['num_modes']
    mode_i      = meas_params['mode_i']
    mode_j      = meas_params['mode_j']

    # initialize lists
    M = []

    # for variation in V
    for i in range(len(V)):
        # calculate progress
        progress = float(i) / float(len(V)) * 100
        # display progress
        logger.debug('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

        # initialize value
        m = 0

        # correlation matrix
        mat_corr = np.real(V[i][num_modes:]).reshape([2 * num_modes, 2 * num_modes])
        # position of ith mode in the correlation matrix
        pos_i = 2 * mode_i
        # position of jth mode in the correlation matrix 
        pos_j = 2 * mode_j

        # get phase-related measures
        if meas_code.find('phase') != -1:
            m = globals()[meas_code](mat_corr, pos_i, pos_j, V[i][mode_i], V[i][mode_j])
        else:
            m = globals()[meas_code](mat_corr, pos_i, pos_j)

        # update lists
        M.append(m)

    # measures calculated
    return M

def disc(mat_corr, pos_i, pos_j):
    """Function to calculate Gaussian quantum discord between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_corr : list
        Matrix containing all correlations between quadratures of the modes.
    pos_i : int
        Position of ith mode in the correlation matrix.
    pos_j : int
        Position of jth mode in the correlation matrix.

    Returns
    -------
    D_G : float
        Gaussian quantum discord.
    """

    # symplectic invariants
    I_1, I_2, I_3, I_4 = get_invariants(mat_corr, pos_i, pos_j)

    try:
        # sum of symplectic invariants
        sigma = I_1 + I_2 + 2 * I_3
        # symplectic eigenvalues
        mu_plus = 1 / np.sqrt(2) * np.sqrt(sigma + np.sqrt(sigma**2 - 4 * I_4))
        mu_minus = 1 / np.sqrt(2) * np.sqrt(sigma - np.sqrt(sigma**2 - 4 * I_4))
    except ValueError:
        logger.warning('Argument of sqrt is negative.\n')
        return 0
        
    # quantum discord value
    return get_f(np.sqrt(I_2)) - get_f(mu_plus) - get_f(mu_minus) + get_f(np.sqrt(get_W(I_1, I_2, I_3, I_4)))

def get_invariants(mat_corr, pos_i, pos_j):
    """Helper function to calculate symplectic invariants for two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_corr : list
        Matrix containing all correlations between quadratures of the modes.
    pos_i : int
        Position of ith mode in the correlation matrix.
    pos_j : int
        Position of jth mode in the correlation matrix.

    Returns
    -------
    invariants : list
        Symplectic invariants.
    """

    # correlation matrix of ith mode
    A = np.matrix([ [   mat_corr[pos_i][pos_i],     mat_corr[pos_i][pos_i + 1]      ],
                    [   mat_corr[pos_i + 1][pos_i], mat_corr[pos_i + 1][pos_i + 1]  ]   ])
    # correlation matrix of jth mode
    B = np.matrix([ [   mat_corr[pos_j][pos_j],     mat_corr[pos_j][pos_j + 1]      ],
                    [   mat_corr[pos_j][pos_j + 1], mat_corr[pos_j + 1][pos_j + 1]  ]   ])
    # correlation matrix of intermodes
    C = np.matrix([ [   mat_corr[pos_i][pos_j],     mat_corr[pos_i][pos_j + 1]      ],
                    [   mat_corr[pos_i + 1][pos_j], mat_corr[pos_i + 1][pos_j + 1]  ]   ])
    # correlation matrix of the modes
    mat_corr_modes = np.matrix([[   mat_corr[pos_i][pos_i],     mat_corr[pos_i][pos_i + 1],     mat_corr[pos_i][pos_j],     mat_corr[pos_i][pos_j + 1]      ],
                                [   mat_corr[pos_i + 1][pos_i], mat_corr[pos_i + 1][pos_i + 1], mat_corr[pos_i + 1][pos_j], mat_corr[pos_i + 1][pos_j + 1]  ],
                                [   mat_corr[pos_j][pos_i],     mat_corr[pos_j][pos_i + 1],     mat_corr[pos_j][pos_j],     mat_corr[pos_j][pos_j + 1]      ],
                                [   mat_corr[pos_j + 1][pos_i], mat_corr[pos_j + 1][pos_i + 1], mat_corr[pos_j + 1][pos_j], mat_corr[pos_j + 1][pos_j + 1]  ]   ])

    # symplectic invariants
    return [np.linalg.det(A), np.linalg.det(B), np.linalg.det(C), np.linalg.det(mat_corr_modes)]

def get_f(x):
    """Helper function for quantum discord calculation."""

    try:
        return (x + 1 / 2) * np.log10(x + 1 / 2) - (x - 1 / 2) * np.log10(x - 1 / 2)
    except ValueError:
        logger.warning('Argument of log in f function is non-positive\n')
        return 0

def get_W(I_1, I_2, I_3, I_4):
    """Helper function for quantum discord calculation."""

    try: 
        if 4 * (I_1 * I_2 - I_4)**2 / (I_1 + 4 * I_4) / (1 + 4 * I_2) / I_3**2 <= 1.0:
            return ((2 * abs(I_3) + np.sqrt(4 * I_3**2 + (4 * I_2 - 1) * (4 * I_4 - I_1))) / (4 * I_2 - 1))**2
        return (I_1 * I_2 + I_4 - I_3**2 - np.sqrt((I_1 * I_2 + I_4 - I_3**2)**2 - 4 * I_1 * I_2 * I_4)) / 2 / I_2
    except ZeroDivisionError:
        logger.warning('Division by zero encountered in W function\n')
        return 0

def entan_bi_log_neg(mat_corr, pos_i, pos_j):
    """Function to calculate quantum entanglement via logarithmic negativity between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_corr : list
        Matrix containing all correlations between quadratures.
    pos_i : int
        Position of ith mode in the correlation matrix.
    pos_j : int
        Position of jth mode in the correlation matrix.

    Returns
    -------
    E_N : float
        Quantum entanglement value using logarithmic negativity.
    """

    # symplectic invariants
    I_1, I_2, I_3, I_4 = get_invariants(mat_corr, pos_i, pos_j)
    
    try:
        # sum of symplectic invariants after positive partial transpose
        sigma = I_1 + I_2 - 2*I_3
        # smallest symplectic eigenvalue
        mu_minus = 1 / np.sqrt(2) * np.sqrt(sigma - np.sqrt(sigma**2 - 4 * I_4))
    except ValueError:
        logger.warning('Argument of sqrt is negative\n')
        return 0

    try:
        # quantum entanglement value using logarithmic negativity
        E_N =  -1 * (np.log(2 * mu_minus))
    except ValueError:
        logger.warning('Argument of ln is non-positive\n')
        return 0
    else:
        return max(0, E_N)

def sync_comp(mat_corr, pos_i, pos_j):
    """Function to calculate quantum complete synchronization between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_corr : list
        Matrix containing all correlations between quadratures.
    pos_i : int
        Position of ith mode in the correlation matrix.
    pos_j : int
        Position of jth mode in the correlation matrix.

    Returns
    -------
    S_C : float
        Quantum complete synchronization value.
    """

    # square difference between position quadratures
    q_minus_2 = 0.5 * (mat_corr[pos_i][pos_i] + mat_corr[pos_j][pos_j] - 2 * mat_corr[pos_i][pos_j])
    # square difference between momentum quadratures
    p_minus_2 = 0.5 * (mat_corr[pos_i + 1][pos_i + 1] + mat_corr[pos_j + 1][pos_j + 1] - 2 * mat_corr[pos_i + 1][pos_j + 1])

    try: 
        # quantum complete synchronization value
        return 1 / (q_minus_2 + p_minus_2)
    except ZeroDivisionError:
        logger.warning('Division by zero encountered in W function\n')
        return 0

def sync_phase(mat_corr, pos_i, pos_j, mode_i, mode_j):
    """Function to calculate quantum phase synchronization between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_corr : list
        Matrix containing all correlations between quadratures.
    pos_i : int
        Position of ith mode in the correlation matrix.
    pos_j : int
        Position of jth mode in the correlation matrix.
    mode_i : np.complex
        Value of the ith mode.
    mode_j : np.complex
        Value of the jth mode.

    Returns
    -------
    S_P : float
        Quantum phase synchronization value.
    """

    # arguments
    arg_i = np.angle(mode_i)
    arg_j = np.angle(mode_j)
    
    # transformation for ith mode momentum quadrature
    p_i_prime_2 = (np.sin(arg_i))**2 * mat_corr[pos_i][pos_i] - (np.sin(arg_i)) * (np.cos(arg_i)) * mat_corr[pos_i][pos_i + 1] - (np.cos(arg_i)) * (np.sin(arg_i)) * mat_corr[pos_i + 1][pos_i] + (np.cos(arg_i))**2 * mat_corr[pos_i + 1][pos_i + 1] 

    # transformation for jth mode momentum quadrature
    p_j_prime_2 = (np.sin(arg_j))**2 * mat_corr[pos_j][pos_j] - (np.sin(arg_j)) * (np.cos(arg_j)) * mat_corr[pos_j][pos_j + 1] - (np.cos(arg_j)) * (np.sin(arg_j)) * mat_corr[pos_j + 1][pos_j] + (np.cos(arg_j))**2 * mat_corr[pos_j + 1][pos_j + 1]

    # transformation for intermode momentum quadratures
    p_i_p_j_prime = (np.sin(arg_i)) * (np.sin(arg_j)) * mat_corr[pos_i][pos_j] - (np.sin(arg_i)) * (np.cos(arg_j)) * mat_corr[pos_i][pos_j + 1] - (np.cos(arg_i)) * (np.sin(arg_j)) * mat_corr[pos_i + 1][pos_j] + (np.cos(arg_i)) * (np.cos(arg_j)) * mat_corr[pos_i + 1][pos_j + 1]

    # square difference between momentum quadratures
    p_minus_prime_2 = 1 / 2 * (p_i_prime_2 + p_j_prime_2 - 2 * p_i_p_j_prime)

    # quantum phase synchronization value
    return 1 / 2 / p_minus_prime_2

def sync_phase_rot(mat_corr, pos_i, pos_j, mode_i, mode_j):
    """Function to calculate quantum phase synchronization between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_corr : list
        Matrix containing all correlations between quadratures.
    pos_i : int
        Position of ith mode in the correlation matrix.
    pos_j : int
        Position of jth mode in the correlation matrix.
    mode_i : np.complex
        Value of the ith mode.
    mode_j : np.complex
        Value of the jth mode.

    Returns
    -------
    S_P : float
        Quantum phase synchronization value.
    """

    # arguments
    arg_i = np.angle(mode_i)
    arg_j = np.angle(mode_j)

    # TODO: complete function

    # rotated quadratures
    return np.cos(arg_i) * np.cos(arg_j) * mat_corr[pos_i + 1][pos_j + 1] - np.cos(arg_i) * np.sin(arg_j) * mat_corr[pos_i + 1][pos_j] - np.sin(arg_i) * np.cos(arg_j) * mat_corr[pos_i][pos_j + 1] + np.sin(arg_i) * np.sin(arg_j) * mat_corr[pos_i][pos_j]