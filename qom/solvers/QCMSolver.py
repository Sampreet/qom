#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle quantum correlation measure solver."""

__name__    = 'qom.solvers.QCMSolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-12'

# dependencies
from typing import Union
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]

# TODO: Add `compute` wrapper.
# TODO: Add `get_sync_phase_rot`.
# TODO: Add `get_phase_match_*`.

class QCMSolver():
    r"""Class to handle quantum correlation measure solver.

    Initializes `corrs` and `modes` properties.

    Parameters
    ----------
    corrs : list
        Quantum correlations of the quadratures.
    modes : list
        Classical modes of the system.
    """

    @property
    def corrs(self):
        """list: Quantum correlations of the quadratures."""

        return self.__corrs
    
    @corrs.setter
    def corrs(self, corrs):
        self.__corrs = corrs

    @property
    def modes(self):
        """list: Classical modes of the system."""

        return self.__modes
    
    @modes.setter
    def modes(self, modes):
        self.__modes = modes

    def __init__(self, modes, corrs):
        """Class constructor for ODESolver."""

        # set attributes
        self.modes = modes
        self.corrs = corrs

    def get_discord(self, idx_mode_i, idx_mode_j):
        """Method to obtain Gaussian quantum discord between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        idx_mode_i : int
            Index of ith mode.
        idx_mode_j : int
            Index of jth mode.

        Returns
        -------
        D_G : float
            Gaussian quantum discord.
        """

        # symplectic invariants
        I_1, I_2, I_3, I_4 = self.__get_invariants(idx_mode_i, idx_mode_j)

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
        return self.__get_f(np.sqrt(I_2)) - self.__get_f(mu_plus) - self.__get_f(mu_minus) + self.__get_f(np.sqrt(self.__get_W(I_1, I_2, I_3, I_4)))

    def __get_invariants(self, idx_mode_i, idx_mode_j):
        """Helper function to calculate symplectic invariants for two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        idx_mode_i : int
            Index of ith mode.
        idx_mode_j : int
            Index of jth mode.

        Returns
        -------
        invariants : list
            Symplectic invariants.
        """

        # frequently used variables
        pos_i = 2 * idx_mode_i
        pos_j = 2 * idx_mode_j

        # correlation matrix of ith mode
        A = np.matrix([ [   self.corrs[pos_i][pos_i],     self.corrs[pos_i][pos_i + 1]      ],
                        [   self.corrs[pos_i + 1][pos_i], self.corrs[pos_i + 1][pos_i + 1]  ]   ])
        # correlation matrix of jth mode
        B = np.matrix([ [   self.corrs[pos_j][pos_j],     self.corrs[pos_j][pos_j + 1]      ],
                        [   self.corrs[pos_j][pos_j + 1], self.corrs[pos_j + 1][pos_j + 1]  ]   ])
        # correlation matrix of intermodes
        C = np.matrix([ [   self.corrs[pos_i][pos_j],     self.corrs[pos_i][pos_j + 1]      ],
                        [   self.corrs[pos_i + 1][pos_j], self.corrs[pos_i + 1][pos_j + 1]  ]   ])
        # correlation matrix of the modes
        self.corrs_modes = np.matrix([[   self.corrs[pos_i][pos_i],     self.corrs[pos_i][pos_i + 1],     self.corrs[pos_i][pos_j],     self.corrs[pos_i][pos_j + 1]      ],
                                    [   self.corrs[pos_i + 1][pos_i], self.corrs[pos_i + 1][pos_i + 1], self.corrs[pos_i + 1][pos_j], self.corrs[pos_i + 1][pos_j + 1]  ],
                                    [   self.corrs[pos_j][pos_i],     self.corrs[pos_j][pos_i + 1],     self.corrs[pos_j][pos_j],     self.corrs[pos_j][pos_j + 1]      ],
                                    [   self.corrs[pos_j + 1][pos_i], self.corrs[pos_j + 1][pos_i + 1], self.corrs[pos_j + 1][pos_j], self.corrs[pos_j + 1][pos_j + 1]  ]   ])

        # symplectic invariants
        return [np.linalg.det(A), np.linalg.det(B), np.linalg.det(C), np.linalg.det(self.corrs_modes)]

    def __get_f(self, x):
        """Helper function for quantum discord calculation."""

        try:
            return (x + 1 / 2) * np.log10(x + 1 / 2) - (x - 1 / 2) * np.log10(x - 1 / 2)
        except ValueError:
            logger.warning('Argument of log in f function is non-positive\n')
            return 0

    def __get_W(self, I_1, I_2, I_3, I_4):
        """Helper function for quantum discord calculation."""

        try: 
            if 4 * (I_1 * I_2 - I_4)**2 / (I_1 + 4 * I_4) / (1 + 4 * I_2) / I_3**2 <= 1.0:
                return ((2 * abs(I_3) + np.sqrt(4 * I_3**2 + (4 * I_2 - 1) * (4 * I_4 - I_1))) / (4 * I_2 - 1))**2
            return (I_1 * I_2 + I_4 - I_3**2 - np.sqrt((I_1 * I_2 + I_4 - I_3**2)**2 - 4 * I_1 * I_2 * I_4)) / 2 / I_2
        except ZeroDivisionError:
            logger.warning('Division by zero encountered in W function\n')
            return 0

    def get_elements(self, idx_mode_i, idx_mode_j):
        """Method to obtain elements of the correlation matrix.

        Parameters
        ----------
        idx_mode_i : int or list
            Index or indices of ith mode.
        idx_mode_j : int or list
            Index or indices of jth mode.

        Returns
        -------
        elements : list
            Elements of the correlation matrix.
        """
        
        # initialize lists
        elements = list()

        # handle single element
        if type(idx_mode_i) is int:
            idx_mode_i = [idx_mode_i]
        if type(idx_mode_j) is int:
            idx_mode_j = [idx_mode_j]

        # frequently used variables
        _dim = len(idx_mode_i)

        assert _dim == len(idx_mode_j), 'Keys `idx_mode_i` and `idx_mode_j` should have same shape'

        for i in range(_dim):
            # get element
            _ele = self.corrs[2 * idx_mode_i[i]][2 * idx_mode_j[i]]
            # update lists
            elements.append(_ele)

        return elements

    def get_entan(self, idx_mode_i, idx_mode_j):
        """Function to calculate quantum entanglement via logarithmic negativity between two modes given the correlation matrix of their quadratures.

        Parameters
        ----------
        idx_mode_i : int
            Index of ith mode.
        idx_mode_j : int
            Index of jth mode.

        Returns
        -------
        E_N : float
            Quantum entanglement value using logarithmic negativity.
        """

        # symplectic invariants
        I_1, I_2, I_3, I_4 = self.__get_invariants(idx_mode_i, idx_mode_j)
        
        try:
            # sum of symplectic invariants after positive partial transpose
            sigma = I_1 + I_2 - 2*I_3
            # smallest symplectic eigenvalue
            mu_minus = 1 / np.sqrt(2) * np.sqrt(sigma - np.sqrt(sigma**2 - 4 * I_4))
        except ValueError:
            logger.warning('Argument of sqrt is negative\n')
            E_N = 0

        try:
            # quantum entanglement value using logarithmic negativity
            E_N =  -1 * (np.log(2 * mu_minus))
        except ValueError:
            logger.warning('Argument of ln is non-positive\n')
            E_N = 0
        else:
            E_N = max(0, E_N)
        
        return E_N

    def get_sync_complete(self, idx_mode_i, idx_mode_j):
        """Method to obtain the quantum complete synchronization measure between two modes.

        Parameters
        ----------
        idx_mode_i : int
            Index of ith mode.
        idx_mode_j : int
            Index of jth mode.

        Returns
        -------
        S_C : float
            Quantum complete synchronization measure.
        """

        # frequently used variables
        pos_i = 2 * idx_mode_i
        pos_j = 2 * idx_mode_j

        # square difference between position quadratures
        q_minus_2 = 0.5 * (self.corrs[pos_i][pos_i] + self.corrs[pos_j][pos_j] - 2 * self.corrs[pos_i][pos_j])
        # square difference between momentum quadratures
        p_minus_2 = 0.5 * (self.corrs[pos_i + 1][pos_i + 1] + self.corrs[pos_j + 1][pos_j + 1] - 2 * self.corrs[pos_i + 1][pos_j + 1])

        try: 
            # quantum complete synchronization value
            return 1 / (q_minus_2 + p_minus_2)
        except ZeroDivisionError:
            logger.warning('Division by zero encountered in W function\n')
            return 0

    def get_sync_phase(self, idx_mode_i, idx_mode_j):
        """Method to obtain the quantum phase synchronization measure between two modes.

        Parameters
        ----------
        idx_mode_i : int
            Index of ith mode.
        idx_mode_j : int
            Index of jth mode.

        Returns
        -------
        S_C : float
            Quantum phase synchronization measure.
        """

        # arguments of the modes
        arg_i = np.angle(self.modes[idx_mode_i])
        arg_j = np.angle(self.modes[idx_mode_j])

        # frequently used variables
        pos_i = 2 * idx_mode_i
        pos_j = 2 * idx_mode_j
        cos_i = np.cos(arg_i)
        cos_j = np.cos(arg_j)
        sin_i = np.sin(arg_i)
        sin_j = np.sin(arg_j)
        
        # transformation for ith mode momentum quadrature
        p_i_prime_2 = sin_i**2 * self.corrs[pos_i][pos_i] - sin_i * cos_i * self.corrs[pos_i][pos_i + 1] - cos_i * sin_i * self.corrs[pos_i + 1][pos_i] + cos_i**2 * self.corrs[pos_i + 1][pos_i + 1] 

        # transformation for jth mode momentum quadrature
        p_j_prime_2 = sin_j**2 * self.corrs[pos_j][pos_j] - sin_j * cos_j * self.corrs[pos_j][pos_j + 1] - cos_j * sin_j * self.corrs[pos_j + 1][pos_j] + cos_j**2 * self.corrs[pos_j + 1][pos_j + 1]

        # transformation for intermode momentum quadratures
        p_i_p_j_prime = sin_i * sin_j * self.corrs[pos_i][pos_j] - sin_i * cos_j * self.corrs[pos_i][pos_j + 1] - cos_i * sin_j * self.corrs[pos_i + 1][pos_j] + cos_i * cos_j * self.corrs[pos_i + 1][pos_j + 1]

        # square difference between momentum quadratures
        p_minus_prime_2 = 1 / 2 * (p_i_prime_2 + p_j_prime_2 - 2 * p_i_p_j_prime)

        # quantum phase synchronization value
        S_C = 1 / 2 / p_minus_prime_2

        return S_C