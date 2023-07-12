#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to interface QOM systems.

References
----------

.. [1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86**, 1931 (2014).
"""

__name__ = 'qom.systems.base'
__authors__ = ["Sampreet Kalita"]
__created__ = "2020-12-04"
__updated__ = "2023-07-12"

# dependencies
import logging
import numpy as np

# qom modules
from ..io import Updater

class BaseSystem():
    r"""Class to interface QOM systems.

    Requires ``system_defaults`` attribute before initializing parent.

    Initializes ``name``, ``desc``, ``num_modes``, ``dim_corrs``, ``num_corrs``, ``params``, ``A``, ``D`` and ``updater``.

    Parameters
    ----------
    params : dict, optional
        Parameters for the system. Refer to the notes below for all available options.
    name : str, default='Sys_00'
        Name of the interfaced system.
    desc : str, default="Base System"
        Description of the interfaced system.
    num_modes : int, default=2
        Number of modes of the interfaced system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Notes
    -----
        The following system methods follow a strict formatting:
            ============================    ================================================
            method                          returns
            ============================    ================================================
            func_ode_modes_corrs            the rates of change of the modes and correlations, formatted as ``func_ode_modes_corrs(t, v, c)``, where ``t`` is the time at which the integration is performed, ``v`` is an array of the modes and correlations and ``c`` is an array of the derived constants and controls of the system. The output should match the dimension of ``v``. This function is already defined inside this class. If ``func_ode_corrs`` parameter is given, this function is treated as the function for the modes only.
            func_ode_modes_deviations       the rate equations of the modes and deviations. It follows the same formatting as ``func_ode_modes_corrs``. However, the parameter ``v`` contains only the deviations.
            func_ode_corrs                  the rate equations of the correlations. It follows the same formatting as ``func_ode_modes_corrs``. However, the parameter ``v`` contains only the correlations.
            get_ivc                         the initial values of the modes, correlations and derived constants and controls, formatted as ``get_ivc()``.
            get_A                           the drift matrix, formatted as ``get_A(modes, c, t)``, where ``modes`` are the mode amplitudes at time ``t`` and ``c`` are the derived constants and controls of the system.
            get_mode_rates                  the rate of change of the modes. It follows the same formatting as ``get_A``.
            get_coeffs_A                    the coefficients of the characteristic equations of the drift matrix. It follows the same formatting as ``get_A``.
            get_coeffs_dispersion           the coefficients of :math:`( i \omega )^{j}` in the dispersions. It follows the same formatting as ``get_A``.
            get_nonlinearities              the nonlinearities. It follows the same formatting as ``get_A``.
            get_beta_rates                  the rates of change of the mechanical modes. It follows the same formatting as ``get_A``.
            get_betas                       the mechanical modes. It follows the same formatting as ``get_A``.
            get_D                           the noise matrix, formatted as ``get_D(modes, corrs, c, t)``, where ``modes`` and ``corrs`` are modes and correlations at time ``t`` and ``c`` are the derived constants and controls of the system.
            get_coeffs_N_o                  the coefficients of the polynomial in mean optical occupancy, formatted as ``get_coeffs_N_o(c)``, where ``c`` are the derived constants and controls of the system.
            get_modes_steady_state          the steady state modes with shape ``(dim, num_modes)``. It follows the same formatting as ``get_coeffs_N_o``.
            ============================    ================================================
    """
    
    system_defaults = {}
    """dict : Default parameters of the system."""

    def __init__(self, params:dict={}, name:str='Sys_00', desc:str="Base System", num_modes:int=2, cb_update=None):
        """Class constructor for BaseSystem."""

        # set constants
        self.name = name
        self.desc = desc
        self.num_modes = num_modes
        self.dim_corrs = (2 * num_modes, 2 * num_modes)
        self.num_corrs = 4 * num_modes**2
        
        # set parameters
        self.set_params(params)

        # initialize drift and noise matrices
        self.is_A_constant = False
        self.is_D_constant = True
        self.init_A_D()

        # initialize buffer variables
        self.mode_rates_real = np.zeros(2 * self.num_modes, dtype=np.float_)
        self.matmul_0 = np.empty(self.dim_corrs, dtype=np.float_)
        self.matmul_1 = np.empty(self.dim_corrs, dtype=np.float_)
        self.sum_0 = np.empty(self.dim_corrs, dtype=np.float_)
        self.sum_1 = np.empty(self.dim_corrs, dtype=np.float_)
        self.v_rates = np.empty(2 * self.num_modes + self.num_corrs, dtype=np.float_)

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.systems.' + self.name),
            cb_update=cb_update
        )

    def set_params(self, params:dict):
        """Method to validate and set the system parameters.

        Parameters
        ----------
        params : dict
            Parameters of the system.
        """

        # update system parameters with new ones
        self.params = dict()
        for key in self.system_defaults:
            self.params[key] = params.get(key, self.system_defaults[key])

    def init_A_D(self):
        """Method to initialize the drift matrix and the noise matrix of the system."""

        # handle missing function
        assert getattr(self, 'get_ivc', None) is not None, "Missing required system method ``get_ivc``"

        # frequently used variables
        iv_modes, iv_corrs, c = self.get_ivc()

        # handle null modes
        iv_modes = np.zeros(self.num_modes, dtype=np.complex_) if iv_modes is None else iv_modes

        # handle null controls/constants
        c = np.empty(0) if c is None else c
        # handle lists
        assert type(c) is list or type(c) is np.ndarray, "Derived constants and controls should be either lists or NumPy arrays or ``None``"
        c = np.array(c) if type(c) is list else c

        # initialize matrices
        self.A = np.zeros(self.dim_corrs, dtype=np.float_)
        self.D = np.zeros(self.dim_corrs, dtype=np.float_)

        # update drift matrix
        self.A = self.get_A(
            modes=iv_modes,
            c=c,
            t=0.0
        ) if getattr(self, 'get_A', None) is not None else None

        # update noise matrix
        self.D = self.get_D(
            modes=iv_modes,
            corrs=iv_corrs,
            c=c,
            t=0.0
        ) if getattr(self, 'get_D', None) is not None else None

    def get_mode_rates_real(self, modes_real, c, t):
        """Method to obtain the real-valued mode rates from real-valued modes.

        Requires the system method ``get_mode_rates``. Refer to **Notes** for its implementation.

        Parameters
        ----------
        modes_real : numpy.ndarray
            Real-valued modes.
        c : numpy.ndarray
            Derived constants and controls.
        t : float
            Time at which the drift matrix is calculated.
        
        Returns
        -------
        mode_rates_real : numpy.ndarray
            Real-valued rates for each mode.
        """

        # handle null
        if getattr(self, 'get_mode_rates', None) is None:
            return self.mode_rates_real

        # get complex-valued mode rates
        mode_rates = self.get_mode_rates(
            modes=modes_real[:self.num_modes] + 1.0j * modes_real[self.num_modes:],
            c=c,
            t=t
        )

        # set real-valued mode rates
        self.mode_rates_real[:self.num_modes] = np.real(mode_rates)
        self.mode_rates_real[self.num_modes:] = np.imag(mode_rates)

        return self.mode_rates_real
    
    def func_ode_modes_corrs(self, t, v, c):
        r"""Wrapper function for the rates of change of the real-valued modes and correlations. 

        Requires system method ``get_mode_rates``. Additionally, ``get_A`` should be defined for the correlations. Optionally, ``get_D`` may be defined for correlations. Refer to **Notes** for their implementations.
        
        The variables are casted to real-valued.
        
        Parameters
        ----------
        t : float
            Time at which the values are calculated.
        v : numpy.ndarray
            Real-valued modes and flattened correlations. First ``num_modes`` elements contain the real parts of the modes, the next ``num_modes`` elements contain the imaginary parts of the modes and optionally, the last ``num_corrs`` elements contain the correlations.
        c : numpy.ndarray
            Defived constants and controls.

        Returns
        -------
        rates : numpy.ndarray
            Rates of change of the real-valued modes and flattened correlations.
        """

        # if only modes are present
        if len(v) == 2 * self.num_modes:
            return self.get_mode_rates_real(
                modes_real=v[:2 * self.num_modes],
                c=c,
                t=t
            )

        # extract frequently used variables
        modes = v[:self.num_modes] + 1.0j * v[self.num_modes:2 * self.num_modes]
        corrs = np.reshape(v[2 * self.num_modes:], self.dim_corrs)

        # get drift matrix
        self.A = self.A if self.is_A_constant else self.get_A(
            modes=modes,
            c=c,
            t=t
        )

        # get noise matrix
        self.D = self.D if self.is_D_constant else self.get_D(
            modes=modes,
            corrs=corrs,
            c=c,
            t=t
        )

        # get real-valued mode rates
        self.v_rates[:2 * self.num_modes] = self.get_mode_rates_real(
            modes_real=v[:2 * self.num_modes],
            c=c,
            t=t
        )
        # get flattened correlation rates
        self.v_rates[2 * self.num_modes:] = np.add(np.add(np.matmul(self.A, corrs, out=self.matmul_0), np.matmul(corrs, self.A.transpose(), out=self.matmul_1), out=self.sum_0), self.D, out=self.sum_1).ravel()

        return self.v_rates

    def func_ode_modes_deviations(self, t, v, c):
        r"""Wrapper function for the rates of change of the real-valued modes and flattened deviations. 

        Requires system method ``get_mode_rates``. Additionally, ``get_A`` should be defined for the deviations. Refer to **Notes** for their implementations.
        
        The variables are casted to real-valued.
        
        Parameters
        ----------
        t : float
            Time at which the values are calculated.
        v : numpy.ndarray
            Real-valued modes and flattened deviations. First ``num_modes`` elements contain the real parts of the modes, the next ``num_modes`` elements contain the imaginary parts of the modes and optionally, the last ``num_corrs`` elements contain the deviations.
        c : numpy.ndarray
            Defived constants and controls.

        Returns
        -------
        rates : numpy.ndarray
            Rates of change of the real-valued modes and flattened deviations.
        """

        # if only modes are present
        if len(v) == 2 * self.num_modes:
            return self.get_mode_rates_real(
            modes_real=v[:2 * self.num_modes],
            c=c,
            t=t
        )

        # get drift matrix
        self.A = self.A if self.is_A_constant else self.get_A(
            modes=v[:self.num_modes] + 1.0j * v[self.num_modes:2 * self.num_modes],
            c=c,
            t=t
        )

        # get real-valued mode rates
        self.v_rates[:2 * self.num_modes] = self.get_mode_rates_real(
            modes_real=v[:2 * self.num_modes],
            c=c,
            t=t
        )
        # get flattened deviation rates
        self.v_rates[2 * self.num_modes:] = np.matmul(self.A, np.reshape(v[2 * self.num_modes:], self.dim_corrs), out=self.matmul_0).ravel()

        return self.v_rates

    def get_mean_optical_occupancies(self):
        r"""Method to obtain the mean optical occupancies.

        Requires system methods ``get_ivc`` and ``get_coeffs_N_o``. Refer to **Notes** for their implementations.

        For example, the mean optical occupancy of a simple end-mirror optomechanical system can be written as [1]_,

        .. math::
        
            N_{o} = |\alpha_{s}|^{2} = \frac{\left| A_{l} \right|^{2}}{\frac{\kappa^{2}}{4} + \Delta^{2}}

        where :math:`\Delta = \Delta_{l} + C N_{o}`. This results in a cubic equation with :math:`4` coefficients. The ``get_coeffs_N_o`` method should return these coefficients.
        
        Returns
        -------
        N_os : numpy.ndarray
            Mean optical occupancies.
        """

        # validate required system methods
        for method_name in ['get_ivc', 'get_coeffs_N_o']:
            assert getattr(self, method_name, None) is not None, "Missing required system method ``{}``".format(method_name)

        # extract parameters
        _, _, c = self.get_ivc()
        coeffs = self.get_coeffs_N_o(
            c=c
        )

        # get all roots
        roots = np.roots(coeffs)

        # return real roots for mean optical occupancy
        return np.real(roots[np.imag(roots) == 0.0])