#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle ODE solver."""

__name__    = 'qom.solvers.ODESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-11'

# dependencies
from decimal import Decimal
from typing import Union
import logging
import numpy as np
import scipy.integrate as si

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]
            
# TODO: Truncate times in `__set_times`.
# TODO: Handle other integrators in `solve`.

class ODESolver():
    r"""Class to handle ODE solver.

    Initializes `c`, `func`, `iv`, `params` and `T` properties.

    Parameters
    ----------
    func : function
        Set of ODEs returning rate equations of the input variables.
    params : dict
        Parameters for the solver.
    iv : list or np.matrix or np.ndarray
        Initial values for the function.
    c : list or np.matrix or np.ndarray, optional
        Constants for the function.
    """

    @property
    def c(self):
        """list or np.matrix or np.ndarray: Constants for the function."""

        return self.__c
    
    @c.setter
    def c(self, c):
        self.__c = c

    @property
    def func(self):
        """function: Set of ODEs returning rate equations of the input variables."""

        return self.__func
    
    @func.setter
    def func(self, func):
        self.__func = func

    @property
    def iv(self):
        """list or np.matrix or np.ndarray: Initial values for the function."""

        return self.__iv
    
    @iv.setter
    def iv(self, iv):
        self.__iv = iv

    @property
    def params(self):
        """dict: Parameters for the solver."""

        return self.__params
    
    @params.setter
    def params(self, params):
        self.__params = params

    @property
    def results(self):
        """dict: Lists of times and values as keys 'T' and 'V', respectively."""

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

    def __init__(self, func, params, iv, c=None):
        """Class constructor for ODESolver."""

        # set attributes
        self.func = func
        self.params = params
        self.__set_times()
        self.iv = iv
        self.c = c

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

    def solve(self, solver_module='si_ode', solver_type='complex'):
        """Method to set up and perform the integration.

        Parameters
        ----------
        solver_module : str, optional
            Module used to solve the ODEs:
                'si_BDF': :class:`scipy.integrate.BDF`.
                'si_DOP853': :class:`scipy.integrate.DOP853`.
                'si_ode': :class:`scipy.integrate.ode` (default). Requires `solver_type` parameter.
                'si_RK45': :class:`scipy.integrate.RK45`.
        solver_type : str, optional
            Type of solver:
                'real': Real-valued variables.
                'complex': Complex-valued variables (default).
        """

        # extract frequently used variables
        solver_module = self.params.get('module', solver_module)
        show_progress = self.params.get('show_progress', False)
        _package = solver_module[:3] if len(solver_module) >= 3 else 'si_'
        _API = solver_module[3:] if len(solver_module) > 3 else 'ode'
        _new_APIs = ['BDF', 'DOP853', 'RK45']
        _len = len(self.T)
        _new = False

        # initialize integrator
        # new API methods of scipy.integrate
        if _package.find('si_') != -1 and _API in _new_APIs:
            integrator = self.__get_integrator_si_new(solver_module)
            # flag
            _new = True
        # FORTRAN-based old API method of scipy.integrate
        else:
            _API = 'ode'
            integrator = self.__get_integrator_si_old(solver_type)

        # display initialization
        if show_progress:
            logger.info('-------------------Integrator Initialized-------------\n')

        # initialize lists
        _ts = [self.T[0]]
        _vs = [self.iv]

        # for each time step, calculate the integration values
        for i in range(1, _len):
            # update progress
            progress = float(i - 1)/float(_len - 1) * 100
            # display progress
            if show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Integrating (scipy.integrate.{API}): Progress = {progress:3.2f}'.format(API=_API, progress=progress))

            # integrate
            # new API methods
            if _new:
                integrator.step()
                t = integrator.t
                v = integrator.y
            # old API method
            else:
                t = self.T[i]
                v = integrator.integrate(t)

            # update log
            logger.debug('t = {}\tv = {}'.format(t, v))

            # update lists
            _ts.append(t)
            _vs.append(v)

        # update attributes
        self.results = {
            'T': _ts,
            'V': _vs
        }
            
        # display completion
        if show_progress:
            logger.info('-------------------Integration Complete---------------\n')

    def __get_integrator_si_new(self, solver_module):
        """Method to obtain the integrator :class:`scipy.integrate.*`.

        Parameters
        ----------
        solver_module : str, optional
            Module used to solve the ODEs:
                'si_BDF': :class:`scipy.integrate.BDF`.
                'si_DOP853': :class:`scipy.integrate.DOP853`.
                'si_RK45': :class:`scipy.integrate.RK45` (default).

        Returns
        -------
        integrator : :class:`scipy.integrate.*`
            Integrator for ODE.
        """

        # extract frequently used variables
        solver_module = self.params.get('module', solver_module)
        _APIs = {
            'BDF': si.BDF,
            'DOP853': si.DOP853,
            'RK45': si.RK45,
        }

        # set constants
        if self.c is not None:
            _func = lambda t, x: self.func(t, x, self.c)
        else:
            _func = self.func
            
        # get integrator
        integrator = _APIs[solver_module[3:]](_func, self.T[0], self.iv, self.T[-1], max_step=self.T[1] - self.T[0])

        return integrator

    def __get_integrator_si_old(self, solver_type='complex'):
        """Method to set up the integrator :class:`scipy.integrate.ode`.

        Parameters
        ----------
        solver_type : str, optional
            Type of solver:
                'real': Real-valued variables.
                'complex': Complex-valued variables.

        Returns
        -------
        integrator : :class:`scipy.integrate.*`
            Integrator for ODE.
        """

        # extract frequently used variables
        solver_type = self.params.get('type', solver_type)
            
        # get integrator
        integrator = si.ode(self.func)

        # for complex ode solver
        if solver_type.find('complex') != -1:
            integrator.set_integrator('zvode')
            
        # set initial values and constants
        integrator.set_initial_value(self.iv, self.T[0])

        # set constants
        if self.c is not None:
            integrator.set_f_params(self.c)

        return integrator