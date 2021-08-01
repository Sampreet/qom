#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to solve ordinary differential equations."""

__name__    = 'qom.solvers.ODESolver'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-04'
__updated__ = '2021-08-01'

# dependencies
import copy
import logging
import scipy.integrate as si

# module logger
logger = logging.getLogger(__name__)

class ODESolver():
    r"""Class to solve ordinary differential equations.

    Initializes ``integrator`` and ``T`` properties.

    Parameters
    ----------
    params : dict
        Parameters for the solver. Refer notes below for all available options.
    func : callable
        Function returning the rate equations of the input variables, formatted as ``func(t, v, c)``, where ``t`` is the time at which the integration is performed, ``v`` is a list of variables and ``c`` is a list of constants. The output should match the dimension of ``v``.
    iv : list
        Initial values for the function.
    c : list, optional
        Constants for the function.
    method : str, optional
        Method used to solve the ODEs (:class:`scipy.integrate.*`). If the method used is "ode", parameter ``integrator`` needs to be provided. Currently available Python-based methods are:
            ==========  ====================================================
            value       meaning
            ==========  ====================================================
            "BDF"       backward-differentiation formulas.
            "DOP853"    explicit Runge-Kutta method of order 8(5, 3).
            "LSODA"     Adams/BDF method with automatic stiffness detection and switching.
            "Radau"     implicit Runge-Kutta of Radau IIA family of order 5.
            "RK23"      explicit Runge-Kutta method of order 3(2).
            "RK45"      explicit Runge-Kutta method of order 5(4) (fallback).
            ==========  ====================================================
    
        Currently available FORTRAN-based are:
            ==========  ====================================================
            value       meaning
            ==========  ====================================================
            "dop853"    explicit Runge-Kutta method of order 8(5, 3).
            "dopri5"    explicit Runge-Kutta method of order 5(4).
            "lsoda"     real-valued Adams/BDF method with automatic stiffness detection and switching.
            "vode"      real-valued implicit Adams/BDF methods.
            "zvode"     complex-valued implicit Adams/BDF methods (fallback).
            ==========  ====================================================

    Notes
    -----
    The "solver" dictionary in ``params`` currently supports the following keys:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "method"            (*str*) method used to solve the ODEs. Currently available methods are "BDF", "DOP853", "dop853", "dopri5", "LSODA", "lsoda", "Radau", "RK23", "RK45" (fallback), "vode" and "zvode". 
        "show_progress"     (*bool*) option to display the progress of the integration.
        ==================  ====================================================

    .. note:: All the options defined in ``params`` supersede individual function arguments.
    """

    # attributes
    code = 'ode_solver'
    name = 'Ordinary Differential Equations Solver'
    new_methods = ['BDF', 'DOP853', 'LSODA', 'Radau', 'RK23', 'RK45']
    old_methods = ['dop853', 'dopri5', 'lsoda', 'vode', 'zvode']

    @property
    def integrator(self):
        """object: Integrator object to solve the ODE."""

        return self.__integrator
    
    @integrator.setter
    def integrator(self, integrator):
        self.__integrator = integrator

    @property
    def T(self):
        """list: Times at which values are calculated."""

        return self.__T
    
    @T.setter
    def T(self, T):
        self.__T = T

    def __init__(self, params: dict, func, iv: list, c: list=None, method: str='RK45'):
        """Class constructor for ODESolver."""

        # supersede solver parameters
        params['method'] = params.get('method', method)

        # validate parameters
        supported_methods = self.new_methods + self.old_methods
        assert method in supported_methods, 'Parameter ``method`` should assume one of {}'.format(supported_methods)

        # set attributes
        self.params = params
        self.func = func
        self.v = copy.deepcopy(iv)
        self.c = copy.deepcopy(c)

        # set properties
        if self.params['method'] in self.old_methods:
            # get integrator
            self.integrator = si.ode(self.func)

            # set integrator
            self.integrator.set_integrator(self.params['method'])
        self.T = None

    def solve(self, T: list, func_c=None):
        """Method to solve a complete integration.

        Parameters
        ----------
        T : list
            Times at which the values are calculated.
        func_c : function, optional
            Function returning the time-dependent constants of the integration, formatted as ``func_c(i)``, where ``i`` is the *i*-th step of integration.

        Returns
        -------
        vs : list
            Lists of values of the variable for all times.
        """

        # extract frequently used variables
        method = self.params['method']
        show_progress = self.params.get('show_progress', False)

        # update times
        self.T = T
        _dim = len(T)

        # update params
        if method in self.old_methods:                
            # set initial values and constants
            self.integrator.set_initial_value(self.v, self.T[0])

            # set constants
            if self.c is not None:
                self.integrator.set_f_params(self.c)

        # initialize lists
        vs = [copy.deepcopy(self.v)]

        # for each time step, calculate the integration values
        for i in range(1, _dim):
            # update progress
            progress = float(i - 1)/float(_dim - 1) * 100
            # display progress
            if show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Integrating (scipy.integrate.{method}): Progress = {progress:3.2f}'.format(method=method if method in self.new_methods else 'ode', progress=progress))

            # update constants
            self.c = func_c(i) if func_c is not None else self.c

            # step
            _v = self.step(t_e=self.T[i], t_s=self.T[i - 1])

            # update log
            logger.debug('t = {}\tv = {}'.format(self.T[i], _v))

            # update lists
            vs.append(_v)

        return vs

    def step(self, t_e: float, t_s: float=0):
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

        # old API method
        if method in self.old_methods:
            self.integrator.set_f_params(self.c)
            v = self.integrator.integrate(t_e).tolist()
        # new API methods
        else:
            # solve
            _sols = si.solve_ivp(self.func, (t_s, t_e), self.v, method=method, rtol=1e-9, atol=1e-13, args=(self.c, ) if self.c is not None else None)
            # extract final values
            v = [y[-1] for y in _sols.y]
            
        # update initial values
        self.v = copy.deepcopy(v)

        return v