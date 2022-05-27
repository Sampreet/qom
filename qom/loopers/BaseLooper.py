#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface loopers."""

__name__    = 'qom.loopers.BaseLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2022-05-27'

# dependencies
from decimal import Decimal
from typing import Union
import copy
import logging
import multiprocessing
import numpy as np
import os
import threading
import time

# qom dependencies
from ..ui.plotters import MPLPlotter

# module logger
logger = logging.getLogger(__name__)

# TODO: Add monotonic modes in `_get_grad_index`.
# TODO: Fix `get_multiprocessed_results`.
# TODO: Handle multi-valued points for gradients in `get_X_results`.
# TODO: Support gradients in `wrap`.

class BaseLooper():
    """Class to interface loopers.

    Initializes ``axes``, ``cb_update``, ``code``, ``func``, ``name``, ``params``, ``results`` and ``time``.

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
        "file_path_prefix"  (*str*) prefix for the file path to save the looper results.
        "grad"              (*bool*) option to calculate gradients with respect to the X-axis.
        "grad_position"     (*str*) a value denoting the position or a mode to calculate the position. For a position other than "all" and "mean", the ``grad_mono_idx`` parameter should be filled. The different positions can be "mean" for the mean of the axis values, "mono_mean" for the mean of the monotonic patches in calculated values, "mono_min" for the local minima of the monotonic patches, "mono_max" for the local maxima of the monotonic patches and "all" to output all positions.
        "grad_mono_idx"     (*int*) index of the monotonic patch.
        "mode"              (*str*) mode of computation. Options are "multiprocess" for multi-processor execution, "multithread" for multi-threaded execution and "serial" for single-threaded execution.
        "show_progress_x"   (*bool*) option to display the progress for the calculation of results in X-axis.
        "show_progress_y"   (*bool*) option to display the progress for the calculation of results in Y-axis.
        "show_progress_yz"  (*bool*) option to display the progress for the calculation of results in YZ-axis.
        "thres_mode"        (*str*) Mode of calculation of threshold values. Options are "minmax" for minimum value at which maximum is reached and "minmin" for minimmum value at which minimum is reached.
        ==================  ====================================================

    Each axis dictionary ("X", "Y" or "Z") inside the "looper" dictionary can contain the following keys in the descending order of their priorities:
        ==========  ====================================================
        key         value
        ==========  ====================================================
        "var"       (*str*) name of the parameter to loop. Its value defaults to the axis name in lower case if the axis is a sequence of values and not a dictionary.
        "idx"       (*int*) index of the parameter if the parameter is a sequence of values.
        "val"       (*list* or *np.ndarray*) values of the parameter. The remaining keys are not checked if its value is given. Otherwise, the "min", "max", "dim" and "scale" values are used to obtain "val".
        "min"       (*float*) minimum value of the parameter.
        "max"       (*float*) maximum value of the parameter.
        "dim"       (*int*) number of values from "min" to "max", both inclusive. Default is 101.
        "scale"     (*str*) step scale of the values. Available scales are "log" for logarithmic and "linear" for linear. If this value is "log", the "min" and "max" values should be the exponents of 10. Default is "linear"
        ==========  ====================================================

    .. note:: All the options defined under "looper" supersede individual method arguments. If "looper" defines a list of axes values, then the individual axes are set automatically.
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
        self.cb_update = cb_update
        self.code = code
        self.func = func
        self.name = name
        self.params = params
        self.time = time.time()

        # set properties
        self.axes = dict()
        self.results = None

        # validate parameters
        assert 'looper' in self.params, 'Dictionary `params` should contain key "looper" for looper parameters'

        # reformat parameters
        if type(self.params['looper']) is list:
            # validate parameters
            supported_types = Union[int, float, np.float_, np.float16, np.float32, np.float64, np.float128].__args__
            assert isinstance(self.params['looper'][0], supported_types), 'Lists of axes values for "looper" should be one of the types: {}'.format(supported_types)
            
            # initialize
            _looper_params = dict()

            # get axis values
            _axes = ['X', 'Y', 'Z']
            for i in range(np.shape(self.params['looper'])[0]):
                _looper_params[_axes[i]] = self.params['looper'][i]

            # update looper parameters
            self.params['looper'] = _looper_params

    def _check_directories(self, file_path: str):
        """Method to check for data directory.
        
        Parameters
        ----------
        file_path : str
            Full file path.
        """

        # get directory
        file_dir = file_path[:len(file_path) - len(file_path.split('/')[-1])]
        # try to create
        try:
            os.makedirs(file_dir)
            # update log
            logger.debug('Directory {dir_name} created\n'.format(dir_name=file_dir))  
        # if already exists
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=file_dir))   

    def _get_full_file_path(self, file_path_prefix: str):
        """Method to obtain the full file path.
        
        Parameters
        ----------
        file_path_prefix : str
            Prefix of the file path.
            
        Returns
        -------
        file_path : str
            Full file path.
        """

        # supersede arguments by looper parameters
        file_path = file_path_prefix

        # # complete filename with system parameters
        # for key in self.params['system']:
        #     file_path += '_' + str(self.params['system'][key])

        # update for XLooper variable
        file_path += self._get_params_str('X')

        # update for XYLooper variable
        if 'XY' in self.code:
            file_path += self._get_params_str('Y')

        # update for XYZLooper variable
        if 'XYZ' in self.code:
            file_path += self._get_params_str('Z')

        return file_path

    def _get_grad_index(self, axis_values: list, grad_position, grad_mono_idx: int):
        """Function to calculate the index of a particular position in a list to calculate the gradients.
        
        Parameters
        ----------
        axis_values : list
            Values of the axis.
        grad_position: str or float
            A value denoting the position or a mode to calculate the position. For a position other than "all" and "mean", the ``grad_mono_idx`` parameter should be filled. The different positions can be:
                ==============  ====================================================
                value           meaning
                ==============  ====================================================
                "all"           all values.
                "mean"          mean of the axis values.
                ==============  ====================================================
        grad_mono_idx: int
            Index of the monotonic patch.

        Returns
        -------
        idx : list
            Indices of the required positions.
        """

        # validate parameters
        supported_types = Union[str, int, float, np.float_, np.float16, np.float32, np.float64, np.float128].__args__
        assert isinstance(grad_position, supported_types), 'Parameter ``grad_position`` should be one of the types: {}'.format(supported_types)

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
            logger.info('---------------------Under Construction-----------------\t\n')
            idx = 0

        return idx

    def _get_multiprocessed_results(self, var, idx, val):
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

    def _get_multithreaded_results(self, var, idx, val):
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

    def _get_params_str(self, axis: str):
        """Method to obtain a strings of parameters used in a looper.
        
        Parameters
        ----------
        axis : str
            Name of the axis ("X", "Y" or "Z").

        Returns
        -------
        params_str: str
            String containing the parameters used in the looper.
        """

        # initialize
        params_str = ''

        # concatenate
        _axis = self.params['looper'][axis] if axis in self.params['looper'] else self.params['looper'][axis.lower()]
        for key in _axis:
            params_str += ('_' + axis.lower() + '=' if key == 'var' else '_') + str(_axis[key])

        return params_str

    def _get_X_results(self, grad: bool, mode: str, show_progress_x: bool):
        """Method to obtain results for variation in X-axis.
        
        Parameters
        ----------
        grad : bool
            Option to calculate gradients with respect to the X-axis.
        mode : str
            Mode of computation. Options are:
                ==================  ====================================================
                value               meaning
                ==================  ====================================================
                "multiprocess"      multi-processor execution.
                "multithread"       multi-thread execution.
                "serial"            single-thread execution (fallback).
                ==================  ====================================================
        show_progress_x : bool
            Option to display the progress for the calculation of results in X-axis.

        Returns
        -------
        xs : list
            Values of the X-axis.
        vs : list
            Calculated values.
        """

        # extract frequently used variables
        x_var = self.axes['X']['var']
        x_idx = self.axes['X']['idx']
        x_val = self.axes['X']['val']
        x_dim = len(x_val)

        # initialize
        results = list()
        xs = list()
        vs = list()

        # if multithreading is opted
        if mode == 'multiprocess':
            # obtain sorted results
            results = self._get_multiprocessed_results(x_var, x_idx, x_val)
        # if multithreading is opted
        elif mode == 'multithread':
            # obtain sorted results
            results = self._get_multithreaded_results(x_var, x_idx, x_val)
        else:
            # iterate
            for i in range(x_dim):
                # update progress
                if show_progress_x:
                    self._update_progress(pos=i, dim=x_dim)
                # update a deep copy
                system_params = copy.deepcopy(self.params['system'])
                if x_idx is not None:
                    # handle non system parameter
                    if system_params.get(x_var, None) is None:
                        system_params[x_var] = [0 for _ in range(x_idx + 1)]
                    system_params[x_var][x_idx] = x_val[i]
                else:
                    system_params[x_var] = x_val[i]
                # calculate value
                self.func(system_params, x_val[i], logger, results)

        # structure results and update lists
        for i in range(x_dim):
            xs.append(results[i][0])
            vs.append(results[i][1])

        # calculate gradients
        if grad:
            vs = np.gradient(vs, xs)

        return xs, vs

    def _set_axis(self, axis: str):
        """Method to set the list of axis values. The values for the axis are numpy floats.
        
        Parameters
        ----------
        axis : str
            Name of the axis ("X", "Y" or "Z").
        """

        # validate parameters
        assert axis in self.params['looper'], 'Key "looper" should contain key "{}" for axis parameters'.format(axis)

        # initialize axis
        self.axes[axis] = dict()

        # extract frequently used variables
        _axis = self.params['looper'][axis]

        # convert to list if numpy array
        if type(_axis) is np.ndarray:
            _axis = _axis.tolist()

        # handle list of values
        if type(_axis) is list:
            _axis = {
                'var': axis,
                'val': _axis
            }

        # if axis values are provided
        _val = _axis.get('val', None)
        # convert to list if numpy array
        if type(_val) is np.ndarray:
            _val = _val.tolist()
        # update values
        if type(_val) is list:
            # validate values
            assert len(_val) != 0, 'Key "{}" should contain key "val" with a non-empty list'.format(axis)

            # set values
            self.axes[axis]['val'] = _val
        # update values
        else:
            # validate range
            assert 'min' in _axis and 'max' in _axis, 'Key "{}" should contain keys "min" and "max" to define axis range'.format(axis)

            # extract dimension
            _min = np.float_(_axis['min'])
            _max = np.float_(_axis['max'])
            _dim = int(_axis.get('dim', 101))
            _scale = str(_axis.get('scale', 'linear'))

            # set values
            if _scale == 'log':
                _val = np.logspace(_min, _max, _dim)
            else:
                _val = np.linspace(_min, _max, _dim)
                # truncate values
                _step_size = (Decimal(str(_max)) - Decimal(str(_min))) / (_dim - 1)
                _decimals = - _step_size.as_tuple().exponent
                _val = np.around(_val, _decimals)
            # update axis
            self.axes[axis]['val'] = _val.tolist()

        # validate variable
        assert 'var' in _axis, 'Key "{}" should contain key "var" for the name of the variable'.format(axis)
        self.axes[axis]['var'] = _axis['var']

        # check index of variable
        _idx = _axis.get('idx', None)
        self.axes[axis]['idx'] = int(_idx) if _idx is not None else None

    def _update_progress(self, pos: int, dim: int):
        """Method to update the progress of the calculation.
        
        Parameters
        ----------
        pos : int
            Index of current iteration.
        dim : int 
            Total number of iterations.
        """
        
        # calculate progress
        progress = pos / (dim - 1) * 100
        # current time
        _time = time.time()

        # display progress
        if _time - self.time > 0.5:
            logger.info('Calculating the values: Progress = {progress:3.2f}'.format(progress=progress))
            if self.cb_update is not None:
                self.cb_update(status='Calculating the values...', progress=progress)

            # update time
            self.time = _time
            
    def get_thresholds(self, thres_mode: str='minmax'):
        """Method to calculate the threshold values for the results.

        Parameters
        ----------
        thres_mode : str
            Mode of calculation of threshold values. Default is "minmax". Options are:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "minmax"    minimum value at which maximum is reached.
                "minmin"    minimum value at which minimum is reached.
                ==========  ====================================================
        
        Returns
        -------
        thres : dict
            Threshold values. Keys are "X", "Y", "Z" and "V".
        """

        # supersede arguments by looper parameters
        thres_mode = self.params['looper'].get('thres_mode', thres_mode)

        # mode selector
        _selector = {
            'minmax': np.argmax,
            'minmin': np.argmin
        }

        # initialize
        thres = dict()

        # get index
        _index = _selector[thres_mode](self.results['V'])

        # 3D looper
        if self.code == 'XYZLooper':
            _x_dim = len(self.axes['X']['val'])
            _xy_dim = len(self.axes['Y']['val']) * _x_dim
            thres['X'] = self.results['X'][int(_index / _xy_dim)][int((_index % (_xy_dim)) / _x_dim)][_index % _x_dim]
            thres['Y'] = self.results['Y'][int(_index / _xy_dim)][int((_index % (_xy_dim)) / _x_dim)][_index % _x_dim]
            thres['Z'] = self.results['Z'][int(_index / _xy_dim)][int((_index % (_xy_dim)) / _x_dim)][_index % _x_dim]
            thres['V'] = self.results['V'][int(_index / _xy_dim)][int((_index % (_xy_dim)) / _x_dim)][_index % _x_dim]
        # 2D looper
        elif self.code == 'XYLooper':
            _x_dim = len(self.axes['X']['val'])
            thres['X'] = self.results['X'][int(_index / _x_dim)][_index % _x_dim]
            thres['Y'] = self.results['Y'][int(_index / _x_dim)][_index % _x_dim]
            thres['V'] = self.results['V'][int(_index / _x_dim)][_index % _x_dim]
        # 1D looper
        else:
            thres['X'] = self.results['X'][_index]
            thres['V'] = self.results['V'][_index]

        return thres
    
    def load_results(self, file_path_prefix: str='data/V'):
        """Method to load the results from a .npz file.
        
        Parameters
        ----------
        file_path_prefix : str, optional
            Prefix of the file path. Default is "data/V".

        Returns
        -------
        loaded : bool
            Boolean denoting whether results were successfully loaded.
        """

        # initialize
        loaded = False

        # supersede arguments by looper parameters
        file_path_prefix = self.params['looper'].get('file_path_prefix', file_path_prefix)

        # get full file path
        file_path = self._get_full_file_path(file_path_prefix=file_path_prefix)

        # check directories
        self._check_directories(file_path=file_path)

        # attempt to load results if exists
        if os.path.isfile(file_path + '.npz'):
            # load results
            V = np.load(file_path + '.npz')['arr_0'].tolist()

            # initialize variables
            _axes = [self.axes.get('X', None), self.axes.get('Y', None), self.axes.get('Z', None)]
            _len = sum([1 if _axes[i] is not None else 0 for i in range(3)])
            _dim = np.shape(V)

            # XYLooper
            if _len == 2:
                X = [_axes[0]['val']] * _dim[0]
                Y = [[_axes[1]['val'][i]] * _dim[1] for i in range(_dim[0])]
                Z = None
            # XYZLooper
            if _len == 3:
                X = [[_axes[0]['val']] * _dim[1]] * _dim[0]
                Y = [[_axes[1]['val'][i]] * _dim[2] for i in range(_dim[1])] * _dim[0]
                Z = [[[_axes[2]['val'][i]] * _dim[2]] * _dim[1] for i in range(_dim[0])]
            # XLooper
            else:
                X = _axes[0]['val']
                Y = None
                Z = None

            # update results
            self.results = {
                'X': X,
                'Y': Y,
                'Z': Z,
                'V': V
            }
            
            # display completion
            logger.info('------------------Results Loaded---------------------\t\n')
            if self.cb_update is not None:
                self.cb_update(status='Results Loaded', progress=None, reset=True)

            loaded = True

        return loaded
            
    def plot_results(self, hold: bool=True, width: float=5.0, height: float=5.0):
        """Method to plot the results.
        
        Parameters
        ----------
        hold : bool, optional
            Option to hold the plot. Default is `True`.
        width : float, optional
            Width of the figure. Default is `5.0`.
        height : float, optional 
            Height of the figure. Default is `5.0`.

        Returns
        -------
        plotter : :class:`qom.ui.plotters.MPLPlotter`
            Instance of ``MPLPLotter``.
        """

        # handle undefined plotter parameters
        if 'plotter' not in self.params:
            self.params['plotter'] = {}

        # supersede arguments by plotter parameters
        self.params['plotter']['type'] = self.params['plotter'].get('type', {
            'XLooper': 'line',
            'XYLooper': 'pcolormesh',
            'XYZLooper': 'surface'
        }[self.code])
        self.params['plotter']['hold'] = self.params['plotter'].get('hold', hold)
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

    def save_results(self, file_path_prefix: str='data/V'):
        """Method to save the results to a .npz file.
        
        Parameters
        ----------
        file_path_prefix : str
            Prefix of the file path. Default is "data/V".
        """

        # supersede arguments by looper parameters
        file_path_prefix = self.params['looper'].get('file_path_prefix', file_path_prefix)

        # get full file path
        file_path = self._get_full_file_path(file_path_prefix=file_path_prefix)

        # check directories
        self._check_directories(file_path=file_path)

        # save data
        np.savez_compressed(file_path, np.array(self.results['V']))
        
        # display completion
        logger.info('------------------Results Saved----------------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Results Saved', progress=None, reset=True)

    def wrap(self, file_path_prefix: str=None, plot: bool=False, hold: bool=True, width: float=5.0, height: float=5.0):
        """Method to wrap the looper.

        Parameters
        ----------
        file_path_prefix : str, optional
            Path of the file path. Default is `None` (doesn't save to file).
        plot: bool, optional
            Option to plot the results. Default is `False`.
        hold : bool, optional
            Option to hold the plot. Default is `True`.
        width : float, optional
            Width of the figure. Default is `5.0`.
        height : float, optional
            Height of the figure. Default is `5.0`.

        Returns
        -------
        looper : :class:`qom.loopers.*`
            Instance of the looper.
        """

        # if save/load opted
        if file_path_prefix is not None:
            # load saved results
            loaded = self.load_results(file_path_prefix=file_path_prefix)
                
            # loop and save results
            if not loaded:
                self.loop()

                # save data
                self.save_results(file_path_prefix=file_path_prefix)
        
        # loop
        else:
            self.loop()

        # plot results
        if plot:
            self.plot_results(hold=hold, width=width, height=height)

        return self