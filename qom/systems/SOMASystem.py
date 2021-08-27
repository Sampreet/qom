#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface an array of single-optomechanical systems."""

__name__    = 'qom.systems.SOMASystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-15'
__updated__ = '2021-08-28'

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
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined in ``params`` supersede individual function arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options. Additionally, the following keys are supported:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "t_div"             (*int*) Number of divisions in the time axis.
        "t_mode"            (*str*) Type of modes, "optical" (default) or "mechanical" for which the dynamics are calculated.
        ==================  ====================================================

    Some functions require one or more of the following predefined functions to work properly. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options. Additionally, the following functions are supported:
        ======================  ================================================
        function                purpose
        ======================  ================================================
        get_op_d                Function returning the dispersion operator ``D``, formatted as ``get_op_d(params, ps, x_ss)``, where ``params`` are the constant parameters of the system, ``ps`` is the frequency spectrum and ``x_ss`` is the step size of the X-axis values. Returns ``op_D``.
        get_op_n                Function returning the nonlinear operator ``N``, formatted as ``get_op_n(params, betas)``, where ``params`` are the constant parameters of the system and ``betas`` are the classical mechanical amplitudes. Returns ``op_N``.
        get_beta_rates          Function returning the rates of the classical mechanical mode amplitudes for a given list of modes, formatted as ``get_beta_rates(betas, c, t)``, where ``betas`` are the mechanical modes amplitudes at time ``t`` and ``c`` is a list of the optical mode amplitudes and the constant parameters of the system. Returns the mechanical mode rates with same dimension as ``betas``.
        get_betas               Function returning the classical mechanical mode amplitudes for a given list of modes, formatted as ``get_betas(betas, parms, t)``, where ``betas`` are the mechanical modes amplitudes at time ``t`` and ``params`` are the constant parameters of the system. Returns the mechanical modes with same dimension as ``betas``.
        ======================  ================================================
    """

    def __init__(self, params, cb_update=None):
        """Class constructor for SOMASystem."""

        # initialize super class
        super().__init__(params=params, code='soma_system', name='Array of single-optomechanical System', num_modes=4, cb_update=cb_update)

        # update attributes
        self.required_funcs.update({
            'get_mode_amplitude_dynamics': ['get_mode_rates', 'get_ivc'],
            'get_nlse_dynamics': ['get_ivc', 'get_op_d', 'get_op_n']
        })

    def get_mode_amplitude_dynamics(self, solver_params, plot=False, plotter_params=dict()):
        """Method to obtain the dynamics of the optical modes by solving the semi-classical equations of motion.

        Requires ``get_mode_rates`` and ``get_ivc`` function for the 

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver containing the keys "t_min", "t_max" and "t_dim" for the integration timescale.
        
        Returns
        -------
        amps : list
            Required mode amplitudes at every point of time.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_mode_amplitude_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # extract frequently used variables
        _N = int(self.num_modes / 2)
        _t_mode = solver_params.get('t_mode', 'optical')

        def get_ivc():
            """Function to get the initial values of the modes and the constant parameters of the system."""
            # get initial values
            iv, c = self.get_ivc()
            # truncate modes
            iv_modes = iv[:self.num_modes]
            # extract constant parameters
            if c is not None and len(c) > 4 * self.num_modes**2:
                c_modes = c[4 * self.num_modes**2:]
            else:
                c_modes = c if c is not None else list()

            return iv_modes, c_modes

        # get modes and times
        Modes, _, T = self.get_modes_corrs_dynamics(solver_params=solver_params)

        # extract required modes
        amps = [[np.linalg.norm(modes[2 * j + (1 if _t_mode == 'mechanical' else 0)]) for j in range(int(len(modes) / 2))] for modes in Modes]

        # get positions
        X = np.linspace(0, _N - 1, _N).tolist()

        if plot:
            self.plot_dynamics(plotter_params=plotter_params, V=amps, T=T, X=X)

        return amps, T, X

    def get_nlse_dynamics(self, solver_params):
        """Method to obtain the solutions of the Nonlinear Schrodinger Equation (NLSE) using the Split-step Fourier Method.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver containing the keys "t_min", "t_max" and "t_dim" for the integration timescale.

        Returns
        -------
        Modes : list
            Calculated solutions.
        X : list
            List of X-axis values of the system.
        T : list
            Times at which the solutions are obtainted.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_nlse_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # validate optional functions
        assert getattr(self, 'get_beta_rates', None) is not None or getattr(self, 'get_betas', None) is not None, 'Either of the functions ``get_beta_rates`` or ``get_betas`` should be non-none'

        # validate parameters
        for key in ['t_min', 't_max', 't_dim']:
            assert key in solver_params, 'Parameter ``params`` should contain key "{}" for looper parameters'.format(key)
                

        # extract frequently used variables
        num_s = int(self.num_modes / 2)
        t_min = np.float_(solver_params['t_min'])
        t_max = np.float_(solver_params['t_max'])
        t_dim = int(solver_params['t_dim'])
        t_div = int(solver_params.get('t_div', 100))
        x_min = np.float_(solver_params.get('x_min', - (num_s - 1) / 2))
        x_max = np.float_(solver_params.get('x_max', (num_s - 1) / 2))
        x_dim = int(solver_params.get('x_dim', num_s))

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
        iv, c = self.get_ivc()
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
            op_D = self.get_op_d(params, ps, x_ss)
            # nonlinear operator trapezoidal approximation
            op_N = self.get_op_n(params, betas)
            
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

            if self.get_beta_rates is not None:
                # solver for betas
                solver = ODESolver({}, self.get_beta_rates, betas, alphas + params, method='zvode')
                t_s = T[int(i / t_div)] + (i % t_div) * _t_ss
                betas = solver.solve(T=[t_s, t_s + _t_ss])[-1]
            else:
                # function to get betas
                betas = self.get_betas(alphas, params, T[int(i / t_div)] + (i % t_div) * _t_ss)
            
            # update lists
            for j in range(x_dim):
                modes[2 * j] = alphas[j]
                modes[2 * j + 1] = betas[j]
            if i % t_div == 0:
                Modes.append(modes)

        return Modes, X, T