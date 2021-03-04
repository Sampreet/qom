#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to solve Heisenberg-Langevin equations for classical mode amplitudes and quantum correlations."""

__name__    = 'qom.solvers.HLESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-02-08'

# dependencies
from decimal import Decimal
from typing import Union
import logging
import numpy as np
import os

# qom modules
from .ODESolver import ODESolver

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]

# TODO: Add `solve_multi` for multi-system solving.

class HLESolver():
    r"""Class to solve Heisenberg-Langevin equations for classical mode amplitudes and quantum correlations.

    Initializes `T` property.

    Parameters
    ----------
    params : dict
        Parameters for the solver.
    """

    # attributes
    code = 'hle'
    name = 'Heisenberg-Langevin Equations Solver'
    methods = ODESolver.new_APIs + ODESolver.old_APIs

    @property
    def Corrs(self):
        """dict: Lists of quantum correlations at all times."""

        return self.__Corrs
    
    @Corrs.setter
    def Corrs(self, Corrs):
        self.__Corrs = Corrs

    @property
    def Modes(self):
        """dict: Lists of mode amplitudes at all times."""

        return self.__Modes
    
    @Modes.setter
    def Modes(self, Modes):
        self.__Modes = Modes

    @property
    def T(self):
        """list: Times at which values are calculated."""

        return self.__T
    
    @T.setter
    def T(self, T):
        self.__T = T

    @property
    def results(self):
        """dict: Lists of times and values as keys "T" and "V", respectively."""

        return self.__results
    
    @results.setter
    def results(self, results):
        self.__results = results

    def __init__(self, params):
        """Class constructor for HLESolver."""

        # set parameters
        self.params = {
            'show_progress': params.get('show_progress', False),
            'method': params.get('method', 'RK45'),
            'value_type': params.get('value_type', 'complex'),
            't_min': params.get('t_min', '0.0'),
            't_max': params.get('t_max', '1000.0'),
            't_dim': params.get('t_dim', '10001'),
        }

        # set properties
        self.__set_times()
        self.Modes = None
        self.Corrs = None
        self.results = None

    def __set_times(self):
        """Method to initialize the times at which values are calculated."""

        # extract frequently used variables
        t_min = np.float_(self.params['t_min'])
        t_max = np.float_(self.params['t_max'])
        t_dim = int(self.params['t_dim'])

        # calculate times
        _ts = np.linspace(t_min, t_max, t_dim)
        # truncate values
        _step_size = (Decimal(str(t_max)) - Decimal(str(t_min))) / (t_dim - 1)
        _decimals = - _step_size.as_tuple().exponent
        _ts = np.around(_ts, _decimals)
        # convert to list
        _ts = _ts.tolist()
        # update attribute
        self.T = _ts

    def __set_results(self, ode_func, iv, c, ode_func_corrs=None, num_modes=None):
        """Method to solve the ODEs and update the results.

        Parameters
        ----------
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        iv : list
            Initial values for the function.
        c : list, optional
            Constants for the function.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations. Requires `num_modes` parameter.
        num_modes : int, optional
            Number of modes of the system.
        """

        # extract frequently used variables
        show_progress = self.params['show_progress']
        single_func = ode_func_corrs is None

        # solve ODE
        ode_solver = ODESolver(self.params, ode_func, iv, c)
        ode_solver.set_integrator_params(self.T, 'complex')
        vs = ode_solver.solve(self.T)
            
        # handle single function 
        if not single_func:
            # update modes
            self.Modes = vs

            # display completion and initialization
            if show_progress:
                logger.info('-------------------Modes Obtained---------------------\n')

            # update initial values and constants
            iv_corrs = [np.real(ele) for ele in iv[num_modes:]]
            iv_modes = [ele for ele in iv[:num_modes]]
            c_corrs = c + iv_modes
            
            # function for variable constants 
            def c_func(i):
                """Function to update the constants of the integration.
                
                Returns
                -------
                i : int
                    Index of the element in `T`.
                
                Returns
                -------
                c_corrs : list
                    Updated constants.
                """
                
                # update constants
                for j in range(num_modes):
                    c_corrs[len(c) + j] = self.Modes[i - 1][j]

                return c_corrs

            # solve ODE
            ode_solver = ODESolver(self.params, ode_func_corrs, iv_corrs, c_corrs)
            ode_solver.set_integrator_params(self.T, 'real')
            self.Corrs = ode_solver.solve(self.T, c_func)
                
            # update results
            self.results = {
                'T': self.T,
                'V': [self.Modes[i] + self.Corrs[i] for i in range(len(self.T))]
            }

            # reshape correlations
            self.Corrs = [np.reshape(corrs, (2 * num_modes, 2 * num_modes)).tolist() for corrs in self.Corrs]
            
            # display completion
            if show_progress:
                logger.info('-------------------Correlations Obtained--------------\n')
        else:
            # update results
            self.results = {
                'T': self.T,
                'V': vs
            }

            # display completion
            if show_progress:
                logger.info('-------------------Results Obtained-------------------\n')

    def get_Corrs(self, num_modes):
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

        # validate call
        assert self.results.get('V', None) is not None, 'ODEs not solved, try calling the `solve` method first'

        # results loaded or solved using single ODE function
        if self.Corrs is not None:
            # get correlations
            return self.Corrs

        # extract frequently used variables
        V = self.results['V']

        # update correlations
        self.Corrs = [np.real(np.reshape(vs[num_modes:], (2 * num_modes, 2 * num_modes))).tolist() for vs in V]
            
        return self.Corrs
    
    def get_Modes(self, num_modes):
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

        # validate call
        assert self.results.get('V', None) is not None, 'ODEs not solved, try calling the `solve` method first'

        # results loaded or solved using single ODE function
        if self.Modes is not None:
            # get modes
            return self.Modes

        # extract frequently used variables
        V = self.results['V']

        # update correlations
        self.Modes = [vs[:num_modes] for vs in V]
            
        return self.Modes

    def solve(self, ode_func, iv, c=None, ode_func_corrs=None, num_modes=None, method=None, cache=True, cache_dir='data', cache_file='V'):
        """Method to obtain the solutions of the ODEs.

        Parameters
        ----------
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        iv : list
            Initial values for the function.
        c : list, optional
            Constants for the function.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations. Requires `num_modes` parameter.
        num_modes : int, optional
            Number of modes of the system.
        method : str, optional
            Method used to solve the ODEs:
                'BDF': :class:`scipy.integrate.BDF`.
                'DOP853': :class:`scipy.integrate.DOP853`.
                'LSODA': :class:`scipy.integrate.LSODA`.
                'ode': :class:`scipy.integrate.ode`.
                'Radau': :class:`scipy.integrate.Radau`.
                'RK23': :class:`scipy.integrate.RK23`.
                'RK45': :class:`scipy.integrate.RK45` (default).
        cache : bool, optional
            Option to cache the dynamics.
        cache_dir : str, optional
            Directory where the results are cached.
        cache_file : str, optional
            File where the results are cached.
        """

        # validate parameters
        assert num_modes is not None if ode_func_corrs is not None else True, 'Parameter `num_modes` should be specified if `ode_func_corrs` is given'
        assert method in self.methods if method is not None else True, 'Supported methods for complex integration are {}'.format(str(self.methods))

        # update parameters
        if method is not None:
            self.params['method'] = method

        # extract frequently used variables
        show_progress = self.params['show_progress']
        cache_path = cache_dir + '/' + cache_file

        # convert uncompressed files to compressed ones
        if cache and os.path.isfile(cache_path + '.npy'):
            # load data
            _temp = np.load(cache_path + '.npy')
            # save to compressed file
            np.savez_compressed(cache_path, _temp)
        
        # load results from compressed file
        if cache and os.path.isfile(cache_path + '.npz'):
            self.results = {
                'T': self.T,
                'V': np.load(cache_path + '.npz')['arr_0'].tolist()
            }

            # extract frequently used variables
            V = self.results['V']

            # set modes and correlations
            self.Modes = [vs[:num_modes] for vs in V]
            self.Corrs = [np.real(np.reshape(vs[num_modes:], (2 * num_modes, 2 * num_modes))).tolist() for vs in V]

            # display loaded
            if show_progress:
                logger.info('-------------------Results Loaded---------------------\n')
        else:
            # solve
            self.__set_results(ode_func, iv, c, ode_func_corrs, num_modes)
            # save
            if cache:
                # create directories
                try:
                    os.makedirs(cache_dir)
                except FileExistsError:
                    # update log
                    logger.debug('Directory {dir_name} already exists\n'.format(dir_name=cache_dir))

                # save to compressed file
                np.savez_compressed(cache_path, np.array(self.results['V']))
            
                # display saved
                if show_progress:
                    logger.info('-------------------Results Saved----------------------\n')