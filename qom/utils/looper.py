#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dependencies
import concurrent.futures as cf
import copy
import logging
import multiprocessing as mp
import numpy as np
import os
import time
 
"""Module containing utility functions for loopers."""

__name__    = 'qom.utils.looper'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-05-25'
__updated__ = '2023-01-29'

# qom modules
from ..ui import init_log
from ..loopers import XLooper, XYLooper, XYZLooper

# module_logger
logger = logging.getLogger(__name__)

default_looper_func_names = {
    'averaged_eigenvalues': 'aes',
    'classical_amplitude_difference': 'cad',
    'classical_phase_difference': 'cpd',
    'lyapunov_exponents': 'les', 
    'mean_optical_occupancies': 'moo',
    'measure_average': 'mav',
    'measure_dynamics': 'mdy',
    'measure_stationary': 'mss',
    'optical_stability_zone': 'osz',
    'pearson_correlation_coefficient': 'pcc'
}

def get_looper_func(SystemClass, solver_params: dict, func_code: str):
    """Function to obtain to the looper function.

    Requires already defined callables ``func_ode``, ``get_mode_rates``, ``get_ivc``, ``get_A`` and ``get_oss_args`` inside the system class.
    
    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Class containing the system.
    solver_params : dict
        All parameters of the solver.
    func_code : str or callable
        Codename of the  default function or the name of the function to loop, following the format defined in :class:`qom.loopers.BaseLooper`. If ``func_code`` is not among the default ones, the same is requared as a predefined function. Default function codes are:
            ==========  ================================================
            value       meaning
            ==========  ================================================
            "aes"       averaged eigenvalue of the drift matrix.
            "cad"       classical amplitude difference.
            "cpd"       classical phase difference.
            "les"       Lyapunov exponents.
            "mav"       measure averages.
            "mdy"       measure dynamics.
            "moo"       mean optical occupancies.
            "mss"       stationary measure.
            "osz"       optical stability zone.
            "pcc"       Pearson correlation factor.
            ==========  ================================================
    """

    # function to calculate mean optical occupancies
    def func_mean_optical_occupanies(system_params, val, logger, results):
        # initialize system
        system = SystemClass(system_params)
        # get mean optical occupancies
        moo, _ = system.get_mean_optical_occupancies()
        # update results
        results.append((val, moo))

    # function to return a function to calculate
    def get_func_solver_params(func_name):
        # function to calculate
        def func_solver_params(system_params, val, logger, results):
            # initialize system
            system = SystemClass(params=system_params)
            # get value
            value = getattr(system, 'get_' + func_name)(solver_params=solver_params)
            # update results
            results.append((val, value))

        return func_solver_params

    # function to return a function to calculate
    def get_func_params(func_name):
        # functio to calculate
        def func_params(system_params, val, logger, results):
            # initialize system
            system = SystemClass(system_params)
            # extract parameters
            _, c = system.get_ivc()
            _len_D = 4 * system.num_modes**2
            params = c[_len_D:] if len(c) > _len_D else c
            # get value
            value = getattr(system, 'get_' + func_name)(params=params)
            # update results
            results.append((val, value))
        
        return func_params

    # if unabbreviated function name
    if func_code in default_looper_func_names:
        func_code = default_looper_func_names[func_code]

    # get function
    func = {
        'aes': get_func_solver_params('averaged_eigenvalues'),
        'cad': get_func_solver_params('classical_amplitude_difference'),
        'cpd': get_func_solver_params('classical_phase_difference'),
        'les': get_func_solver_params('lyapunov_exponents'),
        'mav': get_func_solver_params('measure_average'),
        'mdy': get_func_solver_params('measure_dynamics'),
        'moo': func_mean_optical_occupanies,
        'mss': get_func_solver_params('measure_stationary'),
        'osz': get_func_solver_params('optical_stability_zone'),
        'pcc': get_func_solver_params('pearson_correlation_coefficient')
    }.get(func_code, get_func_params(func_code))

    return func

def run_loopers_in_parallel(SystemClass, params: dict, func, looper, file_path_prefix: str=None, plot: bool=False, hold: bool=True, width: float=5.0, height: float=5.0, num_loopers: int=None):
    """Function to wrap loopers.

    Requires already defined callables ``func_ode``, ``get_mode_rates``, ``get_ivc``, ``get_A`` and ``get_oss_args`` inside the system class.
    
    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Class containing the system.
    params : dict
        All parameters as defined in :class:`qom.loopers.BaseLooper`.
    func : callable
        Function to loop, following the format defined in :class:`qom.loopers.BaseLooper`.
    looper : str
        Code of the looper. Available options are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            "XLooper"       1D looper (:class:`qom.loopers.XLooper`) (fallback).
            "XYLooper"      2D looper (:class:`qom.loopers.XYLooper`).
            "XYZLooper"     3D looper (:class:`qom.loopers.XYZLooper`).
            ==============  ================================================
    file_path_prefix : str, optional
        Path and prefix of the .npz file.
    plot : bool, optional
        Option to plot the results.
    hold : bool, optional
        Option to hold the plot.
    width : float, optional
        Width of the figure.
    height : float, optional
        Height of the figure.
    num_loopers : int, optional
        Number of loopers to run in parallel. The slicing of the values is performed on the first axis. If `None`, then the number slices are determined automatically, throttled by the number of available cores.

    Returns
    -------
    looper : :class:`qom.loopers.*`
        Instance of the looper.
    """

    # validate loopers
    assert looper in ['XLooper', 'XYLooper', 'XYZLooper'], 'Parameter ``looper`` should be either "XLooper", "XYLooper" or "XYZLooper"'

    # frequently used variables
    t_start = time.time()
    _s = 'Time Elapsed\t'
    parallel = True

    # initialize logger
    init_log(parallel=parallel)

    # initialize looper
    if 'XYZ' in looper:
        looper = XYZLooper(func=func, params=params, parallel=True)
        axis = 'Z'
    elif 'XY' in looper:
        looper = XYLooper(func=func, params=params, parallel=True)
        axis = 'Y'
    else:
        looper = XLooper(func=func, params=params, parallel=True)
        axis = 'X'

    # if save/load opted
    if file_path_prefix is not None:
        # load saved results and return looper
        if looper.load_results(file_path_prefix=file_path_prefix):
            # plot results
            if plot:
                looper.plot_results(hold=hold, width=width, height=height)

            return looper

    # extract axis values
    val = looper.axes[axis]['val']

    # handle null value or overflow
    if num_loopers is None or num_loopers > len(val) or num_loopers < 1:
        num_loopers = int(np.min([os.cpu_count() - 2, len(val)])) if len(val) > 1 else 1

    # maximum dimension of each slice
    slice_dim = int(np.ceil(len(val) / num_loopers))
    
    # handle corner case
    while slice_dim * (num_loopers - 1) >= len(val):
        num_loopers -= 1

    # initialize lists
    V = list()
    all_args = list()
        
    # slice and populate arguments
    for i in range(num_loopers):
        # duplicate parameters
        _params = copy.deepcopy(params)
        # update axis parameters
        _params['looper'][axis] = {
            'var': looper.axes[axis]['var'],
            'idx': looper.axes[axis]['idx'],
            'min': val[(i * slice_dim)],
            'max': val[(i + 1) * slice_dim - 1] if (i + 1) * slice_dim <= len(val) else val[-1],
            'dim': slice_dim if (i + 1) * slice_dim <= len(val) else len(val) - i * slice_dim
        }

        # update log string
        _s += looper.code + ' #' + str(i) + '\t'

        # update arguments
        all_args.append([SystemClass, _params, func, looper.code, file_path_prefix, plot, hold, width, height, parallel, t_start, i])

    # update log
    logger.info('\n' + _s + '\n')
        
    # multiprocess and join
    with cf.ProcessPoolExecutor(max_workers=num_loopers if num_loopers < os.cpu_count() else os.cpu_count() - 2, mp_context=mp.get_context('spawn')) as executor:
        _loopers = list(executor.map(run_wrap_looper_instance, all_args))
    
    # join list of values
    for _l in _loopers:
        V += _l.results['V']

    # update results
    looper.results = {
        'X': looper.axes['X']['val'],
        'Y': looper.axes['Y']['val'] if 'XY' in looper.code else None,
        'Z': looper.axes['Z']['val'] if 'XYZ' in looper.code else None,
        'V': V
    }

    # update log
    logger.info('\n')

    # save results
    if file_path_prefix is not None:
        looper.save_results(file_path_prefix=file_path_prefix)

    # plot results
    if plot:
        looper.plot_results(hold=hold, width=width, height=height)

    return looper

def run_wrap_looper_instance(args):
    '''Function to run a single instance of `wrap_looper`.
    
    Parameters
    ----------
    args : list
        Arguments of the `wrap_looper` function.

    Returns
    -------
    looper : :class:`qom.loopers.*`
        Instance of the looper.
    '''

    # extract arguments
    SystemClass, params, func, looper, file_path_prefix, plot, hold, width, height, parallel, p_start, p_index = args

    # return instance
    return wrap_looper(SystemClass=SystemClass, params=params, func=func, looper=looper, file_path_prefix=file_path_prefix, plot=plot, hold=hold, width=width, height=height, parallel=parallel, p_start=p_start, p_index=p_index)

def wrap_looper(SystemClass, params: dict, func, looper, file_path_prefix: str=None, plot: bool=False, hold: bool=True, width: float=5.0, height: float=5.0, parallel=False, p_start=time.time(), p_index=0):
    """Function to wrap loopers.

    Requires already defined callables ``func_ode``, ``get_mode_rates``, ``get_ivc``, ``get_A`` and ``get_oss_args`` inside the system class.
    
    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Class containing the system.
    params : dict
        All parameters as defined in :class:`qom.loopers.BaseLooper`.
    func : str or callable
        Code of the function or the function to loop, following the format defined in :class:`qom.loopers.BaseLooper`. Available function codes are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            "aes"           averaged eigenvalue of the drift matrix.
            "cad"           classical amplitude difference.
            "cpd"           classical phase difference.
            "les"           Lyapunov exponents.
            "mav"           measure averages (fallback).
            "mdy"           measure dynamics.
            "moo"           mean optical occupancies.
            "mss"           stationary measure.
            "osz"           optical stability zone.
            "pcc"           Pearson correlation factor.
            ==============  ================================================
    looper : str
        Code of the looper. Available options are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            "XLooper"       1D looper (:class:`qom.loopers.XLooper`) (fallback).
            "XYLooper"      2D looper (:class:`qom.loopers.XYLooper`).
            "XYZLooper"     3D looper (:class:`qom.loopers.XYZLooper`).
            ==============  ================================================
    file_path_prefix : str, optional
        Prefix of the file path.
    plot: bool, optional
        Option to plot the results.
    hold : bool, optional
        Option to hold the plot.
    width : float, optional
        Width of the figure.
    height : float, optional
        Height of the figure.
    parallel : bool, optional
        Option to format outputs when the looper is run in parallel.
    p_start : float, optional
        Time at which the process was started. If `None`, the value is initialized to current time.
    p_index : int, optional
        Index of the process.

    Returns
    -------
    looper : :class:`qom.loopers.*`
        Instance of the looper.
    """

    # initialize logger
    init_log(parallel=parallel)

    # select function
    if type(func) is str:
        func = get_looper_func(SystemClass=SystemClass, solver_params=params.get('solver', {}), func_code=func)

    # select looper
    if type(looper) is str:
        if looper == 'XYLooper':
            looper = XYLooper(func=func, params=copy.deepcopy(params), parallel=parallel, p_start=p_start, p_index=p_index)
        elif looper == 'XYZLooper':
            looper = XYZLooper(func=func, params=copy.deepcopy(params), parallel=parallel, p_start=p_start, p_index=p_index)
        else:
            looper = XLooper(func=func, params=copy.deepcopy(params), parallel=parallel, p_start=p_start, p_index=p_index)

    # wrap looper
    looper.wrap(file_path_prefix=file_path_prefix, plot=plot, hold=hold, width=width, height=height)

    return looper