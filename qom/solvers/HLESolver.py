#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to solve Heisenberg-Langevin equations for classical modes and quantum correlations."""

__name__    = 'qom.solvers.HLESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-06'

# dependencies
from typing import Union
import logging
import numpy as np

# qom modules
from qom.solvers.ODESolver import ODESolver

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]

# TODO: Add `solve_multi` for multi-system solving.
# TODO: Add option to save results in `solve`.

class HLESolver(ODESolver):
    r"""Class to solve Heisenberg-Langevin equations for classical mode amplitudes and quantum correlations.

    Inherits :class:`qom.solvers.ODESolver`

    Initializes `c`, `func`, `iv`, `params` and `T` properties.

    Parameters
    ----------
    func : function
        Set of ODEs returning rate equations of the input variables.
    params : dict
        Parameters for the solver.
    iv : list
        Initial values for the function.
    c : list, optional
        Constants for the function.
    """

    def __init__(self, func, params, iv, c=None):
        """Class constructor for HLESolver."""

        super().__init__(func, params, iv, c)

        # update attributes
        self.results = dict()

    def get_modes(self, num_modes):
        """Method to obtain the classical mode amplitudes.

        Parameters
        ----------
        num_modes : int
            Number of classical modes.
        
        Returns
        -------
        Modes : list
            All the modes calculated at all times.
        """

        # ODE not solved
        if self.results.get('V', None) is None:
            # solve and update results
            super().solve()

        # extract frequently used variables
        _V = self.results['V']

        # get modes
        Modes = list()
        for i in range(len(_V)):
            Modes.append(_V[i][:num_modes])
            
        return Modes

    def get_corrs(self, num_modes):
        """Method to obtain the quantum correlations.

        Parameters
        ----------
        num_modes : int
            Number of classical modes.
        
        Returns
        -------
        Corrs : list
            All the correlations calculated at all times.
        """

        # ODE not solved
        if self.results.get('V', None) is None:
            # solve and update results
            super().solve()

        # extract frequently used variables
        _V = self.results['V']

        # extract correlations
        Corrs = list()
        for i in range(len(_V)):
            Corrs.append(np.real(np.reshape(_V[i][num_modes:], (2 * num_modes, 2 * num_modes))).tolist())
            
        return Corrs