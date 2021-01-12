#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to solve Heisenberg and Lyapunov equations for classical mode amplitudes and quantum correlations."""

__name__    = 'qom.solvers.HLESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-12'

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
    r"""Class to solve Heisenberg and Lyapunov equations for classical mode amplitudes and quantum correlations.

    Initializes `params` and `T` properties.

    Parameters
    ----------
    params : dict
        Parameters for the solver.
    """

    @property
    def Corrs(self):
        """dict: Lists of times and values as keys 'T' and 'V', respectively."""

        return self.__Corrs
    
    @Corrs.setter
    def Corrs(self, Corrs):
        self.__Corrs = Corrs

    @property
    def Modes(self):
        """dict: Lists of times and values as keys 'T' and 'V', respectively."""

        return self.__Modes
    
    @Modes.setter
    def Modes(self, Modes):
        self.__Modes = Modes

    @property
    def params(self):
        """dict: Parameters for the solver."""

        return self.__params
    
    @params.setter
    def params(self, params):
        self.__params = params

    @property
    def T(self):
        """list: Times at which values are calculated."""

        return self.__T
    
    @T.setter
    def T(self, T):
        self.__T = T

    @property
    def results(self):
        """dict: Lists of times and values as keys 'T' and 'V', respectively."""

        return self.__results
    
    @results.setter
    def results(self, results):
        self.__results = results

    def __init__(self, params):
        """Class constructor for HLESolver."""

        # update attributes
        self.params = params
        self.__set_times()
        self.Modes = None
        self.Corrs = None

    def __set_times(self):
        """Method to initialize the times at which values are calculated."""

        # validate parameters
        assert 'T' in self.params, 'Solver parameters should contain key `T`'
        for key in ['min', 'max']:
            assert key in self.params['T'], 'Key `T` should contain key {}'.format(key)

        # extract frequently used variable
        _T = self.params['T']
        _dim = _T.get('dim', 1001)
        
        # update dim in params
        self.params['T']['dim'] = _dim

        # calculate times
        _ts = np.linspace(_T['min'], _T['max'], _dim)
        # truncate values
        _step_size = (Decimal(str(_T['max'])) - Decimal(str(_T['min']))) / (_dim - 1)
        _decimals = - _step_size.as_tuple().exponent
        _ts = np.around(_ts, _decimals)
        # convert to list
        _ts = _ts.tolist()
        # update attribute
        self.T = _ts

    def __solve_ODEs(self, ode_func, iv, c, ode_func_corrs=None, num_modes=None, solver_method='RK45'):
        """Method to solve the ODEs.

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
        solver_method : str, optional
            Method used to solve the ODEs:
                'BDF': :class:`scipy.integrate.BDF`.
                'DOP853': :class:`scipy.integrate.DOP853`.
                'ode': :class:`scipy.integrate.ode`.
                'RK45': :class:`scipy.integrate.RK45` (default).
        """

        # validate parameters
        assert num_modes is not None if ode_func_corrs is not None else True, 'Parameter `num_modes` should be specified if `ode_func_corrs` is given'

        # extract frequently used variables
        show_progress = self.params.get('show_progress', False)
        _single_func = ode_func_corrs is None
        _len = len(self.T)

        # handle single function 
        if not _single_func:
            # update initial values and constants
            _iv_corrs = [np.real(ele) for ele in iv[num_modes:]]
            iv = [ele for ele in iv[:num_modes]]
            _c_corrs = c + iv
            
            # display initialization
            if show_progress:
                logger.info('-------------------Obtaining Modes--------------------\n')
        else:
            # display initialization
            if show_progress:
                logger.info('-------------------Obtaining Results------------------\n')

        # initialize solver
        ode_solver = ODESolver(self.params, ode_func, iv, c, solver_method)
        ode_solver.set_integrator_params(self.T, 'complex')

        # initialize lists
        _vs = [iv]

        # for each time step, calculate the integration values
        for i in range(1, _len):
            # update progress
            progress = float(i - 1)/float(_len - 1) * 100
            # display progress
            if show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Integrating (scipy.integrate.{method}): Progress = {progress:3.2f}'.format(method=solver_method, progress=progress))

            # step
            _v = ode_solver.step(self.T[i], self.T[i - 1])

            # update log
            logger.debug('t = {}\tmodes = {}'.format(self.T[i], _v))

            # update lists
            _vs.append(_v)
            
        if not _single_func:
            # update modes
            self.Modes = _vs

            # display completion
            if show_progress:
                logger.info('-------------------Modes Obtained---------------------\n')
                logger.info('-------------------Obtaining Correlations-------------\n')

            # initialize solver
            ode_solver = ODESolver(self.params, ode_func_corrs, _iv_corrs, _c_corrs, solver_method)
            ode_solver.set_integrator_params(self.T, 'real')

            self.Corrs = [_iv_corrs]

            # for each time step, calculate the integration values
            for i in range(1, _len):
                # update progress
                progress = float(i - 1)/float(_len - 1) * 100
                # display progress
                if show_progress and int(progress * 1000) % 10 == 0:
                    logger.info('Integrating (scipy.integrate.{method}): Progress = {progress:3.2f}'.format(method=solver_method, progress=progress))

                # step
                for j in range(num_modes):
                    _c_corrs[len(c) + j] = self.Modes[i - 1][j]
                ode_solver.set_func_params(_c_corrs)
                _v = ode_solver.step(self.T[i], self.T[i - 1])

                # update log
                logger.debug('t = {}\tcorrs = {}'.format(self.T[i], _v))

                # update correlations
                self.Corrs.append(np.real(_v).tolist())
                
            # update results
            self.results = {
                'T': self.T,
                'V': [self.Modes[i] + self.Corrs[i] for i in range(_len)]
            }

            # reshape correlations
            self.Corrs = [np.reshape(self.Corrs[i], (2 * num_modes, 2 * num_modes)).tolist() for i in range(_len)]
            
            # display completion
            if show_progress:
                logger.info('-------------------Correlations Obtained--------------\n')
        else:
            # update results
            self.results = {
                'T': self.T,
                'V': _vs
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
        _vs = self.results['V']

        # update correlations
        self.Corrs = [np.real(np.reshape(_vs[i][num_modes:], (2 * num_modes, 2 * num_modes))).tolist() for i in range(len(_vs))]
            
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
        _vs = self.results['V']

        # update correlations
        self.Modes = [_vs[i][:num_modes] for i in range(len(_vs))]
            
        return self.Modes

    def solve(self, ode_func, iv, c, ode_func_corrs=None, num_modes=None, solver_method='RK45', cache=True, cache_dir='data', cache_file='V', system_params=None):
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
        solver_method : str, optional
            Method used to solve the ODEs:
                'BDF': :class:`scipy.integrate.BDF`.
                'DOP853': :class:`scipy.integrate.DOP853`.
                'ode': :class:`scipy.integrate.ode`.
                'RK45': :class:`scipy.integrate.RK45` (default).
        cache : bool, optional
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
        show_progress = self.params.get('show_progress', False)

        # update directory
        cache_dir += '\\' + __name__ + '\\' + str(self.T[0]) + '_' + str(self.T[-1]) + '_' + str(len(self.T)) + '\\'
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
        
        # load results from compressed file
        if cache and os.path.isfile(cache_dir + cache_file + '.npz'):
            self.results = {
                'T': self.T,
                'V': np.load(cache_dir + cache_file + '.npz')['arr_0'].tolist()
            }

            _len = len(self.T)
            self.Modes = [self.results['V'][i][:num_modes] for i in range(_len)]
            self.Corrs = [np.real(np.reshape(self.results['V'][i][num_modes:], (2 * num_modes, 2 * num_modes))).tolist() for i in range(_len)]

            # display loaded
            if show_progress:
                logger.info('-------------------Results Loaded---------------------\n')
        else:
            # solve
            self.__solve_ODEs(ode_func, iv, c, ode_func_corrs, num_modes, solver_method)
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
            
                # display saved
                if show_progress:
                    logger.info('-------------------Results Saved----------------------\n')
