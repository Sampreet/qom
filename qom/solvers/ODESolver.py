#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to solve ordinary differential equations."""

__name__    = 'qom.solvers.ODESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-05-19'

# dependencies
from typing import Union
import copy
import logging
import numpy as np
import scipy.integrate as si

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]

# TODO: Validate parameters.

class ODESolver():
    r"""Class to solve ordinary differential equations.

    Initializes `func`, `iv`, and `c` properties.

    Parameters
    ----------
    params : dict
        Parameters for the solver.
    func : function
        Set of ODEs returning rate equations of the input variables.
    v : list or np.matrix or np.ndarray
        Values of the last iteration.
    c : list or np.matrix or np.ndarray, optional
        Constants for the function.
    method : str, optional
        Method used to solve the ODEs:
            'BDF': :class:`scipy.integrate.BDF`.
            'DOP853': :class:`scipy.integrate.DOP853`.
            'LSODA': :class:`scipy.integrate.LSODA`.
            'ode': :class:`scipy.integrate.ode`.
            'Radau': :class:`scipy.integrate.Radau`.
            'RK23': :class:`scipy.integrate.RK23`.
            'RK45': :class:`scipy.integrate.RK45` (default).
    """

    # attributes
    code = 'ode'
    name = 'Ordinary Differential Equations Solver'
    new_APIs = ['BDF', 'DOP853', 'LSODA', 'Radau', 'RK23', 'RK45']
    old_APIs = ['ode']

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
    def integrator(self):
        """object: Integrator object to solve the ODE."""

        return self.__integrator
    
    @integrator.setter
    def integrator(self, integrator):
        self.__integrator = integrator

    @property
    def v(self):
        """list or np.matrix or np.ndarray: Values of the last iteration."""

        return self.__v
    
    @v.setter
    def v(self, v):
        self.__v = v

    def __init__(self, params, func, iv, c=None, method='RK45'):
        """Class constructor for ODESolver."""

        # set parameters
        self.params = {
            'show_progress': params.get('show_progress', False),
            'method': params.get('method', method),
            'value_type': params.get('value_type', 'complex')
        }

        # set properties
        self.func = func
        self.v = copy.deepcopy(iv)
        self.c = copy.deepcopy(c)

    def set_func_params(self, c):
        """Method to update the parameters for the function.

        Parameters
        ----------
        c : list or np.matrix or np.ndarray
            Constants for the function.  
        """

        # update constants
        self.c = copy.deepcopy(c)

        # old API method
        if self.params['method'] == 'ode':
            self.integrator.set_f_params(c)

    def set_integrator_params(self, T, value_type='complex'):
        """Method to set the parameters for the integrator.

        Parameters
        ----------
        T : list
            Times at which values are calculated.
        value_type : str, optional
            Type of values of the function variables. Required for method "ode" method. Options are:
                'real': Real-valued variables.
                'complex': Complex-valued variables.
        """

        # extract frequently used variables
        method = self.params['method']
        value_type = self.params['value_type']

        # check method
        if method not in self.new_APIs:
            # FORTRAN-based old API method of scipy.integrate
            if method == 'ode':
                # get integrator
                self.integrator = si.ode(self.func)

                # for complex ode solver
                if value_type.find('complex') != -1:
                    self.integrator.set_integrator('zvode')
                    
                # set initial values and constants
                self.integrator.set_initial_value(self.v, T[0])

                # set constants
                if self.c is not None:
                    self.integrator.set_f_params(self.c)
            # default to RK45
            else:
                self.method = 'RK45'

    def step(self, t_e, t_s=0):
        """Method to perform one step of the integration.

        Parameters
        ----------
        t_e : float
            Ending point of the integration.
        t_s : float, optional
            Starting point of the integration.

        Returns
        -------
        v : list
            Values of the integrated variables at the end time.
        """

        # extract frequently used variables
        method = self.params['method']

        # new API methods
        if method in self.new_APIs:
            # solve
            _sols = si.solve_ivp(self.func, (t_s, t_e), self.v, method=method, args=(self.c, ) if self.c is not None else None)

            # update initial values
            self.v = [y[-1] for y in _sols.y]

            # extract attributes
            v = [y[-1] for y in _sols.y]
        # old API method
        else:
            v = self.integrator.integrate(t_e).tolist()

        return v

    def solve(self, T, c_func=None):
        """Method to solve a complete integration.

        Parameters
        ----------
        T : list
            Times at which the values are calculated.
        c_func : function
            Function to obtain the time-dependent constants of the integration.

        Returns
        -------
        vs : list
            Lists of values of the variable for all times.
        """
        # extract frequently used variables
        show_progress = self.params['show_progress']
        method = self.params['method']
        t_dim = len(T)

        # initialize lists
        vs = [copy.deepcopy(self.v)]

        # for each time step, calculate the integration values
        for i in range(1, t_dim):
            # update progress
            progress = float(i - 1)/float(t_dim - 1) * 100
            # display progress
            if show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Integrating (scipy.integrate.{method}): Progress = {progress:3.2f}'.format(method=method, progress=progress))

            # update constants
            if c_func is not None:
                self.set_func_params(c_func(i))
            else:
                self.set_func_params(self.c)

            # step
            _v = self.step(T[i], T[i - 1])

            # update log
            logger.debug('t = {}\tv = {}'.format(T[i], _v))

            # update lists
            vs.append(_v)

        return vs
