#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to solve deterministic equations of motion."""

__name__ = 'qom.solvers.deterministic'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-01-04"
__updated__ = "2023-07-12"

# dependencies
import copy
import logging
import numpy as np
import scipy.fft as sf
import scipy.linalg as sl
import scipy.optimize as so

# qom modules
from .base import get_all_times, validate_system
from .differential import ODESolver
from ..io import Updater

class HLESolver():
    r"""Class to solve the Heisenberg-Langevin equations for classical mode amplitudes and quantum quadrature correlations.

    Initializes ``system``, ``params``, ``T``, ``Modes``, ``Corrs``, ``Measures`` and ``updater``.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system methods for certain solver methods.
    params : dict
        Parameters for the solver. Refer to **Notes** below for all available options. Required options are:
            ========    ====================================================
            key         value
            ========    ====================================================
            't_min'     (*float*) minimum time at which integration starts.
            't_max'     (*float*) maximum time at which integration stops.
            't_dim'     (*int*) number of values from ``'t_max'`` to ``'t_min'``, both inclusive.
            ========    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Notes
    -----
        The ``params`` dictionary currently supports the following keys:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
            'cache'             (*bool*) option to cache the time series on the disk. Default is ``True``.
            'cache_dir'         (*str*) directory where the time series is cached. Default is ``'cache'``.
            'cache_file'        (*str*) filename of the cached time series. Default is ``'V'``.
            'ode_method'        (*str*) method used to solve the ODEs. Available options are ``'BDF'``, ``'DOP853'``, ``'LSODA'``, ``'Radau'``, ``'RK23'``, ``'RK45'`` (fallback), ``'dop853'``, ``'dopri5'``, ``'lsoda'``, ``'vode'`` and ``'zvode'``. Refer to :class:`qom.solvers.differential.ODESolver` for details of each method. Default is ``'RK45'``.
            'ode_is_stiff'      (*bool*) option to select whether the integration is a stiff problem or a non-stiff one. Default is ``False``.
            'ode_atol'          (*float*) absolute tolerance of the integrator. Default is ``1e-12``.
            'ode_rtol'          (*float*) relative tolerance of the integrator. Default is ``1e-6``.
            't_min'             (*float*) minimum time at which integration starts. Default is ``0.0``.
            't_max'             (*float*) maximum time at which integration stops. Default is ``1000.0``.
            't_dim'             (*int*) number of values from ``'t_max'`` to ``'t_min'``, both inclusive. Default is ``10001``.
            't_index_delay'     (*int*) index of the time to delay for the derived constants and controls. Default is ``0``.
            't_index_min'       (*float*) minimum index of the range of time at which the values are required. If not provided, this is set to ``0``.
            't_index_max'       (*float*) maximum index of the range of time at which the values are required. If not provided, this is set to ``t_dim - 1``.
            'indices'           (*list* or *tuple*) indices of the modes as a list, or a tuple of two integers. Default is ``[0]``.
            ================    ====================================================
    """

    # attributes
    name = 'HLESolver'
    """str : Name of the solver."""
    desc = "Heisenberg-Langevin Equations Solver"
    """str : Description of the solver."""
    solver_defaults = {
        'show_progress': False,
        'cache': True,
        'cache_dir': 'cache',
        'cache_file': 'V',
        'ode_method': 'RK45',
        'ode_is_stiff': False,
        'ode_atol': 1e-12,
        'ode_rtol': 1e-6,
        't_min': 0.0,
        't_max': 1000.0,
        't_dim': 10001,
        't_index_delay': 0,
        't_index_min': None,
        't_index_max': None,
        'indices': [0]
    }
    """dict : Default parameters of the solver."""

    def __init__(self, system, params:dict, cb_update=None):
        """Class constructor for HLESolver."""
        
        # set constants
        self.system = system

        # set parameters
        self.set_params(params)

        # set times
        self.T = get_all_times(self.params)

        # initialize variables
        self.Modes = None
        self.Corrs = None
        self.Measures = None

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.solvers.HLESolver'),
            cb_update=cb_update
        )

    def set_params(self, params):
        """Method to validate and set the solver parameters, cache options and times.
        
        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # validate system
        validate_system(
            system=self.system,
            required_system_attributes=['name', 'params']
        )

        # check required parameters
        t_keys = ['t_min', 't_max', 't_dim']
        for key in t_keys:
            assert key in params, "Parameter ``params`` does not contain the required key ``'{}'``".format(key)

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

        # handle none ranges
        if self.params['t_index_min'] == None:
            self.params['t_index_min']  = 0
        if self.params['t_index_max'] == None:
            self.params['t_index_max']  = self.params['t_dim'] - 1

        # set cache options
        self.cache = self.params['cache']
        self.cache_dir = (self.params['cache_dir'] + '/' + self.system.name.lower() + '/' + '_'.join([str(self.params[key]) for key in t_keys] + [self.params['ode_method']])) if self.params['cache_dir'][-len(self.solver_defaults['cache_dir']):] == self.solver_defaults['cache_dir'] else self.params['cache_dir']
        self.cache_file = self.params['cache_file'] + '_' + '_'.join([str(value) for value in self.system.params.values()])

    def set_results(self, func_ode_modes_corrs, iv_modes, iv_corrs, c, func_ode_corrs):
        """Method to solve the ODEs and update the results.

        Parameters
        ----------
        func_ode_modes_corrs : callable
            Function returning the rate equations of the modes and correlations. If ``func_ode_corrs`` parameter is given, this function is treated as the function for the modes only. Refer to :class:`qom.systems.base.BaseSystem` for their implementations.
        iv_modes : list or numpy.ndarray
            Initial values for the modes.
        iv_corrs : list or numpy.ndarray
            Initial values for the correlations.
        c : list or numpy.ndarray
            Derived constants and controls for the function.
        func_ode_corrs : callable
            Function returning the rate equations of the correlations.
        """

        # extract frequently used variables
        show_progress   = self.params['show_progress']
        decoupled       = func_ode_corrs is not None

        # format initial values to real
        if iv_modes is None or len(iv_modes) == 0:
            iv = np.zeros(2 * self.system.num_modes, dtype=np.float_)
        else:
            iv = np.concatenate((np.real(iv_modes), np.imag(iv_modes)), dtype=np.float_)
            
        # handle null
        if iv_corrs is None or (type(iv_corrs) is not list and type(iv_corrs) is not np.ndarray):
            iv_corrs = np.empty(0)
        # handle list
        if type(iv_corrs) is list:
            iv_corrs = np.array(iv_corrs)

        # update initial values with correlations
        if not decoupled:
            iv = np.concatenate((iv, iv_corrs.ravel()), dtype=np.float_)

        # initialize ODE solver
        ode_solver = ODESolver(
            func=func_ode_modes_corrs,
            params=self.params,
            cb_update=self.updater.cb_update
        )
        # solve ODE
        vs = ode_solver.solve(
            T=self.T,
            iv=iv,
            c=c
        )
            
        # handle double functions (feedback support)
        if decoupled:
            # update modes
            Modes_real = np.float_(vs)

            # display completion
            if show_progress:
                self.updater.update_info(
                    status="-" * 42 + "Modes Obtained"
                )

            # update initial values and constants
            c_corrs = np.concatenate((c, iv), dtype=np.float_)
            
            # function for variable constants 
            def func_c(i):
                """Function to update the constants of the integration.
                
                Returns
                -------
                i : int
                    Index of the element in ``T``.
                
                Returns
                -------
                c_corrs : numpy.ndarray
                    Updated constants.
                """
                
                # update constants
                c_corrs[len(c):len(c) + 2 * self.system.num_modes] = Modes_real[i - self.params['t_index_delay'], :] if self.params['t_index_delay'] > i else 0.0

                return c_corrs

            # initialize ODE solver
            ode_solver = ODESolver(
                func=func_ode_corrs,
                params=self.params,
                cb_update=self.updater.cb_update
            )
            # solve ODE
            Corrs_flat = np.float_(ode_solver.solve(
                T=self.T,
                iv=iv_corrs.flatten(),
                c=c_corrs,
                func_c=func_c
            ))
                
            # update results
            self.results= {
                'T': self.T,
                'V': np.concatenate((Modes_real, Corrs_flat), axis=1, dtype=np.float_)
            }
            
            # display completion
            if show_progress:
                self.updater.update_info(
                    status="-" * 35 + "Correlations Obtained"
                )
        else:
            # update results
            self.results= {
                'T': self.T,
                'V': np.float_(vs)
            }

            # display completion
            if show_progress:
                self.updater.update_info(
                    status="-" * 40 + "Results Obtained"
                )

    def solve(self, func_ode_modes_corrs, iv_modes, iv_corrs, c=None, func_ode_corrs=None):
        """Method to solve the HLEs.

        Loads solutions if disk cache is found, else solves and saves the solutions to disk cache.

        Parameters
        ----------
        func_ode_modes_corrs : callable
            Function returning the rate equations of the modes and correlations. If ``func_ode_corrs`` parameter is given, this function is treated as the function for the modes only. Refer to :class:`qom.systems.base.BaseSystem` for their implementations.
        iv_modes : list or numpy.ndarray
            Initial values for the modes.
        iv_corrs : list or numpy.ndarray
            Initial values for the correlations.
        c : list or numpy.ndarray
            Derived constants and controls for the function.
        func_ode_corrs : callable
            Function returning the rate equations of the correlations.

        Returns
        -------
        results : dict
            Results obtained after solving, with keys ``'T'`` and ``'V'`` for times and values.
        """

        # extract frequently used variables
        cache_path = self.cache_dir + '/' + self.cache_file
        show_progress = self.params['show_progress']
        
        # load results from compressed file
        if self.cache and self.updater.exists(
            file_path=cache_path
        ):
            self.results = {
                'T': self.T,
                'V': self.updater.load(
                    file_path=cache_path
                )
            }

            # display loaded
            if show_progress:
                self.updater.update_info(
                    status="-" * 42 + "Results Loaded"
                )
        else:
            # solve
            self.set_results(
                func_ode_modes_corrs=func_ode_modes_corrs,
                iv_modes=iv_modes,
                iv_corrs=iv_corrs,
                c=c,
                func_ode_corrs=func_ode_corrs
            )
            # save
            if self.cache:
                # update directories
                self.updater.create_directory(
                    file_path=cache_path
                )

                # save to compressed file
                self.updater.save(
                    file_path=cache_path,
                    array=self.results['V']
                )
            
                # display saved
                if show_progress:
                    self.updater.update_info(
                        status="-" * 43 + "Results Saved",
                    )

        return self.results

    def get_all_modes_corrs(self):
        """Method to obtain all the modes and correlations.

        Requires predefined system callables ``get_ivc`` and ``func_ode_modes_corrs``. Alternatively, if the system inherits :class:`qom.systems.base.BaseSystem`, ``get_mode_rates`` may be defined along with ``get_A`` and ``get_D`` if correlations are present. Additionally, ``func_ode_corrs`` may be defined for dynamical values (refer to the ``solve`` method). Refer to :class:`qom.systems.base.BaseSystem` for their implementations.

        Returns
        -------
        Modes : numpy.ndarray
            All the modes calculated at all times.
        Corrs : numpy.ndarray
            All the correlations calculated at all times.
        """

        # if already calculated
        if (self.Modes is not None or self.Corrs is not None) and self.T is not None:
            return self.Modes, self.Corrs

        # validate system
        validate_system(
            system=self.system,
            required_system_attributes=['num_modes', 'dim_corrs', 'get_ivc']
        )

        # get initial values and constants
        iv_modes, iv_corrs, c = self.system.get_ivc()
        
        # solve and set results
        self.solve(
            func_ode_modes_corrs=self.system.func_ode_modes_corrs,
            iv_modes=iv_modes,
            iv_corrs=iv_corrs,
            c=c,
            func_ode_corrs=self.system.func_ode_corrs if getattr(self.system, 'func_ode_corrs', None) is not None else None
        )

        # get modes, correlations and times
        return self.get_all_modes(), self.get_all_corrs()

    def get_all_modes(self):
        """Method to obtain all the modes.

        Requires predefined system callables ``get_ivc`` and ``func_ode_modes_corrs``. Alternatively, if the system inherits :class:`qom.systems.base.BaseSystem`, ``get_mode_rates`` may be defined along with ``get_A`` and ``get_D`` if correlations are present. Additionally, ``func_ode_corrs`` may be defined for dynamical values (refer to the ``solve`` method). Refer to :class:`qom.systems.base.BaseSystem` for their implementations.
        
        Returns
        -------
        Modes : numpy.ndarray
            All the modes calculated at all times.
        """

        # solve if results not found
        if getattr(self, 'results', None) is None:
            self.get_all_modes_corrs()

        # modes loaded or solved using single ODE function
        if self.Modes is not None:
            return self.Modes

        # update modes
        self.Modes = self.results['V'][:, :self.system.num_modes] + 1.0j * self.results['V'][:, self.system.num_modes:2 * self.system.num_modes]
            
        return self.Modes

    def get_all_corrs(self):
        """Method to obtain all the correlations.

        Requires predefined system callables ``get_ivc`` and ``func_ode_modes_corrs``. Alternatively, if the system inherits :class:`qom.systems.base.BaseSystem`, ``get_mode_rates`` may be defined along with ``get_A`` and ``get_D`` if correlations are present. Additionally, ``func_ode_corrs`` may be defined for dynamical values (refer to the ``solve`` method). Refer to :class:`qom.systems.base.BaseSystem` for their implementations.
        
        Returns
        -------
        Corrs : numpy.ndarray
            All the correlations calculated at all times.
        """

        # solve if results not found
        if getattr(self, 'results', None) is None:
            self.get_all_modes_corrs()

        # correlations loaded or solved using single ODE function
        if self.Corrs is not None:
            return self.Corrs

        # update correlations
        if len(self.results['V'][0]) > 2 * self.system.num_modes:
            self.Corrs = np.reshape(self.results['V'][:, 2 * self.system.num_modes:], (len(self.T), self.system.dim_corrs[0], self.system.dim_corrs[1]))
        else:
            self.Corrs = None
            
        return self.Corrs

    def get_times(self):
        """Method to obtain the times in the given range.
        
        Returns
        -------
        T : numpy.ndarray
            Times in the given range.
        """

        return self.T[self.params['t_index_min']:self.params['t_index_max'] + 1]

    def get_modes_corrs(self):
        """Method to obtain the dynamics of the modes and correlations in a given range of time.

        Requires predefined system callables ``get_ivc`` and ``func_ode_modes_corrs``. Alternatively, if the system inherits :class:`qom.systems.base.BaseSystem`, ``get_mode_rates`` may be defined along with ``get_A`` and ``get_D`` if correlations are present. Additionally, ``func_ode_corrs`` may be defined for dynamical values (refer to the ``solve`` method). Refer to :class:`qom.systems.base.BaseSystem` for their implementations.

        Returns
        -------
        Modes : numpy.ndarray
            All the modes calculated in a given range of time.
        Corrs : numpy.ndarray
            All the correlations calculated in a given range of time.
        """

        # extract frequently used variables
        _min    = self.params['t_index_min']
        _max    = self.params['t_index_max']

        # get modes, correlations and times
        return self.get_all_modes()[_min:_max + 1], self.get_all_corrs()[_min:_max + 1]

    def get_modes(self):
        """Method to obtain the dynamics of the modes in a given range of time.

        Requires predefined system callables ``get_ivc`` and ``func_ode_modes_corrs``. Alternatively, if the system inherits :class:`qom.systems.base.BaseSystem`, ``get_mode_rates`` may be defined along with ``get_A`` and ``get_D`` if correlations are present. Additionally, ``func_ode_corrs`` may be defined for dynamical values (refer to the ``solve`` method). Refer to :class:`qom.systems.base.BaseSystem` for their implementations.

        Returns
        -------
        Modes : numpy.ndarray
            All the modes calculated in a given range of time.
        """

        # get modes, correlations and times
        return self.get_all_modes()[self.params['t_index_min']:self.params['t_index_max'] + 1]
    
    def get_corrs(self):
        """Method to obtain the dynamics of the correlations in a given range of time.

        Requires predefined system callables ``get_ivc`` and ``func_ode_modes_corrs``. Alternatively, if the system inherits :class:`qom.systems.base.BaseSystem`, ``get_mode_rates`` may be defined along with ``get_A`` and ``get_D`` if correlations are present. Additionally, ``func_ode_corrs`` may be defined for dynamical values (refer to the ``solve`` method). Refer to :class:`qom.systems.base.BaseSystem` for their implementations.

        Returns
        -------
        Corrs : numpy.ndarray
            All the correlations calculated in a given range of time.
        """

        # get modes, correlations and times
        return self.get_all_corrs()[self.params['t_index_min']:self.params['t_index_max'] + 1]
    
    def get_mode_indices(self):
        """Method to obtain the specific modes in a given range of time.
        
        Returns
        -------
        Modes : numpy.ndarray
            Specific modes in a given range of time.
        """

        # validate indices
        _indices = self.params['indices']
        assert type(_indices) is list or type(_indices) is tuple, "Value of key ``'indices'`` can only be of types ``list`` or ``tuple``"
        # convert to list
        _indices = list(_indices) if type(_indices) is tuple else _indices
        # check range
        for index in _indices:
            assert index < self.system.num_modes, "Elements of key ``'indices'`` cannot exceed the total number of modes ({})".format(self.system.num_modes)
            
        return self.get_all_modes()[self.params['t_index_min']:self.params['t_index_max'] + 1, _indices]
    
    def get_mode_intensities(self):
        """Method to obtain the intensities of specific modes.

        Returns
        -------
        intensities : numpy.ndarray
            The intensities of specific modes.
        """

        # mode intensities
        return np.absolute(self.get_mode_indices())**2

    def get_corr_indices(self):
        """Method to obtain the specific correlations in a given range of time.
        
        Returns
        -------
        Corrs : numpy.ndarray
            Specific correlations in a given range of time.
        """

        # validate indices
        _Indices = self.params['indices']
        assert type(_Indices) is list, "Value of key ``'indices'`` can only be of type ``list``"
        # check range
        for _indices in _Indices:
            assert (type(_indices) is list or type(_indices) is tuple) and len(_indices) == 2, "Elements in value of key ``'indices'`` can only be of types ``list`` or ``tuple`` of size 2"
            assert _indices[0] < 2 * self.system.num_modes and _indices[1] < 2 * self.system.num_modes, "Elements in value of key ``'indices'`` cannot exceed twice the total number of modes ({})".format(2 * self.system.num_modes)

        # format indices
        _Indices = np.array(_Indices, dtype=np.int8)
            
        return self.get_all_corrs()[self.params['t_index_min']:self.params['t_index_max'] + 1, _Indices[:, 0], _Indices[:, 1]]
    
class SSHLESolver():
    r"""Class to solve the steady state Heisenberg-Langevin equations for classical mode amplitudes and quantum quadrature correlations.

    Initializes ``system``, ``params``, ``Modes``, ``Corrs``, ``As``, ``Ds``, ``Measures`` and ``updater``.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system methods for certain solver methods.
    params : dict
        Parameters for the solver. Refer to **Notes** below for all available options.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Notes
    -----
        The ``params`` dictionary currently supports the following keys:
            ====================    ====================================================
            key                     value
            ====================    ====================================================
            'show_progress'         (*bool*) option to display the progress of the solver. Default is ``False``.
            'indices'               (*list* or *tuple*) indices of the modes as a list or tuple of two integers. Default is ``[0]``.
            'use_system_method'     (*bool*) option to use the system method ``get_modes_steady_state`` to obtain the steady state mode amplitudes. Requires the predefined system method ``get_coeffs_N_o`` if the system method implements ``get_mean_optical_occupancies``. Default is ``True``.
            ====================    ====================================================
    """

    # attributes
    name = 'SSHLESolver'
    """str : Name of the solver."""
    desc = "Steady State Heisenberg-Langevin Equations Solver"
    """str : Description of the solver."""
    solver_defaults = {
        'show_progress': False,
        'indices': [0],
        'use_system_method': True
    }
    """dict : Default parameters of the solver."""

    def __init__(self, system, params:dict, cb_update=None):
        """Class constructor for SSESolver."""
        
        # set constants
        self.system = system

        # set parameters
        self.set_params(params)

        # initialize variables
        self.Modes = None
        self.Corrs = None
        self.As = None
        self.Ds = None
        self.Measures = None

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.solvers.SSHLESolver'),
            cb_update=cb_update
        )

    def set_params(self, params):
        """Method to validate and set the solver parameters.
        
        Parameters
        ----------
        params : *dict*
            Parameters of the solver.
        """

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])
     
    def get_modes_corrs(self):
        """Method to obtain the steady states of the modes and correlations.

        Requires system method ``get_ivc`` to obtain the derived constants and controls ``c``. To calculate the modes, either ``get_modes_steady_state`` or ``get_mode_rates`` should be defined. Priority is given to ``get_modes_steady_state``. The correlations are calculated by solving the Lyapunov equation. For this, the ``get_A`` and ``get_D`` methods should be defined along with the method required to calculate the modes.

        Returns
        -------
        Modes : numpy.ndarray
            Modes calculated at steady-state.
        Corrs : numpy.ndarray
            Correlations calculated at steady-state.
        """

        # validate system
        validate_system(
            system=self.system,
            required_system_attributes=['num_modes', 'dim_corrs', 'get_ivc']
        )

        # get initial values, derived constants and controls
        iv_modes, _, c = self.system.get_ivc()

        # if steady states expressions are given
        if self.params['use_system_method'] and getattr(self.system, 'get_modes_steady_state', None) is not None:
            self.Modes = np.array(self.system.get_modes_steady_state(
                c=c
            ), dtype=np.complex_)
        # if modes are to be calculated
        elif getattr(self.system, 'get_mode_rates', None) is not None and iv_modes is not None and len(iv_modes) > 0:
            # get real-valued modes
            iv_modes_real = np.concatenate((np.real(iv_modes), np.imag(iv_modes)), dtype=np.float_)
            # solve for modes
            modes_real = so.fsolve(
                func=self.system.get_mode_rates_real,
                x0=iv_modes_real,
                args=(c, None, )
            )
            modes = modes_real[:self.system.num_modes] + 1.0j * modes_real[self.system.num_modes:]

            # set result
            self.Modes = np.array([modes], dtype=np.complex_)

        # if correlations are required
        if self.system.A is not None and self.system.D is not None:
            # frequently used variables
            _dim = len(self.Modes) if self.Modes is not None else 1
            
            # initialize matrices
            self.As     = np.zeros((_dim, ) + self.system.dim_corrs, dtype=np.float_)
            self.Ds     = np.zeros((_dim, ) + self.system.dim_corrs, dtype=np.float_)
            self.Corrs  = np.zeros((_dim, ) + self.system.dim_corrs, dtype=np.float_)

            # solver for each set of modes
            for i in range(_dim):
                # set drift matrix
                self.As[i] = copy.deepcopy(self.system.get_A(
                    modes=self.Modes[i] if self.Modes is not None else None,
                    c=c,
                    t=None
                ))
                # set noise matrix
                self.Ds[i] = copy.deepcopy(self.system.get_D(
                    modes=self.Modes[i] if self.Modes is not None else None,
                    corrs=None,
                    c=c,
                    t=None
                ))
                # solve for correlations
                self.Corrs[i] = sl.solve_lyapunov(self.As[i], - self.Ds[i])
        
        return self.Modes, self.Corrs
    
    def get_modes(self):
        """Method to obtain the steady state modes.
        
        Returns
        -------
        Modes : numpy.ndarray
            Modes calculated at steady-state.
        """

        # modes already obtained
        if self.Modes is not None:
            return self.Modes
    
        # solve for and correlations
        self.get_modes_corrs()
            
        return self.Modes
    
    def get_corrs(self):
        """Method to obtain the steady state correlations.
        
        Returns
        -------
        Corrs : numpy.ndarray
            Correlations calculated at steady-state.
        """

        # correlations already obtained
        if self.Corrs is not None:
            return self.Corrs
    
        # solve for modes and correlations
        self.get_modes_corrs()
            
        return self.Corrs
    
    def get_mode_indices(self):
        """Method to obtain the steady states of specific modes.

        Returns
        -------
        modes : numpy.ndarray
            Specific modes calculated at steady-state.
        """

        # validate indices
        _indices = self.params['indices']
        assert type(_indices) is list or type(_indices) is tuple, "Value of key ``'indices'`` can only be of types ``list`` or ``tuple``"
        # convert to list
        _indices = list(_indices) if type(_indices) is tuple else _indices
        # check range
        for index in _indices:
            assert index < self.system.num_modes, "Elements of key ``'indices'`` cannot exceed the total number of modes ({})".format(self.system.num_modes)
        
        return self.get_modes()[:, _indices]
    
    def get_mode_intensities(self):
        """Method to obtain the intensities of specific modes.

        Returns
        -------
        intensities : numpy.ndarray
            The intensities of specific modes.
        """

        # mode intensities
        return np.absolute(self.get_mode_indices())**2
    
    def get_corr_indices(self):
        """Method to obtain the steady states of specific correlations.

        Returns
        -------
        corrs : numpy.ndarray
            Specific correlations calculated at steady-state.
        """

        # validate indices
        _Indices = self.params['indices']
        assert type(_Indices) is list, "Value of key ``'indices'`` can only be of type ``list``"
        # check range
        for _indices in _Indices:
            assert (type(_indices) is list or type(_indices) is tuple) and len(_indices) == 2, "Elements in value of key ``'indices'`` can only be of types ``list`` or ``tuple`` of size 2"
            assert _indices[0] < 2 * self.system.num_modes and _indices[1] < 2 * self.system.num_modes, "Elements in value of key ``'indices'`` cannot exceed twice the total number of modes ({})".format(2 * self.system.num_modes)

        # format indices
        _Indices = np.array(_Indices, dtype=np.int8)
        
        return self.get_corrs()[:, _Indices[:, 0], _Indices[:, 1]]
    
    def get_As(self):
        """Method to obtain the steady state drift matrices.
        
        Returns
        -------
        As : numpy.ndarray
            Drift matrices calculated at steady-state.
        """

        # matrices already obtained
        if self.As is not None:
            return self.As
    
        # solve for and correlations
        self.get_modes_corrs()
            
        return self.As
    
    def get_Ds(self):
        """Method to obtain the steady state noise matrices.
        
        Returns
        -------
        Ds : numpy.ndarray
            Noise matrices calculated at steady-state.
        """

        # matrices already obtained
        if self.Ds is not None:
            return self.Ds
    
        # solve for and correlations
        self.get_modes_corrs()
            
        return self.Ds

class LLESolver():
    """Method to solve the Lugiato-Lefever equation (LLE) for classical mode amplitudes using the split-step Fourier method.

    Initializes ``system``, ``params``, ``T``, ``Modes`` and ``updater``.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system methods for certain solver methods.
    params : dict
        Parameters for the solver. Refer to **Notes** below for all available options.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Notes
    -----
        The ``params`` dictionary  currently supports the following keys:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
            't_min'             (*float*) minimum time at which integration starts. Default is ``0.0``.
            't_max'             (*float*) maximum time at which integration stops. Default is ``1000.0``.
            't_dim'             (*int*) number of values from ``'t_max'`` to ``'t_min'``, both inclusive. Default is ``10001``.
            'indices'           (*list* or *tuple*) indices of the modes as a list. Default is ``[0]``.
            ================    ====================================================
    """

    # attributes
    name = 'LLESolver'
    """str : Name of the solver."""
    desc = "Lugiato-Lefever Equation Solver"
    """str : Description of the solver."""
    solver_defaults = {
        'show_progress': False,
        't_min': 0.0,
        't_max': 1000.0,
        't_dim': 10001,
        'indices': [0]
    }
    """dict : Default parameters of the solver."""

    def __init__(self, system, params:dict, cb_update=None):
        """Class constructor for LLESolver."""
        
        # set constants
        self.system = system

        # set parameters
        self.set_params(params)

        # set times
        self.T = get_all_times(self.params)

        # initialize variables
        self.Modes = None

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.solvers.LLESolver'),
            cb_update=cb_update
        )

    def set_params(self, params):
        """Method to validate and set the solver parameters and times.
        
        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # check required parameters
        t_keys = ['t_min', 't_max', 't_dim']
        for key in t_keys:
            assert key in params, "Parameter ``params`` does not contain the required key ``'{}'``"

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

    def get_all_modes(self):
        """Method to obtain all the modes.

        Requires predefined system callables ``get_ivc``, ``get_coeffs_dispersion``, ``get_nonlinearities`` and ``get_sources``. Refer to :class:`qom.systems.base.BaseSystem` for their implementations.
        
        Returns
        -------
        Modes : numpy.ndarray
            All the modes calculated at all times.
        """

        # validate system
        validate_system(
            system=self.system,
            required_system_attributes=['num_modes', 'get_ivc', 'get_coeffs_dispersion', 'get_nonlinearities', 'get_sources']
        )

        # extract frequently used variables
        show_progress = self.params['show_progress']
        t_dim = self.params['t_dim']
        t_ss = self.T[1] - self.T[0]
    
        # initialize variables
        modes, _, c = self.system.get_ivc()
        Modes = np.zeros((t_dim, self.system.num_modes), dtype=np.complex_)
        Modes[0] = modes
        N = int(self.system.num_modes / 2)
        omegas = 2.0 * np.pi * np.linspace(- 1.0, 1.0 - 2.0 / N, N) / 2.0

        for i in range(1, t_dim):
            # update progress
            if show_progress:
                self.updater.update_progress(
                    pos=i,
                    dim=t_dim,
                    status="-" * 14 + "Obtaining the dynamics",
                    reset=False
                )

            # get nonlinearities
            nonlinearities = self.system.get_nonlinearities(
                modes=modes,
                c=c,
                t=self.T[i]
            )
            # get dispersions
            coeffs_dispersion = self.system.get_coeffs_dispersion(
                modes=modes,
                c=c,
                t=self.T[i]
            )
            dispersions = np.sum([coeffs_dispersion[i] * (1.0j * omegas)**i for i in range(len(coeffs_dispersion))], axis=0)
            # get sources
            sources = self.system.get_sources(
                modes=modes,
                c=c,
                t=self.T[i]
            )

            # apply nonlinearity
            alpha_nls = np.exp(nonlinearities * t_ss) * (modes[::2] + sources / nonlinearities) - sources / nonlinearities

            # apply dispersion
            alpha_tildes = sf.fftshift(sf.fft(alpha_nls))
            alpha_tildes = np.exp(dispersions * t_ss) * alpha_tildes
            modes[::2] = sf.ifft(sf.fftshift(alpha_tildes))

            # update modes
            Modes[i] = modes

        # display completion
        if show_progress:
            self.updater.update_progress(
                pos=1,
                dim=1,
                status="-" * 14 + "Obtaining the dynamics",
                reset=False
            )
            self.updater.update_info(
                status="-" * 39 + "Dynamics Obtained"
            )

        return Modes
    
    def get_mode_indices(self):
        """Method to obtain the specific modes in a given range of time.
        
        Returns
        -------
        Modes : numpy.ndarray
            Specific modes in a given range of time.
        """

        # validate indices
        _indices = self.params['indices']
        assert type(_indices) is list or type(_indices) is tuple, "Value of key ``'indices'`` can only be of types ``list`` or ``tuple``"
        # convert to list
        _indices = list(_indices) if type(_indices) is tuple else _indices
        # check range
        for index in _indices:
            assert index < self.system.num_modes, "Elements of key ``'indices'`` cannot exceed the total number of modes ({})".format(self.system.num_modes)
            
        return self.get_all_modes()[:, _indices]
    
    def get_mode_intensities(self):
        """Method to obtain the intensities of specific modes.

        Returns
        -------
        intensities : numpy.ndarray
            The intensities of specific modes.
        """

        # mode intensities
        return np.absolute(self.get_mode_indices())**2
    
class NLSESolver():
    """Method to solve the non-linear Schrodinger equation (NLSE) using the split-step Fourier method.

    Initializes ``system``, ``params``, ``T``, ``Modes`` and ``updater``.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system methods for certain solver methods.
    params : dict
        Parameters for the solver. Refer to **Notes** below for all available options.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Notes
    -----
        The ``params`` dictionary  currently supports the following keys:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
            'update_betas'      (*bool*) option to use the mechanical mode rates. Requires either one of the predefined system methods ``get_beta_rates`` (priority) or ``get_betas`` (fallback). Refer to :class:`qom.systems.base.BaseSystem` for their implementations. Default is ``False``.
            'use_sources'       (*bool*) option to use the source terms. Requires the predefined system method ``get_sources``. Refer to :class:`qom.systems.base.BaseSystem` for its implementation. Default is ``True``.
            'ode_method'        (*str*) method used to solve the ODEs. Available options are ``'BDF'``, ``'DOP853'``, ``'LSODA'``, ``'Radau'``, ``'RK23'``, ``'RK45'`` (fallback), ``'dop853'``, ``'dopri5'``, ``'lsoda'``, ``'vode'`` and ``'zvode'``. Refer to :class:`qom.solvers.differential.ODESolver` for details of each method. Default is ``'RK45'``.
            'ode_is_stiff'      (*bool*) option to select whether the integration is a stiff problem or a non-stiff one. Default is ``False``.
            'ode_atol'          (*float*) absolute tolerance of the integrator. Default is ``1e-12``.
            'ode_rtol'          (*float*) relative tolerance of the integrator. Default is ``1e-6``.
            't_min'             (*float*) minimum time at which integration starts. Default is ``0.0``.
            't_max'             (*float*) maximum time at which integration stops. Default is ``1000.0``.
            't_dim'             (*int*) number of values from ``'t_max'`` to ``'t_min'``, both inclusive. Default is ``10001``.
            't_div'             (*int*) number of further divisions in each time step, both inclusive. Default is ``1``.
            'indices'           (*list* or *tuple*) indices of the modes as a list. Default is ``[0]``.
            ================    ====================================================
    """

    # attributes
    name = 'NLSESolver'
    """str : Name of the solver."""
    desc = "Non-linear Schrodinger Equation Solver"
    """str : Description of the solver."""
    solver_defaults = {
        'show_progress': False,
        'update_betas': True,
        'use_sources': False,
        'ode_method': 'RK45',
        'ode_is_stiff': False,
        'ode_atol': 1e-12,
        'ode_rtol': 1e-6,
        't_min': 0.0,
        't_max': 1000.0,
        't_dim': 10001,
        't_div': 1,
        'indices': [0]
    }
    """dict : Default parameters of the solver."""

    def __init__(self, system, params:dict, cb_update=None):
        """Class constructor for LLESolver."""
        
        # set constants
        self.system = system

        # set parameters
        self.set_params(params)

        # set times
        self.T = get_all_times(self.params)

        # initialize variables
        self.Modes = None

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.solvers.NLSESolver'),
            cb_update=cb_update
        )

    def set_params(self, params):
        """Method to validate and set the solver parameters and times.
        
        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # check required parameters
        t_keys = ['t_min', 't_max', 't_dim']
        for key in t_keys:
            assert key in params, "Parameter ``params`` does not contain the required key ``'{}'``"

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

    def get_all_modes(self):
        """Method to obtain all the modes.

        Requires predefined system callables ``get_ivc``, ``get_coeffs_dispersion`` and ``get_nonlinearities``. Either one of the callables ``get_beta_rates`` or ``get_betas`` may also be defined to update the mechanical mode rates. Additionally ``get_sources`` may be defined to include source terms. Refer to :class:`qom.systems.base.BaseSystem` for their implementations.
        
        Returns
        -------
        Modes : numpy.ndarray
            All the modes calculated at all times.
        """

        # validate system
        validate_system(
            system=self.system,
            required_system_attributes=['num_modes', 'get_ivc', 'get_coeffs_dispersion', 'get_nonlinearities']
        )

        # extract frequently used variables
        show_progress = self.params['show_progress']
        update_betas = self.params['update_betas']
        use_sources = self.params['use_sources']
        t_dim = self.params['t_dim']
        t_ss = self.T[1] - self.T[0]

        assert (getattr(self.system, 'get_beta_rates', None) is not None or getattr(self.system, 'get_betas', None) is not None) if update_betas else True, "Either one of the system methods ``get_beta_rates`` or ``update_betas`` are required when parameter ``'update_betas'`` is set to ``True``."

        assert getattr(self.system, 'get_sources', None) is not None if use_sources else True, "System method ``get_sources`` is required when parameter ``'use_sources'`` is set to ``True``."

        # initialize variables
        modes, _, c = self.system.get_ivc()
        Modes = np.zeros((t_dim, self.system.num_modes), dtype=np.complex_)
        Modes[0] = modes
        N = int(self.system.num_modes / 2)
        omegas = 2.0 * np.pi * np.linspace(- 1.0, 1.0 - 2.0 / N, N) / 2.0

        for i in range(1, t_dim):
            # update progress
            if show_progress:
                self.updater.update_progress(
                    pos=i,
                    dim=t_dim,
                    status="-" * 13 + "Obtaining the dynamics",
                    reset=False
                )

            # get nonlinearities
            nonlinearities = self.system.get_nonlinearities(
                modes=modes,
                c=c,
                t=self.T[i]
            )
            # get dispersion coefficients
            coeffs_dispersion = self.system.get_coeffs_dispersion(
                modes=modes,
                c=c,
                t=self.T[i]
            )
            # get dispersions
            dispersions = np.sum([coeffs_dispersion[i] * (1.0j * omegas)**i for i in range(len(coeffs_dispersion))], axis=0)
            # get sources
            sources = self.system.get_sources(
                modes=modes,
                c=c,
                t=self.T[i]
            ) if use_sources else 0.0
            
            # apply dispersion for dt / 2
            alphas_ps = sf.fftshift(sf.fft(modes[::2]))
            temp = np.exp(dispersions * t_ss / 2.0) * alphas_ps
            modes[::2] = sf.ifft(sf.fftshift(temp))

            # apply nonlinearity for dt
            modes[::2] = np.exp(nonlinearities * t_ss) * (modes[::2] + sources / nonlinearities) - sources / nonlinearities
            
            # apply dispersion for dt / 2
            alphas_ps = sf.fftshift(sf.fft(modes[::2]))
            temp = np.exp(dispersions * t_ss / 2.0) * alphas_ps
            modes[::2] = sf.ifft(sf.fftshift(temp))

            # update mechanical modes
            if update_betas:
                if getattr(self.system, 'get_beta_rates', None) is not None:
                    # function to obtain the real-valued beta rates
                    def func_ode(t, v, c):
                        # get complex-valued betas
                        modes[1::2] = v[:int(len(v) / 2)] + 1.0j * v[int(len(v) / 2):]

                        # get complex-valued beta rates
                        beta_rates = self.system.get_beta_rates(
                            modes=modes,
                            c=c,
                            t=t
                        )

                        # return real-valued beta rates
                        return np.concatenate((np.real(beta_rates), np.imag(beta_rates)), dtype=np.float_)
                    
                    # initialize solver
                    solver = ODESolver(
                        func=func_ode,
                        params=self.params,
                        cb_update=self.updater.cb_update
                    )
                    # update solver parameters
                    solver.params['show_progress'] = False

                    # get real-valued betas
                    v = solver.solve(
                        T=[self.T[i], self.T[i] + t_ss],
                        iv=np.concatenate((np.real(modes[1::2]), np.imag(modes[1::2])), dtype=np.float_),
                        c=c,
                        func_c=None
                    )[-1]

                    # update complex-valued modes
                    modes[1::2] = v[:int(len(v) / 2)] + 1.0j * v[int(len(v) / 2):]
                else:
                    # function to get betas
                    modes[1::2] = self.system.get_betas(
                        modes=modes,
                        c=c,
                        t=self.T[i]
                    )
            
            # update modes
            Modes[i] = modes

        # display completion
        if show_progress:
            self.updater.update_progress(
                pos=1,
                dim=1,
                status="-" * 13 + "Obtaining the dynamics",
                reset=False
            )
            self.updater.update_info(
                status="-" * 38 + "Dynamics Obtained"
            )

        return Modes
    
    def get_mode_indices(self):
        """Method to obtain the specific modes in a given range of time.
        
        Returns
        -------
        Modes : numpy.ndarray
            Specific modes in a given range of time.
        """

        # validate indices
        _indices = self.params['indices']
        assert type(_indices) is list or type(_indices) is tuple, "Value of key ``'indices'`` can only be of types ``list`` or ``tuple``"
        # convert to list
        _indices = list(_indices) if type(_indices) is tuple else _indices
        # check range
        for index in _indices:
            assert index < self.system.num_modes, "Elements of key ``'indices'`` cannot exceed the total number of modes ({})".format(self.system.num_modes)
            
        return self.get_all_modes()[:, _indices]
    
    def get_mode_intensities(self):
        """Method to obtain the intensities of specific modes.

        Returns
        -------
        intensities : numpy.ndarray
            The intensities of each mode.
        """

        # mode intensities
        return np.absolute(self.get_mode_indices())**2