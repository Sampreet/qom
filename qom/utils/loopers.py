#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module containing utility functions for loopers."""

__name__ = 'qom.utils.loopers'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-05-25"
__updated__ = "2023-07-12"

# dependencies
import concurrent.futures as cf
import copy
import logging
import multiprocessing as mp
import numpy as np
import os
import time

# qom modules
from ..loopers import XLooper, XYLooper, XYZLooper
from ..ui import init_log
from ..ui.plotters import MPLPlotter

# module_logger
logger = logging.getLogger(__name__)

# TODO: Support for updater callback in parallel loopers.

def run_loopers_in_parallel(looper_name:str, func, params:dict, params_system:dict, plot:bool=False, subplots:bool=False, params_plotter:dict={}, num_processes:int=None, cb_update=None):
    """Function to run multiple loopers in parallel processes.
    
    Parameters
    ----------
    looper_name : {``'XLooper'``, ``'XYLooper'``, ``'XYZLooper'``}
        Name of the looper. Available options are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            'XLooper'       1D looper (:class:`qom.loopers.axes.XLooper`) (fallback).
            'XYLooper'      2D looper (:class:`qom.loopers.axes.XYLooper`).
            'XYZLooper'     3D looper (:class:`qom.loopers.axes.XYZLooper`).
            ==============  ================================================
    func : callable
        Function to loop, formatted as ``func(system_params)``, where ``system_params`` is a dictionary of the updated parameters for the system for that iteration of the looper.
    params : dict
        Parameters of the looper. Refer to **Notes** of :class:`qom.loopers.base.BaseLooper` for all available options.
    params_system : dict
        Parameters of the system. If not provided, new keys are created for the looper variables.
    plot : bool, default=False
        Option to plot the results of the main process.
    subplots : bool, default=False
        Option to plot the results of each subprocesses.
    params_plotter : dict, optional
        Parameters of the plotter.
    num_processes : int, optional
        Number of loopers to run in parallel. The slicing of the values is performed on the first axis. If not provided, then the number slices are determined automatically, throttled by the number of available cores.
    cb_update : callable
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Returns
    -------
    looper : :class:`qom.loopers.axes.*`
        Instance of the looper.
    """

    # validate loopers
    assert looper_name in ['XLooper', 'XYLooper', 'XYZLooper'], "Parameter ``looper_name`` should be either ``'XLooper'``, ``'XYLooper'`` or ``'XYZLooper'``"

    # frequently used variables
    p_start = time.time()
    _s = "Time Elapsed\t"

    # initialize logger
    init_log(parallel=True)

    # initialize looper and axis to splice
    if 'XYZ' in looper_name:
        Looper = XYZLooper
        axis = 'Z'
    elif 'XY' in looper_name:
        Looper = XYLooper
        axis = 'Y'
    else:
        Looper = XLooper
        axis = 'X'
    looper = Looper(
        func=func,
        params=params,
        params_system=params_system,
        cb_update=cb_update,
        parallel=True
    )

    # load saved results and return looper
    if looper.load_results():
        # plot results
        if plot:
            plot_looper_results(
                looper=looper,
                params_plotter=params_plotter
            )

        return looper

    # extract axis values
    val = looper.axes[axis]['val']

    # handle null value or overflow
    if num_processes is None or num_processes > len(val) or num_processes < 1:
        num_processes = int(np.min([os.cpu_count() - 2, len(val)])) if len(val) > 1 else 1

    # maximum dimension of each slice
    slice_dim = int(np.ceil(len(val) / num_processes))
    
    # handle corner case
    while slice_dim * (num_processes - 1) >= len(val):
        num_processes -= 1
        
    # slice and populate arguments
    Args = list()
    for i in range(num_processes):
        # duplicate parameters
        _params = copy.deepcopy(params)
        # update axis parameters
        _params[axis] = {
            'var': looper.axes[axis]['var'],
            'idx': looper.axes[axis]['idx'],
            'val': val[i * slice_dim:((i + 1) * slice_dim) if (i + 1) * slice_dim <= len(val) else None],
            'dim': slice_dim if (i + 1) * slice_dim <= len(val) else len(val) - i * slice_dim,
        }

        # update log string
        _s += looper.name + " #" + str(i) + "\t"

        # update arguments
        Args.append([looper_name, func, _params, params_system, subplots, params_plotter, True, i, p_start])

    # update log
    logger.info("\n" + _s + "\n")
        
    # multiprocess and join
    with cf.ProcessPoolExecutor(max_workers=num_processes if num_processes < os.cpu_count() else os.cpu_count() - 2, mp_context=mp.get_context('spawn')) as executor:
        _loopers = list(executor.map(run_looper_instance, Args))
    
    # join list of values
    V = _loopers[0].results['V']
    for _l in _loopers[1:]:
        V += _l.results['V']

    # initialize variables
    _axes = [looper.axes.get('X', None), looper.axes.get('Y', None), looper.axes.get('Z', None)]
    _len = sum([1 if _axes[i] is not None else 0 for i in range(3)])

    # XYLooper
    if _len == 2:
        _dim = [
            len(V),
            len(V[0])
        ]
        X = [_axes[0]['val']] * _dim[0]
        Y = [[_axes[1]['val'][i]] * _dim[1] for i in range(_dim[0])]
        Z = None
    # XYZLooper
    elif _len == 3:
        _dim = [
            len(V),
            len(V[0]),
            len(V[0][0])
        ]
        X = [[_axes[0]['val']] * _dim[1]] * _dim[0]
        Y = [[_axes[1]['val'][i]] * _dim[2] for i in range(_dim[1])] * _dim[0]
        Z = [[[_axes[2]['val'][i]] * _dim[2]] * _dim[1] for i in range(_dim[0])]
    # XLooper
    else:
        X = _axes[0]['val']
        Y = None
        Z = None

    # update results
    looper.results = {
        'X': X,
        'Y': Y,
        'Z': Z,
        'V': V
    }

    # update log
    logger.info('\n')

    # save results
    looper.save_results()

    # plot results
    if plot:
        plot_looper_results(
            looper=looper,
            params_plotter=params_plotter
        )

    return looper

def run_looper_instance(args):
    """Function to run a single instance of ``wrap_looper``.
    
    Parameters
    ----------
    args : list
        Arguments of the ``wrap_looper`` function.

    Returns
    -------
    looper : :class:`qom.loopers.axes.*`
        Instance of the looper.
    """

    # return looper
    return wrap_looper(
        looper_name=args[0],
        func=args[1],
        params=args[2],
        params_system=args[3],
        plot=args[4],
        params_plotter=args[5],
        cb_update=None,
        parallel=args[6],
        p_index=args[7],
        p_start=args[8]
    )

def wrap_looper(looper_name:str, func, params:dict, params_system:dict, plot:bool=False, params_plotter:dict={}, cb_update=None, parallel=False, p_index:int=0, p_start:float=None):
    """Function to wrap loopers.
    
    Parameters
    ----------
    looper_name : {``'XLooper'``, ``'XYLooper'``, ``'XYZLooper'``}
        Name of the looper. Available options are:
            ==============  ================================================
            value           meaning
            ==============  ================================================
            'XLooper'       1D looper (:class:`qom.loopers.axes.XLooper`) (fallback).
            'XYLooper'      2D looper (:class:`qom.loopers.axes.XYLooper`).
            'XYZLooper'     3D looper (:class:`qom.loopers.axes.XYZLooper`).
            ==============  ================================================
    func : callable
        Function to loop, formatted as ``func(system_params)``, where ``system_params`` is a dictionary of the updated parameters for the system for that iteration of the looper.
    params : dict
        Parameters of the looper. Refer to **Notes** of :class:`qom.loopers.base.BaseLooper` for all available options.
    params_system : dict
        Parameters of the system. If not provided, new keys are created for the looper variables.
    plot : bool, default=False
        Option to plot the results of the main process.
    params_plotter : dict, optional
        Parameters of the plotter.
    cb_update : callable
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.

    Returns
    -------
    looper : :class:`qom.loopers.axes.*`
        Instance of the looper.
    """

    # validate loopers
    assert looper_name in ['XLooper', 'XYLooper', 'XYZLooper'], "Parameter ``looper_name`` should be either ``'XLooper'``, ``'XYLooper'`` or ``'XYZLooper'``"

    # initialize logger
    init_log(parallel=parallel)

    # select looper
    looper = {
        'XLooper': XLooper,
        'XYLooper': XYLooper,
        'XYZLooper': XYZLooper
    }.get(looper_name, XLooper)(
        func=func,
        params=copy.deepcopy(params),
        params_system=copy.deepcopy(params_system),
        cb_update=cb_update,
        parallel=parallel,
        p_index=p_index,
        p_start=p_start
    )
            
    # load or loop results
    if not looper.load_results():
        looper.loop()

        # if save opted
        looper.save_results()

    # plot results
    if plot:
        plot_looper_results(
            looper=looper,
            params_plotter=params_plotter
        )

    return looper

def plot_looper_results(looper, params_plotter:dict):
    """Helper function to plot results.
    
    Parameters
    ----------
    looper : :class:`qom.loopers.axes.*`
        Instance of the looper.
    params_plotter : dict
        Parameters of the plotter. Refer to **Notes** of :class:`qom.ui.plotters.base.BasePlotter` for all available parameters.
    """
    
    # initialize plot
    plotter = MPLPlotter(
        axes=looper.axes,
        params=params_plotter
    )
    
    # update plotter
    plotter.update(
        vs=looper.results['V'],
        xs=looper.results['X'],
        ys=looper.results.get('Y', None),
        zs=looper.results.get('Z', None)
    )
    plotter.show(
        hold=True
    )