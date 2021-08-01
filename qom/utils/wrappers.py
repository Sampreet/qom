#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module for utility functions to wrap subpackages."""

__name__    = 'qom.utils.wrappers'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-05-25'
__updated__ = '2021-08-01'

# dependencies
import numpy as np

# qom modules
from ..ui import init_log
from ..loopers import XLooper, XYLooper, XYZLooper

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
            "ams"           average of a measure (fallback).
            "dms"           dynamics of a measure.
            "les"           Lyapunov exponents.
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

    # function to calculate averaged eigenvalues of the drift matrix
    def func_aes(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get averaged eigenvalues
        aes = system.get_averaged_eigenvalues(solver_params=params['solver'], func_ode=system.func_ode, get_ivc=system.get_ivc, get_A=system.get_A)
        # update results
        results.append((val, [aes]))

    # function to calculate average of a measure
    def func_ams(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get measure average
        ams = system.get_measure_average(solver_params=params['solver'], func_ode=system.func_ode, get_ivc=system.get_ivc, get_A=system.get_A)
        # update results
        results.append((val, ams))

    # function to calculate dynamics of a measure
    def func_dms(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get measure dynamics
        dms, _ = system.get_measure_dynamics(solver_params=params['solver'], func_ode=system.func_ode, get_ivc=system.get_ivc, get_A=system.get_A)
        # update results
        results.append((val, [dms]))

    # function to obtain the maximum Lyapunov exponent
    def func_les(system_params, val, logger, results):
        # update system
        system = SystemClass(system_params)
        # get Lyapunov exponents
        les = system.get_lyapunov_exponents(solver_params=params['solver'], get_mode_rates=system.get_mode_rates, get_ivc=system.get_ivc, get_A=system.get_A)
        # update results
        results.append((val, [les]))

    # function to calculate mean optical occupancies
    def func_moo(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get mean optical occupancies
        moo, _ = system.get_mean_optical_occupancies(get_ivc=system.get_ivc, get_oss_args=system.get_oss_args)
        # update results
        results.append((val, [moo]))

    # function to calculate Pearson correlation coefficient
    def func_pcc(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get Pearson correlation coefficient
        pcc = system.get_pearson_correlation_coefficient(solver_params=params['solver'], func_ode=system.func_ode, get_ivc=system.get_ivc)
        # update results
        results.append((val, pcc))

    # select function
    if type(func) is str:
        func = {
            'aes': func_aes,
            'ams': func_ams,
            'dms': func_dms,
            'les': func_les, 
            'moo': func_moo,
            'pcc': func_pcc
        }.get(func, func_ams)

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