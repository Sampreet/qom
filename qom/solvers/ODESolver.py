#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle ODE solver."""

__name__    = 'qom.solvers.ODESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-01-13'

# dependencies
from typing import Union
import logging
import numpy as np
import scipy.integrate as si

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]

# TODO: Add old API submodules in `set_integrator_params`.

class ODESolver():
    r"""Class to handle ODE solver.

    Initializes `c`, `func`, `iv`, `method` and `params` properties.

    Parameters
    ----------
    params : dict
        Parameters for the solver.
    func : function
        Set of ODEs returning rate equations of the input variables.
    iv : list or np.matrix or np.ndarray
        Initial values for the function.
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
    new_APIs = {
        'BDF': si.BDF,
        'DOP853': si.DOP853,
        'LSODA': si.LSODA,
        'Radau': si.Radau,
        'RK23': si.RK23,
        'RK45': si.RK45,
    }

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
    def iv(self):
        """list or np.matrix or np.ndarray: Initial values for the function."""

        return self.__iv
    
    @iv.setter
    def iv(self, iv):
        self.__iv = iv

    @property
    def method(self):
        """str: Method used to solve the ODEs:
            'BDF': :class:`scipy.integrate.BDF`.
            'DOP853': :class:`scipy.integrate.DOP853`.
            'LSODA': :class:`scipy.integrate.LSODA`.
            'ode': :class:`scipy.integrate.ode`.
            'Radau': :class:`scipy.integrate.Radau`.
            'RK23': :class:`scipy.integrate.RK23`.
            'RK45': :class:`scipy.integrate.RK45` (default)."""

        return self.__method
    
    @method.setter
    def method(self, method):
        self.__method = method

    @property
    def params(self):
        """dict: Parameters for the solver."""

        return self.__params
    
    @params.setter
    def params(self, params):
        self.__params = params

    def __init__(self, params, func, iv, c=None, method='RK45'):
        """Class constructor for ODESolver."""

        # set attributes
        self.params = params
        self.func = func
        self.iv = iv
        self.c = c
        self.method = method

    def set_func_params(self, c):
        """Method to update the parameters for the function.

        Parameters
        ----------
        c : list or np.matrix or np.ndarray
            Constants for the function.  
        """

        # update constants
        self.c = c

        # old API method
        if self.method == 'ode':
            self.integrator.set_f_params(c)

    def set_integrator_params(self, T, solver_type='complex'):
        """Method to set the parameters for the integrator.

        Parameters
        ----------
        T : list
            Times at which values are calculated.
        solver_type : str, optional
            Type of solver for method "ode" method:
                'real': Real-valued variables.
                'complex': Complex-valued variables.
        """

        # extract frequently used variables
        solver_type = self.params.get('type', solver_type)

        # check method
        if self.method not in self.new_APIs:
            # FORTRAN-based old API method of scipy.integrate
            if self.method == 'ode':
                # get integrator
                self.integrator = si.ode(self.func)

                # for complex ode solver
                if solver_type.find('complex') != -1:
                    self.integrator.set_integrator('zvode')
                    
                # set initial values and constants
                self.integrator.set_initial_value(self.iv, T[0])

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

        # new API methods
        if self.method in self.new_APIs:
            # solve
            _sols = si.solve_ivp(self.func, (t_s, t_e), self.iv, method=self.method, args=(self.c, ))

            # update initial values
            self.iv = [_sols.y[i][-1] for i in range(len(self.iv))]

            # extract attributes
            v = [_sols.y[i][-1] for i in range(len(self.iv))]
        # old API method
        else:
            v = self.integrator.integrate(t_e).tolist()

        return v