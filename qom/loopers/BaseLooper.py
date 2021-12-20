#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface loopers."""

__name__    = 'qom.loopers.BaseLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2021-10-20'

# dependencies
from decimal import Decimal
from typing import Union
import copy
import logging
import multiprocessing
import numpy as np
import os
import threading

# qom dependencies
from ..ui.plotters import MPLPlotter

# module logger
logger = logging.getLogger(__name__)

# TODO: Fix `get_multiprocessed_results`.
# TODO: Handle multi-valued points for gradients in `get_X_results`.
# TODO: Handle monotonic modes in `get_index`.
# TODO: Support gradients in `wrap`.

class BaseLooper():
    """Class to interface loopers.

    Initializes ``axes``, ``func`` and ``params`` properties.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params, val, logger, results)``, where ``system_params`` is a dictionary of the parameters for the system, ``val`` is the current value of the looping parameter, ``logger`` is an instance of the module logger and ``results`` is a list of tuples each containing ``val`` and the value calculated within the function.
    params : dict
        Parameters for the looper and optionally, the system and the plotter. The "looper" key is a dictionary containing one or more keys for the axes ("X", "Y" or "Z"), each with the keys "var" and "val" for the name of the parameter to loop and its corresponding values, along with additional options (refer notes).
    code : str
        Codename for the interfaced looper.
    name : str
        Full name of the interfaced looper.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    Notes
    -----
    The "looper" dictionary in ``params`` currently supports the following keys:
        ==================  ====================================================
        key                 value
        ==================  ====================================================
        "grad"              (*bool*) option to calculate gradients with respect to the X-axis.
        "grad_position"     (*str*) a value denoting the position or a mode to calculate the position. For a position other than "all" and "mean", the ``grad_mono_idx`` parameter should be filled. The different positions can be "mean" for the mean of the axis values, "mono_mean" for the mean of the monotonic patches in calculated values, "mono_min" for the local minima of the monotonic patches, "mono_max" for the local maxima of the monotonic patches and "all" to output all positions (default).
        "grad_mono_idx"     (*int*) index of the monotonic patch.
        "mode"              (*str*) mode of computation. Options are "multiprocess" for multi-processor execution, "multithread" for multi-threaded execution and "serial" for single-threaded execution (fallback).
        "show_progress"     (*bool*) option to display the progress for the calculation of results in the first dimension.
        ==================  ====================================================

    Each axis dictionary ("X", "Y" or "Z") inside the "looper" dictionary can contain the following keys in the descending order of their priorities:
        ==========  ====================================================
        key         value
        ==========  ====================================================
        "var"       (*str*) name of the parameter to loop. Its value defaults to "x" if the axis is a list of values and not a dictionary.
        "idx"       (*int*) index of the parameter if the parameter is a list of values.
        "val"       (*list*) values of the parameter. The remaining keys are not checked if its value is given. Otherwise, the "min", "max", "dim" and "scale" values are used to obtain "val".
        "min"       (*float*) minimum value of the parameter.
        "max"       (*float*) maximum value of the parameter.
        "dim"       (*int*) number of values from "min" to "max", both inclusive.
        "scale"     (*str*) step scale of the values. Available scales are "log" and "linear" (fallback). If this value is "log", the "min" and "max" values should be the exponents of 10.
        ==========  ====================================================

    .. note:: All the options defined under "looper" supersede individual function arguments.
    """

    @property
    def axes(self):
        """dict: Lists of axes points used to calculate."""

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        self.__axes = axes

    @property
    def results(self):
        """dict: Lists of axes (keys "X", "Y" and "Z") and values (key "V") ."""

        return self.__results
    
    @results.setter
    def results(self, results):
        self.__results = results

    def __init__(self, func, params: dict, code: str, name: str, cb_update=None):
        """Class constructor for BaseLooper."""

        # validate parameters
        assert 'looper' in params, 'Parameter ``params`` should contain key "looper" for looper parameters'
        if 'system' not in params:
            params['system'] = {}

        # set attributes
        self.func = func
        self.params = params
        self.code = code
        self.name = name
        self.cb_update = cb_update

        # set properties
        self.axes = dict()
        self.results = None

    def _set_axis(self, axis: str):
        """Method to set the list of axis values.
        
        Parameters
        ----------
        axis : str
            Name of the axis ("X", "Y" or "Z").
        """

        # validate parameters
        assert axis in self.params['looper'], 'Key "looper" should contain key "{}" for axis parameters'.format(axis)

        # extract frequently used variables
        _axis = self.params['looper'][axis]

        # if axis is a list of values
        if type(_axis) is list:
            _axis = {
                'var': 'x',
                'val': _axis
            }

        # initialize dict
        self.axes[axis] = dict()

        # validate variable
        assert 'var' in _axis, 'Key "{}" should contain key "var" for the name of the variable'.format(axis)
        self.axes[axis]['var'] = _axis['var']

        # check index of variable
        self.axes[axis]['idx'] = _axis.get('idx', None)

        # if axis values are provided
        _val = _axis.get('val', None)
        if _val is not None and type(_val) is list:
            # set values
            self.axes[axis]['val'] = _val
        # generate values
        else:
            # validate range
            assert 'min' in _axis and 'max' in _axis, 'Key "{}" should contain keys "min" and "max" to define axis range'.format(axis)

            # extract dimension
            _min = np.float_(_axis['min'])
            _max = np.float_(_axis['max'])
            _dim = int(_axis.get('dim', 101))
            _scale = _axis.get('scale', 'linear')

            # set values
            if _scale == 'log':
                _val = np.logspace(_min, _max, _dim)
            elif _scale == 'linear':
                _val = np.linspace(_min, _max, _dim)
                # truncate values
                _step_size = (Decimal(str(_max)) - Decimal(str(_min))) / (_dim - 1)
                _decimals = - _step_size.as_tuple().exponent
                _val = np.around(_val, _decimals)
            # convert to list
            _val = _val.tolist()
            # update axis
            self.axes[axis]['val'] = _val

    def get_full_file_path(self, file_path: str):
        """Method to obtain the complete file path.
        
        Parameters
        ----------
        file_path : str
            Original file path.
            
        Returns
        -------
        file_path : str
            Full file path.
        """

        # complete filename with system parameters
        for key in self.params['system']:
            file_path += '_' + str(self.params['system'][key])
        # update for XLooper variable
        for key in self.params['looper']['X']:
            file_path += '_' + str(self.params['looper']['X'][key])
        # update for XYLooper variable
        if 'xy' in self.code:
            Y = self.axes['Y']
            for key in self.params['looper']['Y']:
                file_path += '_' + str(self.params['looper']['Y'][key])
        # update for XYZLooper variable
        if 'xyz' in self.code:
            Z = self.axes['Z']
            for key in self.params['looper']['Z']:
                file_path += '_' + str(self.params['looper']['Z'][key])

        return file_path

    def get_grad_index(self, axis_values: list, calc_values: list=None, grad_position='mean', grad_mono_idx: int=0):
        """Function to calculate the index of a particular position in a list to calculate the gradients.
        
        Parameters
        ----------
        axis_values : list
            Values of the axis.
        calc_values : list, optional
            Values of the calculation.
        grad_position: str or float, optional
            A value denoting the position or a mode to calculate the position. For a position other than "all" and "mean", the ``grad_mono_idx`` parameter should be filled. The different positions can be:
                ==============  ====================================================
                value           meaning
                ==============  ====================================================
                "mean"          mean of the axis values.
                "mono_mean"     mean of the monotonic patches in calculated values.
                "mono_min"      local minima of the monotonic patches.
                "mono_max"      local maxima of the monotonic patches.
                ==============  ====================================================
        grad_mono_idx: int, optional
            Index of the monotonic patch.

        Returns
        -------
        idx : list
            Indices of the required positions.
        """

        # supersede looper parameters
        grad_position = self.params['looper'].get('grad_position', grad_position)
        grad_mono_idx = self.params['looper'].get('grad_mono_idx', grad_mono_idx)

        # validate parameters
        supported_types = Union[str, int, float, np.float32, np.float64].__args__
        assert isinstance(grad_position, supported_types), 'Parameter ``grad_position`` should be either of the types: {}'.format(supported_types)

        # handle inherited exceptions
        if grad_position == 'all':
            grad_position = 'mean'
        
        # fixed position
        if not type(grad_position) is str:
            idx = abs(np.asarray(axis_values) - grad_position).argmin()
        # mean mode
        elif grad_position == 'mean':
            idx = abs(np.asarray(axis_values) - np.mean(axis_values)).argmin()
        # monotonic modes
        else:
            idx = 0

        return idx

    def get_multiprocessed_results(self, var, idx, val):
        """Method to obtain results of multiprocessed execution of a given function. (*Under construction.*)

        Parameters
        ----------
        var : str
            Name of the variable.
        idx : int
            Index of the variable.
        val : list
            Values of the variable.
        """

        # initialize axes
        results = list()
        pool = multiprocessing.Pool(processes=4)

        # start all threads
        for i in range(len(val)):            
            # update a deep copy
            _system_params = copy.deepcopy(self.params['system'])
            if idx is not None:
                _system_params[var][idx] = val[i]
            else:
                _system_params[var] = val[i]
            # obtain results using multiprocessing pool
            results.append(pool.apply(self.func, args=(_system_params, val[i], logger, results)))

        # sort results by first entry
        results = sorted(results)

        return results

    def get_multithreaded_results(self, var, idx, val):
        """Method to obtain results of multithreaded execution of a given function.

        Parameters
        ----------
        var : str
            Name of the variable.
        idx : int
            Index of the variable.
        val : list
            Values of the variable.
        """

        # initialize axes
        results = list()
        threads = list()

        # start all threads
        for i in range(len(val)):
            # update a deep copy
            _system_params = copy.deepcopy(self.params['system'])
            if idx is not None:
                _system_params[var][idx] = val[i]
            else:
                _system_params[var] = val[i]
            # create thread and pass parameters to function
            _thread = threading.Thread(target=self.func, args=(_system_params, val[i], logger, results, ))
            threads.append(_thread)
            # start thread
            _thread.start()
        
        # join all threads
        main_thread = threading.main_thread()
        for _thread in threading.enumerate():
            if _thread is not main_thread:
                _thread.join()

        # sort results by first entry
        results = sorted(results)

        return results

    def get_thresholds(self, thres_mode='minmax'):
        """Method to calculate the threshold values for the results.

        Parameters
        ----------
        thres_mode : str
            Mode of calculation of threshold values. Options are:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "minmax"    minimum value at which maximum is reached.
                "minmin"    minimum value at which minimum is reached.
                ==========  ====================================================
        
        Returns
        -------
        thres : dict
            Threshold values.
        """

        # mode selector
        _selector = {
            'minmax': np.argmax,
            'minmin': np.argmin
        }

        # initialize
        thres = {}

        # XLooper
        if self.code == 'x_looper':
            _index = _selector[thres_mode](self.results['V'])
            thres['X'] = self.axes['X']['val'][_index]
            thres['V'] = self.results['V'][_index]
        # XYLooper
        if self.code == 'xy_looper':
            _x_dim = len(self.axes['X']['val'])
            _index = _selector[thres_mode](self.results['V'])
            thres['X'] = self.axes['X']['val'][_index % _x_dim]
            thres['Y'] = self.axes['Y']['val'][int(_index / _x_dim)]
            thres['V'] = self.results['V'][int(_index / _x_dim)][_index % _x_dim]

        return thres
    
    def get_X_results(self, grad: bool=False, mode: str='serial'):
        """Method to obtain results for variation in X-axis.
        
        Parameters
        ----------
        grad : bool, optional
            Option to calculate gradients.
        mode : str, optional
            Mode of computation. Available modes are:
                ==================  ====================================================
                value               meaning
                ==================  ====================================================
                "multiprocess"      multi-processor execution.
                "multithread"       multi-thread execution.
                "serial"            single-thread execution (fallback).
                ==================  ====================================================

        Returns
        -------
        xs : list
            Values of the X-axis.
        vs : list
            Calculated values.
        """

        # supersede looper parameters
        grad = self.params['looper'].get('grad', grad)
        mode = self.params['looper'].get('mode', mode)
        show_progress = self.params['looper'].get('show_progress', False)

        # extract frequently used variables
        x_var = self.axes['X']['var']
        x_idx = self.axes['X']['idx']
        x_val = self.axes['X']['val']
        x_dim = len(x_val)

        # initialize axes
        xs = list()
        vs = list()
        results = list()

        # if multithreading is opted
        if mode == 'multiprocess':
            # obtain sorted results
            results = self.get_multiprocessed_results(x_var, x_idx, x_val)
        # if multithreading is opted
        elif mode == 'multithread':
            # obtain sorted results
            results = self.get_multithreaded_results(x_var, x_idx, x_val)
        else:
            # iterate
            for i in range(x_dim):
                # update progress
                if show_progress :
                    self.update_progress(pos=i, dim=x_dim)
                # update a deep copy
                system_params = copy.deepcopy(self.params['system'])
                if x_idx is not None:
                    system_params[x_var][x_idx] = x_val[i]
                else:
                    system_params[x_var] = x_val[i]
                # calculate value
                self.func(system_params, x_val[i], logger, results)

        # structure results
        for i in range(x_dim):
            _x = results[i][0]
            _v = results[i][1]

            # update lists
            xs.append(_x)
            vs.append(_v)

        # if opted for gradient calculation
        if grad:
            vs = np.gradient(vs, xs)

        return xs, vs

    def plot_results(self, hold: bool=True, width: float=5.0, height: float=5.0):
        """Method to plot the results.
        
        Parameters
        ----------
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
        if 'plotter' not in self.params:
            self.params['plotter'] = {}
        # supersede plotter parameters
        self.params['plotter']['type'] = self.params['plotter'].get('type', {
            'x_looper': 'line',
            'xy_looper': 'pcolormesh',
            'xyz_looper': 'surface'
        }[self.code])
        self.params['plotter']['width'] = self.params['plotter'].get('width', width)
        self.params['plotter']['height'] = self.params['plotter'].get('height', height)

        # initialize plot
        plotter = MPLPlotter(self.axes, self.params['plotter'])

        # get plot axes
        _xs = self.results['X']
        _ys = self.results.get('Y', None)
        _zs = self.results.get('Z', None)
        _vs = self.results['V']
        
        # update plotter
        plotter.update(xs=_xs, ys=_ys, zs=_zs, vs=_vs)
        plotter.show(hold)

        return plotter

    def save_results(self, file_path):
        """Method to obtain the complete file path.
        
        Parameters
        ----------
        file_path : str
            Original file path.
        """

        # create directories
        file_dir = file_path[:len(file_path) - len(file_path.split('/')[-1])]
        try:
            os.makedirs(file_dir)
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=file_dir))

        # save data
        np.savez_compressed(file_path, np.array(self.results['V']))
        
        # display completion
        logger.info('------------------Results Saved----------------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Results Saved', progress=None, reset=True)

    def update_progress(self, pos, dim):
        """Method to update the progress of the calculation.
        
        Parameters
        ----------
        pos : int
            Index of current iteration.
        dim : int 
            Total number of iterations.
        """
        
        # calculate progress
        progress = float(pos) / float(dim - 1) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the values: Progress = {progress:3.2f}'.format(progress=progress))
            if self.cb_update is not None:
                self.cb_update(status='Calculating the values...', progress=progress)

    def wrap(self, file_path: str=None, plot: bool=False, hold: bool=True, width: float=5.0, height: float=5.0):
        """Method to wrap the looper.

        Parameters
        ----------
        file_path : str, optional
            Path to the data file.
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

        # initialize variables
        X = self.axes['X']
        Y = None
        Z = None
        if file_path is not None:
            # get full file path
            file_path = self.get_full_file_path(file_path=file_path)

            # attempt to load results if exists
            if os.path.isfile(file_path + '.npz'):
                self.results = {
                    'X': X['val'],
                    'Y': Y['val'] if Y is not None else None,
                    'Z': Z['val'] if Z is not None else None,
                    'V': np.load(file_path + '.npz')['arr_0'].tolist()
                }
                
                # display completion
                logger.info('------------------Results Loaded---------------------\t\n')
                if self.cb_update is not None:
                    self.cb_update(status='Results Loaded', progress=None, reset=True)
                
            # loop and save results
            else:
                self.loop()

                # save data
                self.save_results(file_path=file_path)
        
        # loop
        else:
            self.loop()

        # plot results
        if plot:
            self.plot_results(hold=hold, width=width, height=height)

        return self