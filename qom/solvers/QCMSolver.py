#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle quantum correlation measure solver."""

__name__    = 'qom.solvers.QCMSolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-04'

# dependencies
from typing import Union
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# data types
t_array = Union[list, np.matrix, np.ndarray]

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

    def get_sync_complete(self, i_mode_i, i_mode_j):
        """Method to obtain the quantum complete synchronization measure between two modes.

        Parameters
        ----------
        i_mode_i : int
            Index of ith mode.
        i_mode_j : int
            Index of jth mode.

        Returns
        -------
        S_C : float
            Quantum complete synchronization measure.
        """

        # frequently used variables
        pos_i = 2 * i_mode_i
        pos_j = 2 * i_mode_j

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

    def get_sync_phase(self, i_mode_i, i_mode_j):
        """Method to obtain the quantum phase synchronization measure between two modes.

        Parameters
        ----------
        i_mode_i : int
            Index of ith mode.
        i_mode_j : int
            Index of jth mode.

        Returns
        -------
        S_C : float
            Quantum phase synchronization measure.
        """

        # frequently used variables
        pos_i = 2 * i_mode_i
        pos_j = 2 * i_mode_j

        # arguments
        arg_i = np.angle(self.modes[i_mode_i])
        arg_j = np.angle(self.modes[i_mode_j])
        
        # transformation for ith mode momentum quadrature
        p_i_prime_2 = (np.sin(arg_i))**2 * self.corrs[pos_i][pos_i] - (np.sin(arg_i)) * (np.cos(arg_i)) * self.corrs[pos_i][pos_i + 1] - (np.cos(arg_i)) * (np.sin(arg_i)) * self.corrs[pos_i + 1][pos_i] + (np.cos(arg_i))**2 * self.corrs[pos_i + 1][pos_i + 1] 

        # transformation for jth mode momentum quadrature
        p_j_prime_2 = (np.sin(arg_j))**2 * self.corrs[pos_j][pos_j] - (np.sin(arg_j)) * (np.cos(arg_j)) * self.corrs[pos_j][pos_j + 1] - (np.cos(arg_j)) * (np.sin(arg_j)) * self.corrs[pos_j + 1][pos_j] + (np.cos(arg_j))**2 * self.corrs[pos_j + 1][pos_j + 1]

        # transformation for intermode momentum quadratures
        p_i_p_j_prime = (np.sin(arg_i)) * (np.sin(arg_j)) * self.corrs[pos_i][pos_j] - (np.sin(arg_i)) * (np.cos(arg_j)) * self.corrs[pos_i][pos_j + 1] - (np.cos(arg_i)) * (np.sin(arg_j)) * self.corrs[pos_i + 1][pos_j] + (np.cos(arg_i)) * (np.cos(arg_j)) * self.corrs[pos_i + 1][pos_j + 1]

        # square difference between momentum quadratures
        p_minus_prime_2 = 1 / 2 * (p_i_prime_2 + p_j_prime_2 - 2 * p_i_p_j_prime)

        # quantum phase synchronization value
        return 1 / 2 / p_minus_prime_2