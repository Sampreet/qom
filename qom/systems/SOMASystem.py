#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface an array of single-optomechanical systems."""

__name__    = 'qom.systems.SOMASystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-15'
__updated__ = '2021-08-18'

# dependencies
from decimal import Decimal
import logging
import numpy as np
import scipy.fft as sf

# qom modules
from .BaseSystem import BaseSystem
from ..solvers import ODESolver

# module logger
logger = logging.getLogger(__name__)

class SOMASystem(BaseSystem):
    """Class to interface an array of single-optomechanical systems.
        
    Parameters
    ----------
    params : dict
        Parameters for the system.

    .. note:: All the options defined in ``params`` supersede individual function arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options. Additionally, the following keys are supported:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "t_div"             (*int*) Number of divisions in the time axis.
        ==================  ====================================================
    """

    def __init__(self, params):
        """Class constructor for SOMASystem."""

        # initialize super class
        super().__init__(params, 'soma_system', 'Array of single-optomechanical System', num_modes=4)

    def get_nlse_dynamics(self, solver_params, get_ivc, func_op_d, func_op_n, func_ode_betas=None, get_betas=None):
        """Method to obtain the solutions of the Nonlinear Schrodinger Equation (NLSE) using the Split-step Fourier Method.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver containing the keys "t_min", "t_max" and "t_dim" for the integration timescale.
        get_ivc : callable
            Function returning the initial values and constants, formatted as ``get_ivc()``. Returns values ``iv`` and ``c`` for the initial values and constants respectively.
        func_op_d : callable
            Function returning the dispersion operator ``D``, formatted as ``get_d(params, ps, x_ss)``, where ``params`` are the constant parameters of the system, ``ps`` is the frequency spectrum and ``x_ss`` is the step size of the X-axis values. Returns ``op_D``.
        func_op_n : callable
            Function returning the nonlinear operator ``N``, formatted as ``get_op_n(params, betas)``, where ``params`` are the constant parameters of the system and ``betas`` are the classical mechanical amplitudes. Returns ``op_N``.
        func_ode_betas : callable, optional
            Function returning the rates of the classical mechanical mode amplitudes for a given list of modes, formatted as ``func_ode_betas(betas, c, t)``, where ``betas`` are the mechanical modes amplitudes at time ``t`` and ``c`` is a list of the optical mode amplitudes and the constant parameters of the system. Returns the mechanical mode rates with same dimension as ``betas``.
        get_betas : callable, optional
            Function returning the classical mechanical mode amplitudes for a given list of modes, formatted as ``get_betas(betas, parms, t)``, where ``betas`` are the mechanical modes amplitudes at time ``t`` and ``params`` are the constant parameters of the system. Returns the mechanical modes with same dimension as ``betas``.

        Returns
        -------
        Modes : list
            Calculated solutions.
        X : list
            List of X-axis values of the system.
        T : list
            Times at which the solutions are obtainted.
        """

        # validate parameters
        for key in ['t_min', 't_max', 't_dim']:
            assert key in solver_params, 'Parameter ``params`` should contain key "{}" for looper parameters'.format(key)
        assert func_ode_betas is not None or get_betas is not None, 'Either of the functions ``func_ode_betas`` or ``get_betas`` should be non-none'
                

        # extract frequently used variables
        t_min = np.float_(solver_params['t_min'])
        t_max = np.float_(solver_params['t_max'])
        t_dim = int(solver_params['t_dim'])
        t_div = int(solver_params.get('t_div', 100))
        x_min = np.float_(solver_params.get('x_min', -1))
        x_max = np.float_(solver_params.get('x_max', 1))
        x_dim = int(solver_params.get('x_dim', int(self.num_modes / 2)))

        # calculate times
        ts = np.linspace(t_min, t_max, t_dim)
        # truncate values
        _ss = (Decimal(str(t_max)) - Decimal(str(t_min))) / (t_dim - 1)
        _decimals = - _ss.as_tuple().exponent
        # round off and convert to list
        T = np.around(ts, _decimals).tolist()
        # steps size
        t_ss = T[1] - T[0]

        # calculate times
        _xs = np.linspace(x_min, x_max, x_dim)
        # truncate values
        _ss = (Decimal(str(x_max)) - Decimal(str(x_min))) / (x_dim - 1)
        _decimals = - _ss.as_tuple().exponent
        # round off
        xs = np.around(_xs, _decimals)
        # convert to list
        X = xs.tolist()
        # step size
        x_ss = X[1] - X[0]
        # momentum space
        ps = 2 * np.pi * xs / (xs[-1] - xs[0]) / x_ss

        # extract parameters
        iv, c = get_ivc()
        modes = iv[:self.num_modes]
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c
    
        # list
        Modes = list()
        Modes.append(np.abs(modes).tolist())

        # modes
        alphas = [modes[2 * j] for j in range(x_dim)]
        betas = [modes[2 * j + 1] for j in range(x_dim)]

        for i in range(1, (t_dim - 1) * t_div + 1):
            # update progress
            progress = float(i) / t_div / float(t_dim - 1) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Computing ({module_name}): Progress = {progress:3.2f}'.format(module_name=__name__, progress=progress))

            # frequently used variables
            _t_ss = t_ss / t_div

            # dispersion operator
            op_D = func_op_d(params, ps, x_ss)
            # nonlinear operator trapezoidal approximation
            op_N = func_op_n(params, betas)
            
            # D dt / 2
            alpha_ps = sf.fftshift(sf.fft(alphas))
            temp = np.exp(op_D * _t_ss / 2) * alpha_ps
            alphas = sf.ifft(sf.fftshift(temp))

            # N dt
            alphas = np.exp(op_N * _t_ss) * alphas
            
            # D dt / 2
            alpha_ps = sf.fftshift(sf.fft(alphas))
            temp = np.exp(op_D * _t_ss / 2) * alpha_ps
            alphas = sf.ifft(sf.fftshift(temp)).tolist()

            if func_ode_betas is not None:
                # solver for betas
                solver = ODESolver({}, func_ode_betas, betas, alphas + params, method='zvode')
                t_s = T[int(i / t_div)] + (i % t_div) * _t_ss
                betas = solver.solve(T=[t_s, t_s + _t_ss])[-1]
            else:
                # function to get betas
                betas = get_betas(alphas, params, T[int(i / t_div)] + (i % t_div) * _t_ss)
            
            # update lists
            for j in range(x_dim):
                modes[2 * j] = alphas[j]
                modes[2 * j + 1] = betas[j]
            if i % t_div == 0:
                Modes.append(modes)

        return Modes, X, T