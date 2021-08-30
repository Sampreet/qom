#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface QOM systems."""

__name__    = 'qom.systems.BaseSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2021-08-30'

# dependencies
from typing import Union
import copy
import logging
import numpy as np
import scipy.linalg as sl
import scipy.optimize as so

# qom modules
from ..solvers import HLESolver, ODESolver, QCMSolver, RHCSolver
from ..ui.plotters import MPLPlotter

# module logger
logger = logging.getLogger(__name__)

# TODO: Fix "gso" in `get_lyapunov exponents`.
# TODO: Add `check_limit_cycle`.

class BaseSystem():
    r"""Class to interface QOM systems.

    Initializes `params` property.

    Parameters
    ----------
    params : dict
        Parameters for the system.
    code : str
        Codename for the interfaced system.
    name : str
        Full name of the interfaced system.
    num_modes : int
        Number of modes of the interfaced system.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    References
    ----------

    .. [1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86** (4), 1931 (2014).

    .. [2] F. Galve, G. L. Giorgi, R. Zambrini, *Quantum Correlations and Synchronization Measures*, Lectures on General Quantum Correlations and their Applications, Quantum Science and Technology, Springer (2017).

    Notes
    -----
    The ``params`` dictionary currently supports the following keys:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "cache"             (*bool*) option to cache the time series.
        "cache_dir"         (*str*) directory where the time series is cached.
        "cache_file"        (*str*) filename of the cached time series.
        "idx_e"             (*int* or *tuple* or *list*) index or indices of the elements in a list. This value should be an integer or a list of integers when the type of measure is "mode_amp" or "eigen_dm". Otherwise, it is a tuple of dimension *2* or a list of such tuples. Refer notes for all currently supported values.
        "measure_type"      (*str*) type of measure to calculate. Currently supported types of measures are described in the next table.
        "method_le"         (*str*) method used to calculate the unit vectors and eigenvalues for Lyapunov exponents. Currently supported methods are "gso" for Gram-Schmidt orthonormalization and "svd" for singular value decomposition.
        "num_iters"         (*int*) number of iterations to calculate the deviations for Lyapunov exponents. 
        "range_min"         (*float*) minimum index of time at which the measure is calculated.
        "range_max"         (*float*) maximum index of time at which the measure is calculated.
        "show_progress"     (*bool*) option to display the progress of the solver.
        "t_min"             (*float*) minimum time at which integration starts.
        "t_max"             (*float*) maximum time at which integration stops.
        "t_dim"             (*int*) number of values from "t_max" to "t_min", both inclusive.
        ==================  ====================================================

    The key "measure_type" currently supports the following options (refer :class:`qom.solvers.QCMSolver` for quantum correlation measures):
        ==================  ====================================================
        value               meaning
        ==================  ====================================================
        "corr_ele"          elements of the correlation matrix. The corresponding "idx_e" key is a tuple or a list of tuples of the two quadrature indices.
        "discord_G"         Gaussian quantum discord. The corresponding "idx_e" key is a tuple or a list of tuples of the two mode indices.
        "eigen_dm"          eigenvalues of the drift matrix. The corresponding "idx_e" key is an integer or a list of integers of the quadrature indices.
        "entan_ln"          quantum entanglement using logarithmic negativity. The corresponding "idx_e" key is a tuple or a list of tuples of the two mode indices.
        "mode_amp"          complex-valued classical mode amplitudes. The corresponding "idx_e" key is an integer or a list of integers of the mode indices.
        "sync_c"            complete quantum synchronization. The corresponding "idx_e" key is a tuple or a list of tuples of the two mode indices.
        "sync_p"            quantum phase synchronization. The corresponding "idx_e" key is a tuple or a list of tuples of the two mode indices.
        ==================  ====================================================

    .. note:: All the options defined in ``params`` supersede individual function arguments.

    Some functions require one or more of the following predefined functions to work properly:
        ======================  ================================================
        function                purpose
        ======================  ================================================
        func_ode                Function returning the rate equations of the classical mode amplitudes and quantum correlations, formatted as ``func_ode(t, v, c)``, where ``t`` is the time at which the integration is performed, ``v`` is a list of the amplitudes and fluctuations and ``c`` is a list of constant parameters. The output should match the dimension of ``v``. If ``func_ode_corrs`` parameter is given, this function is treated as the function for the modes only.
        func_ode_corrs          Function returning rate equations of the quantum correlations. It follows the same formatting as ``func_ode``.
        get_A                   Function returning the drift matrix, formatted as ``get_A(modes, params, t)``, where ``modes`` are the modes amplitudes at time ``t`` and ``params`` are the constant parameters of the system. Returns the drift matrix ``A``.
        get_ivc                 Function returning the initial values and constants, formatted as ``get_ivc()``. Returns values ``iv`` and ``c`` for the initial values and constants respectively.
        get_mode_rates          Function returning the rate of the classical mode amplitudes for a given list of modes, formatted as ``get_mode_rates(modes, params, t)``, where ``modes`` are the modes amplitudes at time ``t`` and ``params`` are the constant parameters of the system. Returns the mode rates with same dimension as ``modes``.
        get_oss_args            Function to obtain the required parameters to calculate the optical steady state, formatted as ``get_oss_args(params)``, where ``params`` are the constant parameters of the system. 
        ======================  ================================================

    The ``get_oss_args`` function should return the following values in order:
        ==========  ====================================================
        parameter   value
        ==========  ====================================================
        ``A_l``     (*float*) amplitude of the laser.
        ``Delta``   (*float*) effective detuning if method is "basic", else detuning of the laser.
        ``kappa``   (*float*) optical decay rate.
        ``C``       (*float*) coefficient of :math:`|\alpha_{s}|^{2}`.
        ==========  ====================================================
    """

    # attributes
    types_measures = ['corr_ele', 'eigen_dm', 'mode_amp']
    types_qcm = ['discord_G', 'entan_ln', 'sync_c', 'sync_p']
    types_plots = getattr(MPLPlotter, 'types_1D') + getattr(MPLPlotter, 'types_2D') + getattr(MPLPlotter, 'types_3D')
    required_funcs = {
        'get_averaged_eigenvalues': ['get_A', 'get_ivc', 'get_mode_rates'],
        'get_lyapunov_exponents': ['get_A', 'get_ivc', 'get_mode_rates'],
        'get_mean_optical_amplitudes': ['get_ivc', 'get_oss_args'],
        'get_mean_optical_occupancies': ['get_ivc', 'get_oss_args'],
        'get_measure_average': ['get_ivc', 'get_mode_rates'],
        'get_measure_dynamics': ['get_ivc', 'get_mode_rates'],
        'get_measure_stationary': ['get_ivc'],
        'get_modes_corrs_dynamics': ['get_ivc', 'get_mode_rates'],
        'get_modes_corrs_stationary': ['get_ivc'],
        'get_pearson_correlation_coefficient': ['get_ivc', 'get_mode_rates'],
        'get_rhc_count_dynamics': ['get_A', 'get_ivc', 'get_mode_rates'],
        'get_rhc_count_stationary': ['get_ivc', 'get_mode_rates']
    }
    required_params = {
        'get_averaged_eigenvalues': ['cache', 'cache_dir', 'cache_file', 'method', 'range_min', 'range_max', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_lyapunov_exponents': ['cache', 'cache_dir', 'cache_file', 'method', 'method_le', 'num_iters', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_mean_optical_amplitudes': [],
        'get_mean_optical_occupancies': [],
        'get_measure_average': ['cache', 'cache_dir', 'cache_file', 'idx_e', 'measure_type', 'method', 'range_min', 'range_max', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_measure_dynamics': ['cache', 'cache_dir', 'cache_file', 'idx_e', 'measure_type', 'method', 'range_min', 'range_max', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_measure_stationary': ['idx_e', 'measure_type', 'show_progress'],
        'get_modes_corrs_dynamics': ['cache', 'cache_dir', 'cache_file', 'method', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_modes_corrs_stationary': [],
        'get_pearson_correlation_coefficient': ['cache', 'cache_dir', 'cache_file', 'idx_e', 'measure_type', 'method', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_rhc_count_dynamics': ['cache', 'cache_dir', 'cache_file', 'method', 'show_progress', 't_min', 't_max', 't_dim'],
        'get_rhc_count_stationary': []
    }
    ui_defaults = {
        'cache': True,
        'cache_dir': 'data',
        'cache_file': 'V',
        'idx_e': [0],
        'measure_type': 'mode_amp',
        'method': 'RK45',
        'method_le': 'svd',
        'num_iters': 10000,
        'range_min': 0,
        'range_max': 10001,
        'show_progress': True,
        't_min': 0.0,
        't_max': 1000.0,
        't_dim': 10001
    }

    def __init__(self, params: dict, code: str, name: str, num_modes: int, cb_update=None):
        """Class constructor for BaseSystem."""

        # set attributes
        self.params = params
        self.code = code
        self.name = name
        self.num_modes = num_modes
        self.cb_update = cb_update

    def __get_cache_options(self, solver_params):
        """Method to return updated options to cache dynamics.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.

        Returns
        -------
        cache : bool, optional
            Option to cache the time series.
        cache_dir : str
            Directory where the time series is cached.
        cache_file : str
            Filename of the cached time series.
        """

        # extract frequently used variables
        t_min = np.float_(solver_params.get('t_min', 0.0))
        t_max = np.float_(solver_params.get('t_max', 1000.0))
        t_dim = int(solver_params.get('t_dim', 10001))
        cache = solver_params.get('cache', True)
        cache_dir = solver_params.get('cache_dir', 'data')
        cache_file = solver_params.get('cache_file', 'V')

        # if cache opted
        if cache and cache_dir != '' and cache_file != '':
            # update directory
            if cache_dir == 'data':
                cache_dir += '\\' + self.code + '\\' + str(t_min) + '_' + str(t_max) + '_' + str(t_dim)
            # update filename
            if cache_file == 'V' and self.params is not None:
                for key in self.params:
                    cache_file += '_' + str(self.params[key])

        return cache, cache_dir, cache_file

    def __get_func_real(self, func):
        """Method to return a real-valued function from a complex-valued one.
        
        Parameters
        ----------
        func : callable
            Complex-valued function, formatted as ``func(v, c, t)``, where ``v`` are the complex-valued variables at time ``t`` and ``c`` are real-valued arguments. Returns complex-valued variables ``values`` of same dimension as ``v``.

        Returns
        -------
        func_real : callable
            Real-valued function, formatted as ``func_real(modes_real, c, t)``, where ``v_real`` contain the real and imaginary parts of ``v`` at time ``t`` and ``c`` are the unaltered real-valued arguments. Returns real-valued variables ``values_real`` of twice the dimension of ``v``.
        """
        
        # real-valued function
        def func_real(v_real, c, t):
            """Function to obtain a real-valued function.
                    
            Parameters
            ----------
            v_real : list
                List of real-valued variables.
            c : tuple
                Other constants of the function.
    
            Returns
            -------
            values_real : list
                List of real-valued values.
            """
            
            # convert to complex
            v = [v_real[2 * i] + 1j * v_real[2 * i + 1] for i in range(int(len(v_real) / 2))]

            # complex-valued mode rates
            values = func(v, c, t)

            # convert to real
            values_real = list()
            for value in values:
                values_real.append(np.real(value))
                values_real.append(np.imag(value))

            return values_real
    
        return func_real

    def __get_measure(self, solver_params: dict, modes: list, corrs: list):
        """Method to calculate the measure.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        corrs : list
            Matrix of quantum correlations.
        modes : list
            Values of classical mode amplitudes.
        
        Returns
        -------
        measure : float
            Calculated measure.
        """

        # extract frequently used variables
        _measure_type = solver_params['measure_type']
        _idx_e = solver_params['idx_e']

        # correlation matrix elements
        if _measure_type == 'corr_ele':
            measure = [corrs[idx[0]][idx[1]]  for idx in _idx_e]
        # mode amplidutes
        elif _measure_type == 'mode_amp':
            measure = [modes[idx] for idx in _idx_e]
        # quantum correlation measure
        else:
            solver = QCMSolver(modes=modes, corrs=corrs)
            # get function
            _qcm_func = {
                'discord_G': 'get_discord_Gaussian',
                'entan_ln': 'get_entanglement_logarithmic_negativity',
                'sync_c': 'get_synchronization_complete',
                'sync_p': 'get_synchronization_phase'
            }[_measure_type]
            # calculate measure
            measure = getattr(solver, _qcm_func)(pos_i=2 * _idx_e[0][0], pos_j=2 * _idx_e[0][1])

        return measure

    def __validate_params_measure(self, solver_params: dict, count: int=None):
        """Method to validate parameters for 1D list indices.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        """

        # validate parameters
        assert 'measure_type' in solver_params, 'Solver parameters should contain key "measure_type" for the type of measure'
        assert 'idx_e' in solver_params, 'Solver parameters should contain the key "idx_e" for the index of element'

        # extract frequently used variables
        _measure_type = solver_params['measure_type']
        _idx_e = solver_params['idx_e']
        _dim = 2 * self.num_modes

        # supported measure types
        supported_types = self.types_measures + self.types_qcm
        assert _measure_type in supported_types, 'Key "measures" should assume one of {}'.format(supported_types)

        # index type
        assert isinstance(_idx_e, Union[list, int, tuple].__args__), 'Key "idx_e" should be integer or list of integers'
        
        # convert to list
        if type(_idx_e) is int or type(_idx_e) is tuple:
            solver_params['idx_e'] = [_idx_e]
            _idx_e = [_idx_e]
        # handle fixed count
        assert len(_idx_e) == count if count is not None else True, 'Key "idx_e" should contain exactly {} entries'.format(count)
        # handle limits
        for idx in _idx_e:
            # handle integers (mode amplitudes or eigenvalues of drift matrix)
            if type(idx) is int:
                assert idx < _dim / 2 if _measure_type == 'mode_amp' else idx < _dim, 'Element indices should not exceed total number of modes or quadratures'
            # handle tuples (elements of correlation matrix or qcm)
            else:
                assert len(idx) == 2, 'Tuples should be of lenght ``2``'
                assert idx[0] < _dim and idx[1] < _dim if _measure_type == 'corr_ele' else idx[0] < _dim / 2 and idx[1] < _dim / 2, 'Element indices should not exceed total number of modes or quadratures'

    def func_ode(self, t, v, c):
        """Wrapper function for the rate equations of the modes and quadrature correlations. 

        Requires already defined callables ``get_mode_rates`` and ``get_A`` inside the system class.
        
        The variables are complex-valued, hence the model requires a complex-valued integrator.
        
        Parameters
        ----------
        t : float
            Time at which the rate is calculated.
        v : list
            Complex-valued variables defining the system.
        c : list
            Constants of the integration. First (4 * num_modes^2) elements contain the noise matrix. Remaining elements contain the constant parameters.

        Returns
        -------
        rates : list
            Rates of the complex-valued variables defining the system.
        """

        # if only mode ODEs
        if len(v) == self.num_modes:
            return self.get_mode_rates(modes=v, params=c, t=t)        

        # extract the modes and correlations
        _dim    = [2 * self.num_modes, 2 * self.num_modes]
        modes   = v[:self.num_modes]
        corrs   = np.real(v[self.num_modes:]).reshape(_dim)
        D       = np.array(c[:_dim[0] * _dim[1]]).reshape(_dim)
        params  = c[_dim[0] * _dim[1]:]

        # mode rates
        mode_rates  = self.get_mode_rates(modes=modes, params=params, t=t)

        # drift matrix
        A = self.get_A(modes=modes, params=params, t=t)

        # quadrature correlation rate equation
        dcorrs_dt = A.dot(corrs) + corrs.dot(np.transpose(A)) + D

        # mirror matrix
        for i in range(len(dcorrs_dt)):
            for j in range(0, i):
                dcorrs_dt[i, j] = dcorrs_dt[j, i]

        # convert to 1D list and concatenate all rates
        rates = mode_rates + [np.complex(element) for element in dcorrs_dt.flatten()]

        return rates

    def get_averaged_eigenvalues(self, solver_params: dict):
        """Function to obtain the averaged eigenvalues of the drift matrix.

        Requires already defined callables ``func_ode``, ``get_A`` inside the system class.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.            
        
        Returns
        -------
        eig_avg : list
            Averaged eigenvalues of the drift matrix.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_averaged_eigenvalues', mode='verbose') is True, 'Missing required predefined functions'

        # update a deep copy of parameters
        _solver_params = copy.deepcopy(solver_params)
        _solver_params['measure_type'] = 'mode_amp'
        _solver_params['idx_e'] = [i for i in range(self.num_modes)]

        # get averaged modes
        modes = self.get_measure_average(solver_params=_solver_params)

        # extract parameters
        _, c = self.get_ivc()
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c

        # drift matrix
        A = self.get_A(modes=modes, params=params, t=None)

        # initialize lists
        eig_avg = list()
        
        # update eigenvalues
        eigenvalues, _ = np.linalg.eig(A)
        for idx in _solver_params['idx_e']:
            eig_avg.append(eigenvalues[idx])

        return eig_avg

    def get_lyapunov_exponents(self, solver_params, method_le: str='svd', num_iters: int=10000):
        """Method to obtain the Lyapunov exponents.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        method_le : int, optional
            Method used to calculate the unit vectors and eigenvalues. Currently available options are
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "gso"       Gram-Schmidt orthonormalization (fallback).
                "svd"       singular value decomposition.
                ==========  ====================================================
        num_iters : int, optional
            Number of iterations for the calculation of deviations.

        Returns
        -------
        lambdas : float
            Lyapunov exponents.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_lyapunov_exponents', mode='verbose') is True, 'Missing required predefined functions'

        # supersede solver parameterss
        method_le = solver_params.get('method_le', method_le)
        num_iters = int(solver_params.get('num_iters', num_iters))

        # frequently used variables
        _dim = 2 * self.num_modes
        iv, c = self.get_ivc()
        if len(c) > _dim**2:
            params = c[_dim**2:]
        else:
            params = c

        # get modes and times
        Modes, _, T = self.get_modes_corrs_dynamics(solver_params=solver_params)

        # extract the last element
        _dt = T[1] - T[0]
        _T = np.linspace(T[-1], T[-1] + num_iters * _dt, num_iters + 1)

        # if singular value decomposition
        if method_le == 'svd':
            # ODE function
            def func_ode(t, v, c=None):
                # extract frequently used variables
                quads = v[0:_dim]
                modes = [quads[2 * i] + 1j * quads[2 * i + 1] for i in range(int(_dim / 2))]
                W = np.reshape(v[_dim:], (_dim, _dim))

                # obtain quadrature rates
                quad_rates = self.__get_func_real(func=self.get_mode_rates)(v_real=quads, c=params, t=t)
                # obtain deviation rates
                W_rate = np.dot(self.get_A(modes=modes, params=params, t=t), W).flatten().tolist()

                return quad_rates + W_rate

            # initial values
            iv_quads = list()
            for m in Modes[-1]:
                iv_quads.append(np.real(m))
                iv_quads.append(np.imag(m))
            iv = iv_quads + np.identity(_dim, dtype=np.float_).flatten().tolist()

            # initialize solver
            solver = ODESolver(params=solver_params, func=func_ode, iv=iv)
            # extract final vector for another t_dim points
            W = np.reshape(solver.solve(T=_T)[-1][_dim:], (_dim, _dim))

            # singular value decomposition
            _, s, _ = sl.svd(W)
            # exponents
            lambdas = [np.log10(s[i]) / num_iters / _dt  for i in range(len(s))]
        # Gram-Schmidt orthonormalization    
        else:
            # ODE function
            def func_ode(t, modes, c=None):
                return self.get_mode_rates(modes=modes, params=params, t=t)

            # initialize solver
            solver = ODESolver(params=solver_params, func=func_ode, iv=Modes[-1])
            # extract final vector for another t_dim points
            Modes = solver.solve(T=_T)

            # initialize variables
            lambdas = np.zeros(_dim, dtype=np.float_)
            W_T = np.identity(_dim, dtype=np.float_)

            # iterate
            for k in range(0, num_iters):
                # get drift matrix at steady state
                jac = self.get_A(modes=Modes[k], params=params, t=_T[k])

                # calculate zs and transpose for ease in next steps
                Z_T = np.transpose(np.dot(np.identity(_dim, dtype=np.float_) + jac * _dt, np.transpose(W_T)))

                # perform Gram-Schmidt orthonormalization
                for i in range(_dim):
                    # orthonormalize
                    Z_T[i] -= np.sum([np.dot(Z_T[i], W_T[j]) * Z_T[j] for j in range(0, i)], axis=0)

                    # update unit eigenvectors
                    W_T[i] = Z_T[i] / np.linalg.norm(Z_T[i])

                    # update Lyapunov exponents
                    lambdas[i] += np.log10(np.linalg.norm(Z_T[i])) / num_iters

        return lambdas

    def get_mean_optical_amplitudes(self, method: str='cubic'):
        r"""Method to obtain the mean optical amplitudes.

        The optical steady state is assumed to be of the form [1]_,

        .. math::
            \alpha_{s} = \frac{A_{l}}{\frac{\kappa}{2} - \iota \Delta}

        where :math:`\Delta = \Delta_{l} + C |\alpha_{s}|^{2}`.

        Parameters
        ----------
        method : str, optional
            Method of calculation of intracavity photon number. Currently available options are:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "basic"     assuming constant effective detuning.
                "cubic"     cubic variation with laser detuning (fallback).
                ==========  ====================================================
        
        Returns
        -------
        alpha_s : list
            Mean optical amplitudes.
        roots : list
            Roots of the cubic equation. If ``method`` is "basic", this is the same as ``N_o``.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_mean_optical_amplitudes', mode='verbose') is True, 'Missing required predefined functions'
        
        # extract parameters
        _, c = self.get_ivc()
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c
        A_l, Delta, kappa, C = self.get_oss_args(params=params)

        # basic method
        if method == 'basic':
            alpha_s = [A_l / (kappa / 2 - 1j * Delta)]
            roots = [np.real(np.conjugate(a) * a) for a in alpha_s]
        # cubic method
        else:
            # get mean optical occupancies and roots of the cubic equation
            N_o, roots = self.get_mean_optical_occupancies()
            alpha_s = list()
            for n_o in N_o:
                alpha_s.append(A_l / (kappa / 2 - 1j * (Delta + C * n_o)))

        # return
        return alpha_s, roots

    def get_mean_optical_occupancies(self, method: str='cubic'):
        r"""Method to obtain the mean optical occupancies.

        The mean optical occupancy can be written as [1]_,

        .. math::
            N_{o} = |\alpha_{s}|^{2} = \frac{\left| A_{l} \right|^{2}}{\frac{\kappa^{2}}{4} + \Delta^{2}}

        where :math:`\Delta = \Delta_{l} + C N_{o}`.

        Parameters
        ----------
        method : str, optional
            Method of calculation of intracavity photon number. Currently available options are:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "basic"     assuming constant effective detuning.
                "cubic"     cubic variation with laser detuning (fallback).
                ==========  ====================================================
        
        Returns
        -------
        N_o : list
            Mean optical occupancies.
        roots : list
            Roots of the cubic equation. If ``method`` is "basic", this is the same as ``N_o``.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_mean_optical_occupancies', mode='verbose') is True, 'Missing required predefined functions'

        # extract parameters
        _, c = self.get_ivc()
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c
        A_l, Delta, kappa, C = self.get_oss_args(params=params)

        # basic method
        if method == 'basic':
            # get mean optical amplitudea
            _, N_o = self.get_mean_optical_amplitude()
            roots = [n_o for n_o in N_o]

        # cubic method
        else:
            # get coefficients
            coeff_0 = 4 * C**2
            coeff_1 = 8 * C * Delta
            coeff_2 = 4 * Delta**2 + kappa**2
            coeff_3 = - 4 * np.real(np.conjugate(A_l) * A_l)

            # get roots
            roots = np.roots([coeff_0, coeff_1, coeff_2, coeff_3])

            # mean optical occupancy
            N_o = list()
            # retain real roots
            for root in roots:
                if np.imag(root) == 0.0:
                    N_o.append(np.real(root))

        # return
        return N_o, roots

    def get_measure_average(self, solver_params: dict):
        """Method to obtain the average value of a measure.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        
        Returns
        -------
        M_avg : float
            Average value of the measures.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_measure_average', mode='verbose') is True, 'Missing required predefined functions'

        # get measures at all times
        M, _ = self.get_measure_dynamics(solver_params=solver_params)

        # calculate average over first axis
        M_avg = np.mean(M, 0)

        return M_avg
    
    def get_measure_dynamics(self, solver_params: dict, plot: bool=False, plotter_params: dict=dict()):
        """Method to obtain the dynamics of a measure.

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
        M : list
            Measures calculated at all times.
        T : list 
            Times at which the measures are calculated.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_measure_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # validate parameters
        self.__validate_params_measure(solver_params=solver_params)

        # get mode and correlation dynamics
        Modes, Corrs, T = self.get_modes_corrs_dynamics(solver_params=solver_params)

        # extract frequently used variables
        _show_progress = solver_params.get('show_progress', False)
        _range_min = int(solver_params.get('range_min', 0))
        _range_max = int(solver_params.get('range_max', len(T)))
        _measure_type = solver_params['measure_type']
        _module_name = {
            'corr_ele': __name__,
            'eigen_dm': __name__,
            'mode_amp': __name__,
        }.get(_measure_type, 'qom.solvers.QCMSolver')

        # validate required function
        assert getattr(self, 'get_A', None) is not None if _measure_type == 'eigen_dm' else True, 'Missing required predefined function ``get_A``'

        # display initialization
        if _show_progress:
            logger.info('------------------Obtaining Measures-----------------\n')
            if self.cb_update is not None:
                self.cb_update(status='Obtaining Measures...', progress=None, reset=True)

        # initialize list
        M = list()

        # iterate for all times in given range
        for i in range(_range_min, _range_max):
            # update progress
            progress = float(i - _range_min)/float(_range_max - _range_min - 1) * 100
            # display progress
            if _show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Computing ({module_name}): Progress = {progress:3.2f}'.format(module_name=_module_name, progress=progress))
                if self.cb_update is not None:
                    self.cb_update(status='Computing ({module_name})...'.format(module_name=_module_name), progress=progress)

            # eigenvalues of drift matrix
            if _measure_type == 'eigen_dm':
                # extract parameters
                _, c = self.get_ivc()
                if len(c) > 4 * self.num_modes**2:
                    params = c[4 * self.num_modes**2:]
                else:
                    params = c
                eigs, _ = np.linalg.eig(self.get_A(modes=Modes[i], params=params, t=T[i]))

                # extract eigenvalues
                measure = list()
                for idx in solver_params['idx_e']:
                    measure.append(eigs[idx])
            # elif correlation matrix element or mode amplitude
            else:
                measure = self.__get_measure(solver_params=solver_params, modes=Modes[i], corrs=Corrs[i])

            # update list
            M.append(measure)

        # display completion
        if _show_progress:
            logger.info('------------------Measures Obtained------------------\n')
            if self.cb_update is not None:
                self.cb_update(status='Measures Obtained', progress=None, reset=True)

        if plot:
            self.plot_dynamics(plotter_params=plotter_params, V=np.transpose(M).tolist() if _measure_type in self.types_qcm else M, T=T[_range_min:_range_max])

        return M, T[_range_min:_range_max]
    
    def get_measure_stationary(self, solver_params: dict):
        """Method to obtain the stationary value of a measure.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.

        Returns
        -------
        measure : float
            Calculated measure.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_measure_stationary', mode='verbose') is True, 'Missing required predefined functions'

        # validate parameters
        self.__validate_params_measure(solver_params=solver_params)

        # get stationary values of mode and correlation
        modes, corrs = self.get_modes_corrs_stationary(type_func='complex')

        # extract frequently used variables
        _show_progress = solver_params.get('show_progress', False)
        _measure_type = solver_params['measure_type']

        # validate required function
        assert getattr(self, 'get_A', None) is not None if _measure_type == 'eigen_dm' else True, 'Missing required predefined function ``get_A``'

        # eigenvalues of drift matrix
        if _measure_type == 'eigen_dm':
            # extract parameters
            _, c = self.get_ivc()
            if len(c) > 4 * self.num_modes**2:
                params = c[4 * self.num_modes**2:]
            else:
                params = c
            eigs, _ = np.linalg.eig(self.get_A(modes=modes, params=params, t=None))
                
            # extract eigenvalues
            measure = list()
            for idx in solver_params['idx_e']:
                measure.append(eigs[idx])
        # elif correlation matrix element or mode amplitude
        else:
            measure = self.__get_measure(solver_params=solver_params, modes=modes, corrs=corrs)

        # display completion
        if _show_progress:
            logger.info('------------------Measure Obtained-------------------\n')
            if self.cb_update is not None:
                self.cb_update(status='Measures Obtained', progress=None, reset=True)

        return measure

    def get_modes_corrs_dynamics(self, solver_params: dict):
        """Method to obtain the dynamics of the classical mode amplitudes and quantum correlations from the Heisenberg and Lyapunov equations.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.

        Returns
        -------
        Modes : list
            All the modes calculated at all times.
        Corrs : list
            All the correlations calculated at all times.
        T : list
            Times at which values are calculated.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_modes_corrs_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # extract frequently used variables
        _method = solver_params.get('method', 'RK45')
        _cache, _cache_dir, _cache_file = self.__get_cache_options(solver_params=solver_params)

        # update solver params
        _solver_params = copy.deepcopy(solver_params)
        _solver_params['method'] = _method
        _solver_params['cache'] = _cache
        _solver_params['cache_dir'] = _cache_dir
        _solver_params['cache_file'] = _cache_file

        # get initial values and constants
        iv, c = self.get_ivc()
        # if correlations are required
        if len(iv) != self.num_modes:
            # validate drift matrix function
            assert getattr(self, 'get_A', None) is not None, 'Missing required function ``get_A``'
        # handle null constants
        if c is None:
            c = list()

        # initialize solver
        solver = HLESolver(params=_solver_params, cb_update=self.cb_update)
        
        # solve and set results
        solver.solve(func_ode=self.func_ode, iv=iv, c=c, func_ode_corrs=self.func_ode_corrs if getattr(self, 'func_ode_corrs', None) is not None else None, num_modes=self.num_modes)

        # get modes, correlations and times
        Modes = solver.get_Modes(num_modes=self.num_modes)
        Corrs = solver.get_Corrs(num_modes=self.num_modes)
        T = solver.T
        
        return Modes, Corrs, T

    def get_modes_corrs_stationary(self, type_func: str='complex'):
        """Method to obtain the steady states of the classical mode amplitudes and quantum correlations from the Heisenberg and Lyapunov equations.

        Parameters
        ----------
        type_func : str, optional
            Return data-type of ``get_mode_rates``. Currently available options are:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "real"      real-valued rates.
                "complex"   complex-valued rates (fallback).
                ==========  ====================================================

        Returns
        -------
        modes : list
            All the modes calculated at steady-state.
        corrs : list
            All the correlations calculated at steady-state.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_modes_corrs_stationary', mode='verbose') is True, 'Missing required predefined functions'

        # extract the modes and correlations
        _dim = 2 * self.num_modes

        # get initial values and constants
        iv, c = self.get_ivc()

        # if correlations are required
        if len(iv) != self.num_modes:
            # validate drift matrix function
            assert getattr(self, 'get_A', None) is not None, 'Missing required function ``get_A``'

        # handle null constants
        if c is None:
            c = list()
        # get parameters
        if len(c) > _dim**2:
            params = c[_dim**2:]
        else:
            params = c

        # if modes are to be calculated
        if getattr(self, 'get_mode_rates', None) is not None:
            # complex-valued function
            if type_func == 'real':
                # real-valued function
                get_mode_rates_real = self.get_mode_rates
                # real-valued initial values
                iv_real = iv
            else:
                # get real-valued function
                get_mode_rates_real = self.__get_func_real(func=self.get_mode_rates)

                # real-valued initial values
                iv_real = list()
                for mode in iv[:self.num_modes]:
                    iv_real.append(np.real(mode))
                    iv_real.append(np.imag(mode))
        
            # solve for modes
            roots_real = so.fsolve(get_mode_rates_real, iv_real, (params, None, ))
            modes = [roots_real[2 * i] + 1j * roots_real[2 * i + 1] for i in range(int(len(roots_real) / 2))] 
        # modes not required
        else:
            modes = None

        # if drift matrix is given
        if getattr(self, 'get_A', None) is not None:
            # get matrices
            _A = self.get_A(modes=modes, params=params, t=None)
            _D = np.array(c[:_dim**2]).reshape((_dim, _dim))

            # convert to numpy arrays
            _A = np.array(_A) if type(_A) is list else _A
            _D = np.array(_D) if type(_D) is list else _D

            # solve for correlations
            corrs = sl.solve_lyapunov(_A, - _D)
        # correlations not required
        else: 
            corrs = None
        
        return modes, corrs

    def get_pearson_correlation_coefficient(self, solver_params: dict):
        r"""Method to obtain the Pearson correlation coefficient.

        The implementation measure reads as [2]_,

        .. math::
            C_{ij} = \frac{\Sigma_{t} \langle \delta \mathcal{O}_{i} (t) \delta \mathcal{O}_{j} (t) \rangle}{\sqrt{\Sigma_{t} \langle \delta \mathcal{O}_{i}^{2} (t) \rangle} \sqrt{\Sigma_{t} \langle \delta \mathcal{O}_{j}^{2} (t) \rangle}}

        where :math:`\delta \mathcal{O}_{i}` and :math:`\delta \mathcal{O}_{j}` are the corresponding quadratures of quantum fluctuations.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        
        Returns
        -------
        S_Pearson : float
            Pearson synchronization measure.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_pearson_correlation_coefficient', mode='verbose') is True, 'Missing required predefined functions'

        # validate parameters
        self.__validate_params_measure(solver_params=solver_params, count=3)

        # get measures at all times
        M, T = self.get_measure_dynamics(solver_params=solver_params)

        # get mean values
        mean_ii = np.mean([m[0] for m in M])
        mean_ij = np.mean([m[1] for m in M])
        mean_jj = np.mean([m[2] for m in M])

        # Pearson synchronztion measure
        S_Pearson = mean_ij / np.sqrt(mean_ii * mean_jj)

        return S_Pearson

    def get_rhc_count_dynamics(self, solver_params: dict, plot: bool=False, plotter_params: dict=dict()):
        """Function to obtain the number of positive real roots of the drift matrix using the Routh-Hurwitz criterion.

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
        Counts : list
            Number of positive real roots of the drift matrix.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_rhc_count_dynamics', mode='verbose') is True, 'Missing required predefined functions'

        # get modes
        Modes, _, T = self.get_modes_corrs_dynamics(solver_params=solver_params)

        # extract frequently used variables
        _show_progress = solver_params.get('show_progress', False)
        _range_min = int(solver_params.get('range_min', 0))
        _range_max = int(solver_params.get('range_max', len(T)))
        _t_ss = np.float_(solver_params.get('t_max', T[-1] - T[0])) / int(solver_params.get('t_dim', len(T)))

        # extract parameters
        _, c = self.get_ivc()
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c
            
        # display initialization
        if _show_progress:
            logger.info('------------------Obtaining Counts-------------------\n')
            if self.cb_update is not None:
                self.cb_update(status='Obtaining Counts...', progress=None, reset=True)

        # initialize counter
        Counts = list()
        # iterate for all times in given range
        for i in range(_range_min, _range_max):
            # update progress
            progress = float(i - _range_min)/float(_range_max - _range_min - 1) * 100
            # display progress
            if _show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Computing ({module_name}): Progress = {progress:3.2f}'.format(module_name=__name__, progress=progress))
                if self.cb_update is not None:
                    self.cb_update(status='Computing ({module_name})...'.format(module_name=__name__), progress=progress)
                
            # drift matrix
            A = self.get_A(Modes[i], params, i * _t_ss)

            # indices of the RHC sequence
            solver = RHCSolver(A)
            _idxs = solver.get_indices()
            # update counter
            Counts.append(len(_idxs))

        # display completion
        if _show_progress:
            logger.info('------------------Counts Obtained--------------------\n')
            if self.cb_update is not None:
                self.cb_update(status='Counts Obtained', progress=None, reset=True)

        if plot:
            self.plot_dynamics(plotter_params=plotter_params, V=Counts, T=T[_range_min:_range_max])

        return Counts, T[_range_min:_range_max]

    def get_rhc_count_stationary(self, type_func: str='complex'):
        """Function to obtain the number of positive real roots of the drift matrix from the stationary state using the Routh-Hurwitz criterion.

        Parameters
        ----------
        type_func : str, optional
            Return data-type of ``get_mode_rates``. Currently available options are:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "real"      real-valued rates.
                "complex"   complex-valued rates (fallback).
                ==========  ====================================================
        
        Returns
        -------
        count : int
            Number of positive real roots of the drift matrix.
        idxs : list
            Indices of the RHC sequence.
        """

        # validate required functions
        assert self.validate_required_funcs(func_name='get_rhc_count_stationary', mode='verbose') is True, 'Missing required predefined functions'

        # validate optional functions
        assert getattr(self, 'get_A', None) is not None or getattr(self, 'get_coeffs', None) is not None, 'Either of the functions ``get_A`` or ``get_corrs`` should be non-none'

        # get modes
        modes, _ = self.get_modes_corrs_stationary(type_func=type_func)

        # extract parameters
        _, c = self.get_ivc()
        if len(c) > 4 * self.num_modes**2:
            params = c[4 * self.num_modes**2:]
        else:
            params = c

        # if drift matrix is given
        if self.get_A is not None:
            # initialize solver
            solver = RHCSolver(A=self.get_A(modes=modes, params=params, t=None))
        # use coefficients
        else:
            # initialize solver
            solver = RHCSolver(coeffs=self.get_coeffs(modes=modes, params=params, t=None))
            
        # get indices with sign changes
        idxs = solver.get_indices()
        # get number of sign changes
        count = len(idxs)

        return count, idxs

    def plot_dynamics(self, plotter_params: dict, V: list, T: list, X: list=None, hold: bool=True, width: float=5.0, height: float=5.0):
        """Method to plot the dynamics.
        
        Parameters
        ----------
        plotter_params : dict
            Parameters for the plotter. Refer :class:`qom.ui.plotters.MPLPlotter` for curently available options.
        T : list
            Times at which values are calculated.
        V : list
            Values calculated at all times.
        X : list, optional
            X-axis values.
        hold : bool, optional
            Option to hold the plot.
        width : float, optional
            Width of the figure.
        height : float, optional 
            Height of the figure.

        Returns
        -------
        plotter : :class:`qom.ui.plotters.MPLPlotter`
            Instance of ``MPLPLotter``.
        """

        # handle undefined plotter parameters
        if plotter_params is None:
            plotter_params = {}
        # supersede plotter parameters
        plotter_params['type'] = plotter_params.get('type', 'lines')
        plotter_params['width'] = plotter_params.get('width', width)
        plotter_params['height'] = plotter_params.get('height', height)

        # set plotter axes 
        axes = {
            'X': X,
            'Y': T
        } if X is not None else {'X': T}
        
        # initialize plotter
        plotter = MPLPlotter(axes=axes, params=plotter_params)
        
        # update plotter
        plotter.update(xs=X if X is not None else T, ys=T if X is not None else None, vs=V)
        plotter.show(hold)

        return plotter

    def validate_required_funcs(self, func_name, mode='silent'):
        """Method to validate the arguments of available functions.
        
        Parameters
        ----------
        func_name : str
            Name of the getter function.
        mode : str
            Mode of return of the validation check. Available options are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            "verbose"       Provides a detailed log of missing functions
            "silent"        No log provided are raised (fallback).
            ==============  ================================================

        Returns
        -------
        is_go : bool
            Verdict whether all requirements are met.
        """

        # initialize variables
        is_go = True

        # search for all required functions
        for required_func in self.required_funcs.get(func_name, {}):
            if getattr(self, required_func, None) is None:
                # update log
                if mode == 'verbose':
                    logger.warning('Missing required function {required_func}\n'.format(required_func=required_func))
                # flag
                is_go = False
                break

        return is_go