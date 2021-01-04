#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to solve Heisenberg-Langevin equations for classical modes and quantum correlations."""

__name__    = 'qom.solvers.HLESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-04'

# dependencies
from typing import Union
import logging
import numpy as np

# qom modules
from qom.solvers.ODESolver import ODESolver

# module logger
logger = logging.getLogger(__name__)

# data types
t_array = Union[list, np.matrix, np.ndarray]

class HLESolver(ODESolver):
    r"""Class to solve Heisenberg-Langevin equations for classical modes and quantum correlations.

    Inherits :class:`qom.solvers.ODESolver`

    Initializes `c`, `func`, `iv`, `params` and `T` properties.

    Parameters
    ----------
    func : function
        Set of ODEs as rate equations of the variables.
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

    def get_modes(self):
        """Method to obtain the classical modes.
        
        Returns
        -------
        modes : list
            Values of the modes calculated.
        """

        # validate parameters
        assert 'num_modes' in self.params, 'Solver parameters should contain key `num_modes` for number of modes.'

        # ODE not solved
        if self.results.get('V', None) is None:
            # solve and update results
            super().solve()

        # extract frequently used variables
        _V = self.results['V']
        _num_modes = self.params['num_modes']

        # get modes
        modes = list()
        for i in range(len(_V)):
            modes.append(_V[i][:_num_modes])
            
        return modes

    def get_corrs(self):
        """Method to obtain the quantum correlations.
        
        Returns
        -------
        corrs : list
            Values of the correlations calculated.
        """

        # validate parameters
        assert 'num_modes' in self.params, 'Solver parameters should contain key `num_modes` for number of modes.'

        # ODE not solved
        if self.results.get('V', None) is None:
            # solve and update results
            super().solve()

        # extract frequently used variables
        _V = self.results['V']
        _num_modes = self.params['num_modes']

        # extract correlations
        corrs = list()
        for i in range(len(_V)):
            corrs.append(np.real(np.reshape(_V[i][_num_modes:], (2 * _num_modes, 2 * _num_modes))).tolist())
            
        return corrs