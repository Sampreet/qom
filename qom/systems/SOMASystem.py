#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface an array of single-optomechanical systems."""

__name__    = 'qom.systems.SOMASystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-15'
__updated__ = '2022-07-26'

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

# TODO: Implement integration in `get_lle_dynamics`.

class SOMASystem(BaseSystem):
    """Class to interface an array of single-optomechanical systems.
        
    Parameters
    ----------
    params : dict
        Parameters for the system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    References
    ----------

    .. [1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86**, 1931 (2014).

    Notes
    -----
    All the options defined in ``params`` supersede individual method arguments. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options. Additionally, the following keys are supported:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "t_div"             (*int*) Number of divisions in the time axis.
        "mode_type"         (*str*) Type of mode, "optical" (default) or "mechanical", for which the dynamics are calculated.
        ==================  ====================================================

    Some functions require one or more of the following predefined functions to work properly. Refer :class:`qom.systems.BaseSystem` for a complete list of supported options. Additionally, the following functions are supported:
        ======================  ================================================
        function                purpose
        ======================  ================================================
        get_op_d                function to obtain the dispersion operator ``D``, formatted as ``get_op_d(params, ps, x_ss)``, where ``params`` are the constant parameters of the system, ``ps`` is the frequency spectrum and ``x_ss`` is the step size of the X-axis values. Returns ``op_D``.
        get_op_n                function to obtain the nonlinear operator ``N``, formatted as ``get_op_n(params, betas)``, where ``params`` are the constant parameters of the system and ``betas`` are the classical mechanical amplitudes. Returns ``op_N``.
        get_beta_rates          function to obtain the rates of the classical mechanical mode amplitudes for a given list of modes, formatted as ``get_beta_rates(betas, c, t)``, where ``betas`` are the mechanical modes amplitudes at time ``t`` and ``c`` is a list of the optical mode amplitudes and the constant parameters of the system. Returns the mechanical mode rates with same dimension as ``betas``.
        get_betas               function to obtain the classical mechanical mode amplitudes for a given list of modes, formatted as ``get_betas(betas, parms, t)``, where ``betas`` are the mechanical modes amplitudes at time ``t`` and ``params`` are the constant parameters of the system. Returns the mechanical modes with same dimension as ``betas``.
        ======================  ================================================
    """

    def __init__(self, params, cb_update=None):
        """Class constructor for SOMASystem."""

        # initialize super class
        super().__init__(params=params, code='SOMASystem', name='Array of single-optomechanical System', num_modes=4, cb_update=cb_update)

        # update attributes
        self.required_funcs.update({
            'get_mode_amplitude_dynamics': ['get_ivc', 'get_mode_rates'],
            'get_lle_dynamics': ['get_Ds', 'get_ivc', 'get_Ns', 'get_S', 'get_X'],
            'get_nlse_dynamics': ['get_ivc', 'get_op_d', 'get_op_n']
        })
        self.required_params.update({
            'get_mode_amplitude_dynamics': ['cache', 'cache_dir', 'cache_file', 'method', 'mode_type', 'range_min', 'range_max', 'show_progress', 't_min', 't_max', 't_dim'],
            'get_nlse_dynamics': ['show_progress', 't_min', 't_max', 't_dim', 't_div']
        })
        self.ui_defaults.update({
           't_div': 100,
           'mode_type': 'optical'
        })

    def get_mode_intensity_dynamics(self, solver_params: dict, plot: bool=False, plotter_params: dict=dict()):
        """Method to obtain the dynamics of the optical or mechanical mode amplitudes by solving the classical equations of motion.

        Requires predefined callables ``get_ivc`` and ``get_mode_rates``.
        
        Refer [1]_ for the implementation details.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        plot : bool
            Option to plot the dynamics.
        plotter_params : dict
            Parameters for the plotter.

        Returns
        -------
        I : list
            Required mode intensities at every point of time.
        T : list 
            Times at which the measures are calculated.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_mode_amplitude_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # get modes and times
        Modes, _, T = self.get_modes_corrs_dynamics(solver_params=solver_params)

        # extract frequently used variables
        _n = int(self.num_modes / 2)
        _mode_type = solver_params.get('mode_type', 'optical')
        _range_min = int(solver_params.get('range_min', 0))
        _range_max = int(solver_params.get('range_max', len(T)))
        N = list(range(_n))

        # extract required mode intensities
        I = [[np.linalg.norm(Modes[i][2 * j + (1 if _mode_type == 'mechanical' else 0)]) for j in range(_n)] for i in range(_range_min, _range_max)]

        # if plot opted
        if plot:
            self.plot_dynamics(plotter_params=plotter_params, V=I, T=T, N=N)

        return I, T[_range_min:_range_max], N

    def get_lle_dynamics(self, solver_params):
        """Method to obtain the solutions of the Lugiato-Lefever equation (LLE) using the Split-step Fourier Method.

        Requires predefined callables ``get_D``, ``get_ivc``, ``get_N``, ``get_S`` and ``get_X``. Also, either one of the functions ``get_betas`` and ``get_beta_rates`` should be defined.

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
        assert self.validate_required_funcs(func_name='get_lle_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # validate optional functions
        assert getattr(self, 'get_beta_rates', None) is not None or getattr(self, 'get_betas', None) is not None, 'Either of the functions ``get_beta_rates`` or ``get_betas`` should be non-none'

        # validate parameters
        for key in ['t_min', 't_max', 't_dim']:
            assert key in solver_params, 'Parameter ``params`` should contain key "{}" for looper parameters'.format(key)
                
        # extract frequently used variables
        t_min = np.float_(solver_params['t_min'])
        t_max = np.float_(solver_params['t_max'])
        t_dim = int(solver_params['t_dim'])
        # _method = solver_params.get('method', 'RK45')
        _show_progress = solver_params.get('show_progress', False)

        # calculate times
        ts = np.linspace(t_min, t_max, t_dim)
        # truncate values
        _ss = (Decimal(str(t_max)) - Decimal(str(t_min))) / (t_dim - 1)
        _decimals = - _ss.as_tuple().exponent
        # round off and convert to list
        T = np.around(ts, _decimals).tolist()
        # steps size
        t_ss = T[1] - T[0]

        # extract parameters
        iv, c = self.get_ivc()
        modes = iv[:self.num_modes]
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c
    
        # initialize variables
        Modes = list()
        Modes.append([m for m in modes])
        alphas = np.array(modes[::2])

        for i in range(1, t_dim):
            t = (i - 1) * t_ss + t_min
            # update progress
            if _show_progress:
                self._update_progress(module_name=__name__, pos=i, dim=t_dim)

            # apply nonlinearity
            Ns = self.get_Ns(modes, params, t)
            S = self.get_S(modes, params, t)
            alpha_nls = np.exp(Ns * t_ss) * (alphas + S / Ns) - S / Ns

            # apply dispersion
            alpha_tildes = sf.fft(alpha_nls)
            # solver = ODESolver(params=solver_params, func=lambda t, v, c: self.get_Ds(modes=v, params=c, t=t), iv=alpha_tildes, c=params, method=_method, cb_update=self.cb_update)
            # alpha_tildes = solver.solve(T=[0, t_ss])[-1]
            Ds = self.get_Ds(modes, params, t)
            alpha_tildes = np.exp(Ds * t_ss) * alpha_tildes
            alphas = sf.ifft(alpha_tildes)

            # update lists
            for j in range(len(alphas)):
                modes[2 * j] = alphas[j]
            betas = self.get_betas(modes, params, t)
            for j in range(len(alphas)):
                modes[2 * j + 1] = betas[j]
            Modes.append([m for m in modes])

        # display completion
        if _show_progress:
            logger.info('------------------Dynamics Obtained------------------\n')
            if self.cb_update is not None:
                self.cb_update(status='Dynamics Obtained', progress=None, reset=True)

        return Modes, self.get_X(params), T

    def get_nlse_dynamics(self, solver_params):
        """Method to obtain the solutions of the Nonlinear Schrodinger Equation (NLSE) using the Split-step Fourier Method.

        Requires predefined callables ``get_ivc``, ``get_op_d`` and ``get_op_n``. Also, either one of the functions ``get_betas`` and ``get_beta_rates`` should be defined.

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
        show_progress = solver_params.get('show_progress', False)

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
            if show_progress and int(progress * 1000) % 10 == 0:
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

            if getattr(self, 'get_beta_rates', None) is not None:
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