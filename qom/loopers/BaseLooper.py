#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface loopers."""

__name__    = 'qom.loopers.BaseLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2021-01-07'

# dependencies
from decimal import Decimal
from typing import Union
import copy
import logging
import multiprocessing
import numpy as np
import threading

# qom dependencies
from qom.ui.plotters import MPLPlotter

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_position = Union[str, int, float, np.float32, np.float64]

# TODO: Fix `get_multiprocessed_results`.
# TODO: Handle multi-valued points for gradients in `get_X_results`.
# TODO: Handle monotonic modes in `get_index`.
# TODO: Add `get_thresholds`.
# TODO: Handle exceptions in `plot_results`.

class BaseLooper():
    """Class to interface loopers.

    Initializes `axes`, `func` and `params` properties.

    Parameters
    ----------
    func : function
        Function to loop.
    params : dict
        Parameters for the system, looper and figure.
    """

    @property
    def axes(self):
        """dict: Lists of axes points used to calculate."""

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        self.__axes = axes

    @property
    def func(self):
        """function: Function to loop."""

        return self.__func
    
    @func.setter
    def func(self, func):
        self.__func = func

    @property
    def params(self):
        """dict: Parameters for the system, looper and figure."""

        return self.__params

    @params.setter
    def params(self, params):
        self.__params = params

    @property
    def results(self):
        """list: Calculated results."""

        return self.__results
    
    @results.setter
    def results(self, results):
        self.__results = results

    def __init__(self, func, params: dict):
        """Class constructor for BaseLooper."""

        # validate parameters
        assert 'system' in params, 'Parameter `params` should contain key `system` for system parameters'
        assert 'looper' in params, 'Parameter `params` should contain key `looper` for looper parameters'

        # set attributes
        self.func = func
        self.params = params
        self.axes = dict()

    def _set_axis(self, axis):
        """Method to set the list of X-axis points.
        
        Parameters
        ----------
        axis : str
            Name of the axis.
        """

        # validate parameters
        assert axis in self.params['looper'], 'Key `looper` should contain key `{}` for axis parameters'.format(axis)
        self.axes[axis] = dict()

        # extract frequently used variables
        _axis = self.params['looper'][axis]

        # validate variable
        assert 'var' in _axis, 'Key `{}` should contain key `var` for the name of the variable'.format(axis)
        self.axes[axis]['var'] = _axis['var']

        # if axis values are provided
        _val = _axis.get('val', None)
        if _val is not None and type(_val) is list:
            # set values
            self.axes[axis]['val'] = _val

        # generate values
        else:
            # validate range
            assert 'min' in _axis and 'max' in _axis, 'Key `{}` should contain keys `min` and `max` to define axis range'.format(axis)

            # set values
            _val = np.linspace(_axis['min'], _axis['max'], _axis.get('dim', 101))
            # truncate values
            _step_size = (_axis['max'] - _axis['min']) / (len(_val) - 1)
            _decimals = - Decimal(str(_step_size)).as_tuple().exponent
            _val = np.around(_val, _decimals)
            # convert to list
            _val = _val.tolist()
            # update axis
            self.axes[axis]['val'] = _val
    
    def get_X_results(self, mode: str='serial', grad: bool=False):
        """Method to obtain results for variation in X-axis.
        
        Parameters
        ----------
        mode : str, optional
            Mode of execution, superseded by `mode` of looper parameters. Available modes are:
                'serial': Single-thread computation.
                'multithread': Multi-thread computation.
                'multiprocess': Multi-processor computation.
        grad : bool, optional
            Option to calculate gradients.

        Returns
        -------
        xs : list
            Values of the X-axis.
        vs : list
            Calculated values.
        """

        # extract frequently used variables
        system_params = self.params['system']
        looper_mode = self.params['looper'].get('mode', mode)
        show_progress = self.params['looper'].get('show_progress', False)
        x_var = self.axes['X']['var']
        x_val = self.axes['X']['val']
        x_dim = len(x_val)

        # initialize axes
        xs = list()
        vs = list()
        results = list()

        # if multithreading is opted
        if looper_mode == 'multithread':
            # obtain sorted results
            results = self.get_multithreaded_results(x_var, x_val)
        else:
            # iterate
            for i in range(x_dim):
                # update progress
                progress = float(i)/float(x_dim - 1) * 100
                # display progress
                if show_progress and int(progress * 1000) % 10 == 0:
                    logger.info('Calculating the values: Progress = {progress:3.2f}'.format(progress=progress))
                # calculate value
                _val = x_val[i]
                system_params[x_var] = _val
                # calculate value
                self.func(system_params, _val, logger, results)

        # structure results
        for i in range(x_dim):
            _x = results[i][0]
            _y = results[i][1]

            # handle multi-value result
            if type(_y) is list:
                for j in range(len(_y)):
                    xs.append(_x)
                    vs.append(_y[j])
            else:
                xs.append(_x)
                vs.append(_y)

        # gradient opted
        if grad:
            vs = np.gradient(vs, xs)

        return xs, vs

    def get_multithreaded_results(self, var, val):
        """Method to obtain results of multithreaded execution of a given function.

        Parameters
        ----------
        var : str
            Name of the variable.
        val : list
            Values of the variable.
        """

        # extract frequently used variables
        system_params = self.params['system']
        dim = len(val)

        # initialize axes
        results = list()
        threads = list()

        # start all threads
        for i in range(dim):            
            # udpate a deep copy
            _system_params = copy.deepcopy(system_params)
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

    def get_multiprocessed_results(self, var, val):
        """Method to obtain results of multiprocessed execution of a given function. (*Under construction.*)

        Parameters
        ----------
        var : str
            Name of the variable.
        val : list
            Values of the variable.
        """

        # extract frequently used variables
        system_params = self.params['system']
        dim = len(val)

        # initialize axes
        results = list()
        pool = multiprocessing.Pool(processes=4)

        # start all threads
        for i in range(dim):            
            # udpate a deep copy
            _system_params = copy.deepcopy(system_params)
            _system_params[var] = val[i]
            # obtain results using multiprocessing pool
            results.append(pool.apply(self.func, args=(_system_params, val[i], logger, results)))

        # sort results by first entry
        results = sorted(results)

        return results

    def get_index(self, axis_values: list, calc_values: list=None, position: t_position='mean', mono_idx: int=0):
        """Function to calculate the index of a particular position in a list.
        
        Parameters
        ----------
        axis_values : list
            Values of the axis.
        calc_values : list, optional
            Values of the calculation.
        position: str or float, optional
            A value denoting the position or a mode to calculate the position. For a mode other than 'mean', the `mono_idx` parameter should be filled. The different modes can be:
                'mean': Mean of the axis values.
                'mono_mean': Mean of the monotonic patches in calculated values.
                'mono_min': Local minima of the monotonic patches.
                'mono_max': Local maxima of the monotonic patches.
        mono_idx: int, optional
            Index of the monotonic patch.

        Returns
        -------
        idx : list
            Indices of the required positions.
        """
        
        # fixed position
        if not type(position) is str:
            idx = abs(np.asarray(axis_values) - position).argmin()
        # mean mode
        elif position == 'mean':
            idx = abs(np.asarray(axis_values) - np.mean(axis_values)).argmin()
        # monotonic modes
        else:
            idx = 0

        return idx

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

    def plot_results(self):
        """Method to plot the results."""

        # validate parameters
        assert 'plotter' in self.params, 'Parameter `params` should contain key `plotter` for plotter parameters'
        assert 'type' in self.params['plotter'], 'Parameter `plotter` should contain key `type`.'

        # initialize plot
        plotter = MPLPlotter(self.axes, self.params['plotter'])

        # get plot axes
        _xs = self.results['X']
        _ys = self.results.get('Y', None)
        _zs = self.results.get('Z', None)
        _vs = self.results['V']
        
        # update plotter
        plotter.update(_xs, _ys, _zs, _vs)
        plotter.show(True)

