#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Modules to calculate quantum correlation measures."""

__name__    = 'qom.measures.corr'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-02-26'
__updated__ = '2020-06-09'

# dependencies
import logging
from numpy import abs, angle, cos, log, log10, matrix, sin, sqrt 
from numpy.linalg import det

# module logger
logger = logging.getLogger(__name__)

def disc(Corr_mat, pos_i, pos_j):
    """Function to calculate quantum discord between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    Corr_mat : list
        Matrix containing all correlations between quadratures of the modes.

    pos_i : *int*
        Position of ith mode in the correlation matrix.

    pos_j : *int*
        Position of jth mode in the correlation matrix.

    Returns
    -------
    qd : float
        Quantum discord value.
    """

    # symplectic invariants
    I_1, I_2, I_3, I_4 = get_invariants(Corr_mat, pos_i, pos_j)

    try:
        # sum of symplectic invariants
        sigma = I_1 + I_2 + 2*I_3
        # symplectic eigenvalues
        mu_plus = 1/sqrt(2)*sqrt(sigma + sqrt(sigma**2 - 4*I_4))
        mu_minus = 1/sqrt(2)*sqrt(sigma - sqrt(sigma**2 - 4*I_4))
    except ValueError:
        logger.warning('Argument of sqrt is negative.\n')
        return 0
        
    # quantum discord value
    return get_f(sqrt(I_2)) - get_f(mu_plus) - get_f(mu_minus) + get_f(sqrt(get_W(I_1, I_2, I_3, I_4)))

def get_invariants(Corr_mat, pos_i, pos_j):
    """Helper function to calculate symplectic invariants for two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    Corr_mat : list
        Matrix containing all correlations between quadratures of the modes.

    pos_i : *int*
        Position of ith mode in the correlation matrix.

    pos_j : *int*
        Position of jth mode in the correlation matrix.

    Returns
    -------
    invariants : list
        Symplectic invariants.
    """

    # correlation matrix of ith mode
    A = matrix([[   Corr_mat[pos_i][pos_i],     Corr_mat[pos_i][pos_i + 1]      ],
                [   Corr_mat[pos_i + 1][pos_i], Corr_mat[pos_i + 1][pos_i + 1]  ]   ])
    # correlation matrix of jth mode
    B = matrix([[   Corr_mat[pos_j][pos_j],     Corr_mat[pos_j][pos_j + 1]      ],
                [   Corr_mat[pos_j][pos_j + 1], Corr_mat[pos_j + 1][pos_j + 1]  ]   ])
    # correlation matrix of intermodes
    C = matrix([[   Corr_mat[pos_i][pos_j],     Corr_mat[pos_i][pos_j + 1]      ],
                [   Corr_mat[pos_i + 1][pos_j], Corr_mat[pos_i + 1][pos_j + 1]  ]   ])
    # correlation matrix of the modes
    Corr_mat_modes = matrix([   [   Corr_mat[pos_i][pos_i],     Corr_mat[pos_i][pos_i + 1],     Corr_mat[pos_i][pos_j],     Corr_mat[pos_i][pos_j + 1]      ],
                                [   Corr_mat[pos_i + 1][pos_i], Corr_mat[pos_i + 1][pos_i + 1], Corr_mat[pos_i + 1][pos_j], Corr_mat[pos_i + 1][pos_j + 1]  ],
                                [   Corr_mat[pos_j][pos_i],     Corr_mat[pos_j][pos_i + 1],     Corr_mat[pos_j][pos_j],     Corr_mat[pos_j][pos_j + 1]      ],
                                [   Corr_mat[pos_j + 1][pos_i], Corr_mat[pos_j + 1][pos_i + 1], Corr_mat[pos_j + 1][pos_j], Corr_mat[pos_j + 1][pos_j + 1]  ]   ])

    # symplectic invariants
    return [det(A), det(B), det(C), det(Corr_mat_modes)]

def get_f(x):
    """Helper function for quantum discord calculation."""

    try:
        return (x + 1/2)*log10(x + 1/2) - (x - 1/2)*log10(x - 1/2)
    except ValueError:
        logger.warning('Argument of log in f function is non-positive\n')
        return 0

def get_W(I_1, I_2, I_3, I_4):
    """Helper function for quantum discord calculation."""
    try: 
        if 4*(I_1*I_2 - I_4)**2/(I_1 + 4*I_4)/(1 + 4*I_2)/I_3**2 <= 1.0:
            return ((2*abs(I_3) + sqrt(4*I_3**2 + (4*I_2 - 1)*(4*I_4 - I_1)))/(4*I_2 - 1))**2
        return (I_1*I_2 + I_4 - I_3**2 - sqrt((I_1*I_2 + I_4 - I_3**2)**2 - 4*I_1*I_2*I_4))/2/I_2
    except ZeroDivisionError:
        logger.warning('Division by zero encountered in W function\n')
        return 0

def entan_bi_log_neg(Corr_mat, pos_i, pos_j):
    """Function to calculate quantum entanglement via logarithmic negativity between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    Corr_mat : list
        Matrix containing all correlations between quadratures.

    pos_i : *int*
        Position of ith mode in the correlation matrix.

    pos_j : *int*
        Position of jth mode in the correlation matrix.

    Returns
    -------
    qe_log_neg : float
        Quantum entanglement value using logarithmic negativity.
    """

    # symplectic invariants
    I_1, I_2, I_3, I_4 = get_invariants(Corr_mat, pos_i, pos_j)
    
    try:
        # sum of symplectic invariants after positive partial transpose
        sigma = I_1 + I_2 - 2*I_3
        # smallest symplectic eigenvalue
        mu_minus = 1 / sqrt(2) * sqrt(sigma - sqrt(sigma**2 - 4*I_4))
    except ValueError:
        logger.warning('Argument of sqrt is negative\n')
        return 0

    try:
        # quantum entanglement value using logarithmic negativity
        qe_log_neg =  -1*(log(2 * mu_minus))
    except ValueError:
        logger.warning('Argument of ln is non-positive\n')
        return 0
    else:
        return max(0, qe_log_neg)

def sync_comp(Corr_mat, pos_i, pos_j):
    """Function to calculate quantum complete synchronization between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    Corr_mat : list
        Matrix containing all correlations between quadratures.

    pos_i : *int*
        Position of ith mode in the correlation matrix.

    pos_j : *int*
        Position of jth mode in the correlation matrix.

    Returns
    -------
    qs_c : float
        Quantum complete synchronization value.
    """

    # square difference between position quadratures
    q_minus_2 = 0.5*(Corr_mat[pos_i][pos_i] + Corr_mat[pos_j][pos_j] - 2*Corr_mat[pos_i][pos_j])
    # square difference between momentum quadratures
    p_minus_2 = 0.5*(Corr_mat[pos_i + 1][pos_i + 1] + Corr_mat[pos_j + 1][pos_j + 1] - 2*Corr_mat[pos_i + 1][pos_j + 1])

    try: 
        # quantum complete synchronization value
        return 1/(q_minus_2 + p_minus_2)
    except ZeroDivisionError:
        logger.warning('Division by zero encountered in W function\n')
        return 0

def sync_phase(Corr_mat, pos_i, pos_j, mode_i, mode_j):
    """Function to calculate quantum phase synchronization between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    Corr_mat : list
        Matrix containing all correlations between quadratures.

    pos_i : *int*
        Position of ith mode in the correlation matrix.

    pos_j : *int*
        Position of jth mode in the correlation matrix.

    mode_i : np.complex
        Value of the ith mode.

    mode_j : np.complex
        Value of the jth mode.

    Returns
    -------
    qs_p : float
        Quantum phase synchronization value.
    """

    # arguments
    arg_i = angle(mode_i)
    arg_j = angle(mode_j)
    
    # transformation for ith mode momentum quadrature
    p_i_prime_2 = (sin(arg_i))**2*Corr_mat[pos_i][pos_i] - (sin(arg_i))*(cos(arg_i))*Corr_mat[pos_i][pos_i + 1] - (cos(arg_i))*(sin(arg_i))*Corr_mat[pos_i + 1][pos_i] + (cos(arg_i))**2*Corr_mat[pos_i + 1][pos_i + 1] 

    # transformation for jth mode momentum quadrature
    p_j_prime_2 = (sin(arg_j))**2*Corr_mat[pos_j][pos_j] - (sin(arg_j))*(cos(arg_j))*Corr_mat[pos_j][pos_j + 1] - (cos(arg_j))*(sin(arg_j))*Corr_mat[pos_j + 1][pos_j] + (cos(arg_j))**2*Corr_mat[pos_j + 1][pos_j + 1]

    # transformation for intermode momentum quadratures
    p_i_p_j_prime = (sin(arg_i))*(sin(arg_j))*Corr_mat[pos_i][pos_j] - (sin(arg_i))*(cos(arg_j))*Corr_mat[pos_i][pos_j + 1] - (cos(arg_i))*(sin(arg_j))*Corr_mat[pos_i + 1][pos_j] + (cos(arg_i))*(cos(arg_j))*Corr_mat[pos_i + 1][pos_j + 1]

    # square difference between momentum quadratures
    p_minus_prime_2 = 1/2*(p_i_prime_2 + p_j_prime_2 - 2*p_i_p_j_prime)

    # quantum phase synchronization value
    return 1/2/p_minus_prime_2

def sync_phase_rot(mat_Corr, pos_i, pos_j, mode_i, mode_j):
    """Function to calculate quantum phase synchronization between two modes given the correlation matrix of their quadratures.

    Parameters
    ----------
    mat_Corr : list
        Matrix containing all correlations between quadratures.

    pos_i : *int*
        Position of ith mode in the correlation matrix.

    pos_j : *int*
        Position of jth mode in the correlation matrix.

    mode_i : np.complex
        Value of the ith mode.

    mode_j : np.complex
        Value of the jth mode.

    Returns
    -------
    qs_p : float
        Quantum phase synchronization value.
    """

    # arguments
    arg_i = angle(mode_i)
    arg_j = angle(mode_j)

    # rotated quadratures
    return cos(arg_i)*cos(arg_j)*mat_Corr[pos_i + 1][pos_j + 1] - cos(arg_i)*sin(arg_j)*mat_Corr[pos_i + 1][pos_j] - sin(arg_i)*cos(arg_j)*mat_Corr[pos_i][pos_j + 1] + sin(arg_i)*sin(arg_j)*mat_Corr[pos_i][pos_j]