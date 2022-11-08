#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to solve Heisenberg-Langevin equations for classical mode amplitudes and quantum correlations."""

__name__    = 'qom.solvers.HLESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2022-09-18'

# dependencies
from decimal import Decimal
import logging
import numpy as np
import os

# qom modules
from .ODESolver import ODESolver

# module logger
logger = logging.getLogger(__name__)

# TODO: Add `solve_multi` for multi-system solving.

class HLESolver():
    r"""Class to solve Heisenberg-Langevin equations for classical mode amplitudes and quantum correlations.

    Initializes ``Corrs``, ``cb_update``, ``Modes``, ``params``, ``results`` and ``T``.

    Parameters
    ----------
    params : dict
        Parameters for the solver. Refer notes below for all available options. Required options are:
            ==========  ====================================================
            key         value
            ==========  ====================================================
            "t_min"     (*float*) minimum time at which integration starts.
            "t_max"     (*float*) maximum time at which integration stops.
            "t_dim"     (*int*) number of values from "t_max" to "t_min", both inclusive.
            ==========  ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    Notes
    -----
    The "solver" dictionary in ``params`` currently supports the following keys:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "cache"             (*bool*) option to cache the time series.
        "cache_dir"         (*str*) directory where the time series is cached.
        "cache_file"        (*str*) filename of the cached time series.
        "show_progress"     (*bool*) option to display the progress of the integration.
        "t_min"             (*float*) minimum time at which integration starts.
        "t_max"             (*float*) maximum time at which integration stops.
        "t_dim"             (*int*) number of values from "t_max" to "t_min", both inclusive.
        ==================  ====================================================

    .. note:: All the options defined in ``params`` supersede individual function arguments.
    """

    # attributes
    code = 'HLESolver'
    name = 'Heisenberg-Langevin Equations Solver'
    ui_params = {
        'method': ODESolver.new_methods + ODESolver.old_methods,
        't_min': 0.0,
        't_max': 1000.0,
        't_dim': 10001
    }

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
    def results(self):
        """dict: Lists of times (key "T") and values (key "V")."""

        return self.__results
    
    @results.setter
    def results(self, results):
        self.__results = results

    @property
    def T(self):
        """list: Times at which values are calculated."""

        return self.__T
    
    @T.setter
    def T(self, T):
        self.__T = T

    def __init__(self, params: dict, cb_update=None):
        """Class constructor for HLESolver."""

        # validate parameters
        for key in ['t_min', 't_max', 't_dim']:
            if key not in params:
                logger.info('``params`` does not contain "{}", using {}\n'.format(key, self.ui_params[key]))

        # set attributes
        self.params = params
        self.cb_update = cb_update

        # set properties
        self.Corrs = None
        self.Modes = None
        self.results = None
        self.T = self._get_times()

    def _get_num_modes(self, dim):
        """Method to detect number of modes of the system.

        Parameters
        ----------
        dim : int
            Dimension of values at any point of time.
        
        Returns
        -------
        num_modes : int
            Number of modes of the system.
        """

        # natural root of the quadratic equation (4 * n**2 + n - dim = 0)
        num_modes = int((- 1 + np.sqrt(1 + 16 * dim)) / 8)

        return num_modes

    def _get_times(self):
        """Method to initialize the times at which values are calculated.
        
        Returns
        -------
        T : list
            Times at which values are calculated.
        """

        # extract frequently used variables
        t_min = np.float_(self.params.get('t_min', self.ui_params['t_min']))
        t_max = np.float_(self.params.get('t_max', self.ui_params['t_max']))
        t_dim = int(self.params.get('t_dim', self.ui_params['t_dim']))

        # calculate times
        _ts = np.linspace(t_min, t_max, t_dim)
        # truncate values
        _step_size = (Decimal(str(t_max)) - Decimal(str(t_min))) / (t_dim - 1)
        _decimals = - _step_size.as_tuple().exponent
        # round off and convert to list
        T = np.around(_ts, _decimals).tolist()
        
        return T

    def _set_results(self, func_ode, iv, c, func_ode_corrs, num_modes, method):
        """Method to solve the ODEs and update the results.

        Parameters
        ----------
        func_ode : callable
            Function returning the rate equations of the classical mode amplitudes and quantum correlations, formatted as ``func_ode(t, v, c)``, where ``t`` is the time at which the integration is performed, ``v`` is a list of the amplitudes and fluctuations and ``c`` is a list of constant parameters. The output should match the dimension of ``v``. If ``func_ode_corrs`` parameter is given, this function is treated as the function for the modes only.
        iv : list
            Initial values for the function.
        c : list
            Constants for the function.
        func_ode_corrs : callable
            Function returning the rate equations of the quantum correlations. It follows the same formatting as ``func_ode``.
        num_modes : int
            Number of modes of the system.
        method : str, optional
            Method used to solve the ODEs. Currently available methods are "BDF", "DOP853", "dop853", "dopri5", "LSODA", "lsoda", "Radau", "RK23", "RK45" (fallback), "vode" and "zvode". Refer :class:`qom.solvers.ODESolver` for more details on supported methods.
        """

        # extract frequently used variables
        show_progress = self.params.get('show_progress', False)
        single_func = func_ode_corrs is None

        # solve ODE
        ode_solver = ODESolver(params=self.params, func=func_ode, iv=iv, c=c, method=method, cb_update=self.cb_update)
        vs = ode_solver.solve(self.T)
            
        # handle single function 
        if not single_func:
            # update modes
            self.Modes = vs

            # display completion
            if show_progress:
                _status = '------------------------------------------Modes Obtained'
                logger.info(_status + '\t\n')
                if self.cb_update is not None:
                    self.cb_update(status=_status, progress=None, reset=True)

            # update initial values and constants
            iv_corrs = [np.real(ele) for ele in iv[num_modes:]]
            iv_modes = [ele for ele in iv[:num_modes]]
            c_corrs = c + iv_modes
            
            # function for variable constants 
            def func_c(i):
                """Function to update the constants of the integration.
                
                Returns
                -------
                i : int
                    Index of the element in ``T``.
                
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
            ode_solver = ODESolver(params=self.params, func=func_ode_corrs, iv=iv_corrs, c=c_corrs, method=method, cb_update=self.cb_update)
            self.Corrs = ode_solver.solve(func_c=func_c)
                
            # update results
            self.results = {
                'T': self.T,
                'V': [self.Modes[i] + self.Corrs[i] for i in range(len(self.T))]
            }

            # reshape correlations
            self.Corrs = [np.reshape(corrs, (2 * num_modes, 2 * num_modes)).tolist() for corrs in self.Corrs]
            
            # display completion
            if show_progress:
                _status = '-----------------------------------Correlations Obtained'
                logger.info(_status + '\t\n')
                if self.cb_update is not None:
                    self.cb_update(status=_status, progress=None, reset=True)
        else:
            # update results
            self.results = {
                'T': self.T,
                'V': vs
            }

            # display completion
            if show_progress:
                _status = '----------------------------------------Results Obtained'
                logger.info(_status + '\t\n')
                if self.cb_update is not None:
                    self.cb_update(status=_status, progress=None, reset=True)

    def get_Corrs(self, num_modes=None):
        """Method to obtain the quantum correlations.

        Parameters
        ----------
        num_modes : int, optional
            Number of classical modes.
        
        Returns
        -------
        Corrs : list
            All the correlations calculated at all times.
        """

        # validate call
        assert self.results.get('V', None) is not None, 'ODEs not solved, try calling the ``solve`` method first'

        # results loaded or solved using single ODE function
        if self.Corrs is not None:
            # get correlations
            return self.Corrs

        # detect number of modes if not given
        if num_modes is None:
            num_modes = self._get_num_modes(dim=len(self.results['V'][0]))

        # update correlations
        if len(self.results['V'][0]) > num_modes:
            self.Corrs = [np.real(np.reshape(vs[num_modes:], (2 * num_modes, 2 * num_modes))).tolist() for vs in self.results['V']]
        else:
            self.Corrs = None
            
        return self.Corrs
    
    def get_Modes(self, num_modes=None):
        """Method to obtain the classical mode amplitudes.

        Parameters
        ----------
        num_modes : int, optional
            Number of classical modes.
        
        Returns
        -------
        Modes : list
            All the modes calculated at all times.
        """

        # validate call
        assert self.results.get('V', None) is not None, 'ODEs not solved, try calling the ``solve`` method first'

        # results loaded or solved using single ODE function
        if self.Modes is not None:
            # get modes
            return self.Modes

        # detect number of modes if not given
        if num_modes is None:
            num_modes = self._get_num_modes(dim=len(self.results['V'][0]))

        # update correlations
        self.Modes = [vs[:num_modes] for vs in self.results['V']]
            
        return self.Modes

    def solve(self, func_ode, iv: list, c: list=list(), func_ode_corrs=None, num_modes: int=None, method: str='RK45', cache: bool=False, cache_dir: str='data', cache_file: str='V'):
        """Method to obtain the solutions of the ODEs.

        Parameters
        ----------
        func_ode : function
            Function returning the rate equations of the classical mode amplitudes and quantum correlations, formatted as ``func_ode(t, v, c)``, where ``t`` is the time at which the integration is performed, ``v`` is a list of the amplitudes and fluctuations and ``c`` is a list of constant parameters. The output should match the dimension of ``v``. If ``func_ode_corrs`` parameter is given, this function is treated as the function for the modes only.
        iv : list
            Initial values for the function.
        c : list, optional
            Constants for the function.
        func_ode_corrs : callable, optional
            Function returning the rate equations of the quantum correlations. It follows the same formatting as ``func_ode``.
        num_modes : int, optional
            Number of modes of the system.
        method : str, optional
            Method used to solve the ODEs. Currently available methods are "BDF", "DOP853", "dop853", "dopri5", "LSODA", "lsoda", "Radau", "RK23", "RK45" (fallback), "vode" and "zvode". Refer :class:`qom.solvers.ODESolver` for more details on supported methods.
        cache : bool, optional
            Option to cache the time series.
        cache_dir : str, optional
            Directory where the time series is cached.
        cache_file : str, optional
            Filename of the cached time series.

        Returns
        -------
        results : dict
            Times and calculated values.
        """

        # supersede solver parameters
        method = self.params.get('method', method)
        cache = self.params.get('cache', cache)
        cache_dir = self.params.get('cache_dir', cache_dir)
        cache_file = self.params.get('cache_file', cache_file)

        # validate parameters
        if func_ode_corrs is not None and num_modes is None:
            num_modes = self._get_num_modes(dim=len(iv))

        # extract frequently used variables
        show_progress = self.params.get('show_progress', False)
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

            # display loaded
            if show_progress:
                _status = '------------------------------------------Results Loaded'
                logger.info(_status + '\t\n')
                if self.cb_update is not None:
                    self.cb_update(status=_status, progress=None, reset=True)
        else:
            # solve
            self._set_results(func_ode=func_ode, iv=iv, c=c, func_ode_corrs=func_ode_corrs, num_modes=num_modes, method=method)
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
                    _status = '-------------------------------------------Results Saved'
                    logger.info(_status + '\t\n')
                    if self.cb_update is not None:
                        self.cb_update(status=_status, progress=None, reset=True)

        return self.results