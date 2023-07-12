#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to solve ordinary differential equations."""

__name__ = 'qom.solvers.differential'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-01-04"
__updated__ = "2023-07-12"

# dependencies
import logging
import numpy as np
import scipy.integrate as si

# qom modules
from ..io import Updater

class ODESolver():
    r"""Class to solve ordinary differential equations using :class:`scipy.integrate`.

    Initializes ``solver_methods``, ``func``, ``params``, ``integrator`` and ``updater``.

    Parameters
    ----------
    func : callable
        Function returning the rate equations of the input variables, formatted as ``func(t, v, c)``, where ``t`` is the time at which the integration is performed, ``v`` is a list of variables and ``c`` is a list of constants. The output should match the dimension of ``v``.
    params : dict
        Parameters for the solver. Refer to **Notes** below for all available options.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Notes
    -----
        The ``params`` dictionary currently supports the following keys:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the integration. Default is ``False``.
            'ode_method'        (*str*) method used to solve the ODEs. Available options are ``'BDF'``, ``'DOP853'``, ``'LSODA'``, ``'Radau'``, ``'RK23'``, ``'RK45'`` (fallback), ``'dop853'``, ``'dopri5'``, ``'lsoda'``, ``'vode'`` and ``'zvode'`` (refer to :class:`qom.solvers.ODESolver`). Default is ``'RK45'``.
            'ode_is_stiff'      (*bool*) option to select whether the integration is a stiff problem or a non-stiff one. Default is ``False``.
            'ode_atol'          (*float*) absolute tolerance of the integrator. Default is ``1e-12``.
            'ode_rtol'          (*float*) relative tolerance of the integrator. Default is ``1e-6``.
            ================    ====================================================

        Currently available Python-based methods are:
            ========    ====================================================
            value       meaning
            ========    ====================================================
            'BDF'       backward-differentiation formulas.
            'DOP853'    explicit Runge-Kutta method of order 8(5, 3).
            'LSODA'     Adams/BDF method with automatic stiffness detection and switching.
            'Radau'     implicit Runge-Kutta of Radau IIA family of order 5.
            'RK23'      explicit Runge-Kutta method of order 3(2).
            'RK45'      explicit Runge-Kutta method of order 5(4) (fallback).
            ========    ====================================================

        Currently available FORTRAN-based are:
            ========    ====================================================
            value       meaning
            ========    ====================================================
            'dop853'    explicit Runge-Kutta method of order 8(5, 3).
            'dopri5'    explicit Runge-Kutta method of order 5(4).
            'lsoda'     real-valued Adams/BDF method with automatic stiffness detection and switching.
            'vode'      real-valued implicit Adams/BDF methods.
            'zvode'     complex-valued implicit Adams/BDF methods.
            ========    ====================================================
    """

    # attributes
    name = 'ODESolver'
    """str : Name of the solver."""
    desc = "Ordinary Differential Equations Solver"
    """str : Description of the solver."""
    new_api_methods = ['BDF', 'DOP853', 'LSODA', 'Radau', 'RK23', 'RK45']
    """list : New Python-based methods availabile in :class:`scipy.integrate`."""
    old_api_methods = ['dop853', 'dopri5', 'lsoda', 'vode', 'zvode']
    """list : Old FORTRAN-based methods availabile in :class:`scipy.integrate`."""
    solver_defaults = {
        'show_progress': False,
        'ode_method': 'RK45',
        'ode_is_stiff': False,
        'ode_atol': 1e-12,
        'ode_rtol': 1e-6
    }
    """dict : Default parameters of the solver."""

    def __init__(self, func, params:dict, cb_update=None):
        """Class constructor for ODESolver."""

        # set constants
        self.scipy_methods = self.new_api_methods + self.old_api_methods
        self.func = func

        # set parameters
        self.set_params(params)

        # set integrator
        if self.params['ode_method'] in self.old_api_methods:
            self.integrator = si.ode(self.func)

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.solvers.ODESolver'),
            cb_update=cb_update
        )

    def set_params(self, params):
        """Method to set the solver parameters.
        
        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # validate parameters
        assert params.get('ode_method', self.solver_defaults['ode_method']) in self.scipy_methods, "Parameter ``'ode_method'`` should assume one of ``{}``".format(self.scipy_methods)

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

    def solve(self, T, iv, c=None, func_c=None):
        """Method to obtain the solutions of the ODE at all times.

        Parameters
        ----------
        T : numpy.ndarray
            Times at which the values are calculated.
        iv : numpy.ndarray
            Initial values for the integration.
        c : numpy.ndarray
            Constants of the integration.
        func_c : callable, optional
            Function returning the time-dependent constants of the integration, formatted as ``func_c(i)``, where ``i`` is the *i*-th step of integration.

        Returns
        -------
        vs : numpy.ndarray
            Values of the variables at all times.
        """

        # extract frequently used variables
        ode_method = self.params['ode_method']
        show_progress = self.params['show_progress']
        method_module = ode_method if ode_method in self.new_api_methods else 'ode'

        # old API methods
        if ode_method in self.old_api_methods:            
            # set integrator
            self.integrator.set_integrator(
                name=ode_method,
                atol=self.params['ode_atol'],
                rtol=self.params['ode_rtol'],
                method='bdf' if self.params['ode_is_stiff'] else 'adams'
            )    
            # set initial values and constants
            self.integrator.set_initial_value(
                y=iv,
                t=T[0]
            )
            # set constants
            self.integrator.set_f_params(c if c is not None else np.empty(0))

            # initialize values
            vs = np.zeros((len(T), len(iv)), dtype=np.float_)
            vs[0] = iv

            # for each time step, calculate the integration values
            for i in range(1, len(T)):
                # display progress
                if show_progress:
                    self.updater.update_progress(
                        pos=i,
                        dim=len(T),
                        status="-" * (6 - len(method_module)) + "Integrating (scipy.integrate." + method_module + ")",
                        reset=False
                    )
                # update constants
                if func_c is not None:
                    # old API methods
                    if self.params['ode_method'] in self.old_api_methods:
                        self.integrator.set_f_params(func_c(i))
            
                # update values
                vs[i] = self.integrator.integrate(T[i])
        # new API methods
        else:
            # display progress
            if show_progress:
                self.updater.update_progress(
                    pos=None,
                    dim=len(T),
                    status="-" * (26 - len(method_module)) + "Integrating (scipy.integrate." + method_module + ")",
                    reset=False
                )
                
            # solve
            vs = self.solve_new(
                T=T,
                iv=iv,
                c=c
            )
            
        return vs
    
    def solve_new(self, T, iv, c):
        """Method to integrate with the new API methods.

        Parameters
        ----------
        T : float
            Times at which the values are obtained.
        iv : numpy.ndarray
            Initial values of the variables.
        c : numpy.ndarray
            Constants of the integration.

        Returns
        -------
        vs : numpy.ndarray
            Values of the variables.
        """
        
        # solve
        _sols = si.solve_ivp(
            fun=self.func,
            t_span=(T[0], T[-1]),
            y0=iv,
            method=self.params['ode_method'],
            t_eval=T,
            atol=self.params['ode_atol'],
            rtol=self.params['ode_rtol'],
            args=(c, )
        )
        
        # required values
        vs = _sols.y.transpose()

        # update log
        self.updater.update_debug(
            message="t = {}\tv = {}".format(T, vs)
        )

        return vs