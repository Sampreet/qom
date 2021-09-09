#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module for utility functions to wrap subpackages."""

__name__    = 'qom.utils.looper'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-05-25'
__updated__ = '2021-09-09'

# qom modules
from ..ui import init_log
from ..loopers import XLooper, XYLooper, XYZLooper

default_looper_func_names = {
    'averaged_eigenvalues': 'aes',
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
            "les"       Lyapunov exponents.
            "moo"       mean optical occupancies.
            "mav"       measure averages.
            "mdy"       measure dynamics.
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
            system = SystemClass(system_params)
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

    if func_code in default_looper_func_names:
        func_code = default_looper_func_names[func_code]

    func = {
        'aes': get_func_solver_params('averaged_eigenvalues'),
        'les': get_func_solver_params('lyapunov_exponents'),
        'mav': get_func_solver_params('measure_average'),
        'mdy': get_func_solver_params('measure_dynamics'),
        'mss': get_func_solver_params('measure_stationary'),
        'moo': func_mean_optical_occupanies,
        'osz': get_func_solver_params('optical_stability_zone'),
        'pcc': get_func_solver_params('pearson_correlation_coefficient')
    }.get(func_code, get_func_params(func_code))

    return func

def wrap_looper(SystemClass, params: dict, func, looper, file_path: str=None, plot: bool=False, hold: bool=True, width: float=5.0, height: float=5.0):
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
            "les"           Lyapunov exponents.
            "mav"           measure averages (fallback).
            "mdy"           measure dynamics.
            "moo"           mean optical occupancies.
            "pcc"           Pearson correlation factor.
            ==============  ================================================
    looper : str or class
        Code of the looper or the looper class. Available loopers names are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            "x_looper"       1D looper (:class:`qom.loopers.XLooper`) (fallback).
            "xy_looper"      2D looper (:class:`qom.loopers.XYLooper`).
            "xyz_looper"     3D looper (:class:`qom.loopers.XYZLooper`).
            ==============  ================================================
    file_path : str, optional
        Path and prefix of the .npz file.
    plot: bool, optional
        Option to plot the results.
    hold : bool, optional
        Option to hold the plot.
    width : float, optional
        Width of the figure.
    height : float, optional
        Height of the figure.

    Returns
    -------
    looper : :class:`qom.loopers.*`
        Instance of the looper.
    """
    
    # initialize logger
    init_log()

    # select function
    if type(func) is str:
        func = get_looper_func(SystemClass=SystemClass, solver_params=params.get('solver', {}), func_code=func)

    # select looper
    if type(looper) is str:
        if looper == 'xy_looper':
            looper = XYLooper(func, params)
        elif looper == 'xyz_looper':
            looper = XYZLooper(func, params)
        else:
            looper = XLooper(func, params)
        
    # wrap looper
    looper.wrap(file_path=file_path, plot=plot, hold=hold, width=width, height=height)

    return looper