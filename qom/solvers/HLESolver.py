#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to solve Heisenberg-Langevin equations for classical modes and quantum correlations."""

__name__    = 'qom.solvers.HLESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-08'

# dependencies
from typing import Union
import logging
import numpy as np
import os

# qom modules
from qom.solvers.ODESolver import ODESolver

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]

# TODO: Add `solve_multi` for multi-system solving.

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

    def solve(self, solver_module='si', solver_type='complex', cache=False, cache_dir='data', cache_file='V', system_params=None):
        """Method to set up the integrator for the calculation.

        Parameters
        ----------
        solver_module : str, optional
            Module used to solve the ODEs:
                'si': :class:`scipy.integrate`.
        solver_type : str, optional
            Type of solver:
                'real': Real-valued variables.
                'complex': Complex-valued variables.
        cache : str, optional
            Option to cache the dynamics.
        cache_dir : str, optional
            Directory where the results are cached.
        cache_file : str, optional
            File where the results are cached.
        system_params : dict, optional
            Parameters for the system.
        """

        # extract frequently used variables
        cache = self.params.get('cache', cache)
        cache_dir = self.params.get('cache_dir', cache_dir)
        cache_file = self.params.get('cache_file', cache_file)
        _T = self.params['T']

        # update directory
        cache_dir += '\\' + __name__ + '\\' + str(_T['min']) + '_' + str(_T['max']) + '_' + str(_T['dim']) + '\\'
        # upate filename
        if cache_file == 'V' and system_params is not None:
            for key in system_params:
                cache_file += '_' + str(system_params[key])

        # convert uncompressed files to compressed ones
        if cache and os.path.isfile(cache_dir + cache_file + '.npy'):
            # load data
            _temp = np.load(cache_dir + cache_file + '.npy')
            # save to compressed file
            np.savez_compressed(cache_dir + cache_file, _temp)
        
        # load compressed file
        if cache and os.path.isfile(cache_dir + cache_file + '.npz'):
            self.results = {
                'T': self.T,
                'V': np.load(cache_dir + cache_file + '.npz')['arr_0'].tolist()
            }
        else:
            # solve
            super().solve(solver_module, solver_type)
            # save
            if cache:
                # create directories
                try:
                    os.makedirs(cache_dir)
                except FileExistsError:
                    # update log
                    logger.debug('Directory {dir_name} already exists\n'.format(dir_name=cache_dir))
                # save to compressed file
                np.savez_compressed(cache_dir + cache_file, np.array(self.results['V']))

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
            self.solve()

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
            self.solve()

        # extract frequently used variables
        _V = self.results['V']

        # extract correlations
        Corrs = list()
        for i in range(len(_V)):
            Corrs.append(np.real(np.reshape(_V[i][num_modes:], (2 * num_modes, 2 * num_modes))).tolist())
            
        return Corrs