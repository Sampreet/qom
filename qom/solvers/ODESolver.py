#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle ODE solver."""

__name__    = 'qom.solvers.ODESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-05'

# dependencies
from typing import Union
import logging
import numpy as np
import scipy.integrate as si

# module logger
logger = logging.getLogger(__name__)

# data types
t_array = Union[list, np.matrix, np.ndarray]

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

        # calculate times
        self.T = np.linspace(_T['min'], _T['max'], _T.get('dim', 1001)).tolist()

    def solve(self, solver_module='si', solver_type='complex'):
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
        """

        # extract frequently used variables
        solver_module = self.params.get('module', solver_module)
        solver_type = self.params.get('type', solver_type)
        _len = len(self.T)

        # initialize integrator
        if solver_module == 'si':
            integrator = si.ode(self.func)
            # for complex ode solver
            if solver_type.find('complex') != -1:
                integrator.set_integrator('zvode')
                
            # set initial values and constants
            integrator.set_initial_value(self.iv, self.T[0])

            # set constants
            if self.c is not None:
                integrator.set_f_params(self.c)
        else:
            # TODO: Handle other integrators.
            integrator = None

        # initialize lists
        _ts = [self.T[0]]
        _vs = [self.iv]

        # for each time step, calculate the integration values
        for i in range(1, _len):
            # update progress
            progress = float(i - 1)/float(_len - 1) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the values: Progress = {progress:3.2f}'.format(progress=progress))

            # integrate
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