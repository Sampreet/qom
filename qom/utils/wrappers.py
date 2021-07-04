#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Utility functions to wrap subpackages."""

__name__    = 'qom.utils.wrappers'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-05-25'
__updated__ = '2021-07-04'

# dependencies
import numpy as np

# qom modules
from ..ui import init_log
from ..loopers import XLooper, XYLooper, XYZLooper

def wrap_looper(SystemClass, params: dict, func_name: str, looper_name: str, file_path: str=None, plot: bool=False, width: float=5.0, height: float=5.0):
    """Function to wrap loopers.
    
    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Class containing the system.
    params : dict
        All parameters.
    func_name : str
        Name of the function to loop. Available functions are:
            'eig_max': Maximum eigenvalue of the drift matrix.
            'measure_average': Average measure (fallback).
            'measure_dynamics': Dynamics of measure.
            'measure_pearson': Pearson synchronization measure.
    looper_name : str
        Name of the looper. Available loopers are:
            'XLooper': 1D looper (fallback).
            'XYLooper': 2D looper.
            'XYZLooper': 3D looper.
    file_path : str, optional
        Path and prefix of the .npz file.
    plot: bool, optional
        Option to plot the results.
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

    # function to calculate maximum eigenvalue of the drift matrix
    def func_eig_max(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get maximum eigenvalue
        eig_max = system.get_eig_max(params['solver'], system.ode_func, system.get_ivc, system.get_A)
        # update results
        results.append((val, eig_max))

    # function to calculate average measure
    def func_measure_average(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get average measure
        M_avg = system.get_measure_average(params['solver'], system.ode_func, system.get_ivc)
        # update results
        results.append((val, M_avg))

    # function to calculate measure dynamics
    def func_measure_dynamics(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get measure dynamics
        M, T = system.get_measure_dynamics(params['solver'], system.ode_func, system.get_ivc)
        # update results
        results.append((val, [M]))

    # function to calculate Pearson synchronization
    def func_measure_pearson(system_params, val, logger, results):
        # update parameters
        system = SystemClass(system_params)
        # get measure
        m = system.get_measure_pearson(params['solver'], system.ode_func, system.get_ivc)
        # update results
        results.append((val, m))

    # select function
    if func_name == 'eig_max':
        func = func_eig_max
    elif func_name == 'measure_dynamics':
        func = func_measure_dynamics
    elif func_name == 'measure_pearson':
        func = func_measure_pearson
    else:
        func = func_measure_average

    # select looper
    if looper_name == 'XYLooper':
        looper = XYLooper(func, params)
    elif looper_name == 'XYZLooper':
        looper = XYZLooper(func, params)
    else:
        looper = XLooper(func, params)
        
    # wrap looper
    looper.wrap(file_path, plot, width, height)

    return looper