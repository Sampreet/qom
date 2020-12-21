#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface loopers."""

__name__    = 'qom.loopers.BaseLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2020-12-21'

# dependencies
import copy
import logging
import multiprocessing
import numpy as np
import threading

# module logger
logger = logging.getLogger(__name__)

class BaseLooper():
    """Class to interface loopers.

    Parameters
    ----------
    params : dict
        Parameters for the system, solver and figure.
    """

    @property
    def axes(self):
        """dict: Lists of axes points used to calculate."""

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        self.__axes = axes

    @property
    def params(self):
        """dict: Parameters for the system, solver and figure."""

        return self.__params

    @params.setter
    def params(self, params):
        self.__params = params

    @property
    def values(self):
        """list: Calculated values."""

        return self.__values
    
    @values.setter
    def values(self, values):
        self.__values = values

    def __init__(self, params: dict):
        """Class constructor for BaseLooper."""

        # validate params
        assert 'system' in params, 'Parameter `params` should contain key `system` for system parameters'
        assert 'solver' in params, 'Parameter `params` should contain key `solver` for solver parameters'

        self.params = params
        self.axes = dict()

    def _set_axis(self, axis):
        """Method to set the list of X-axis points.
        
        Parameters
        ----------
        axis : str
            Name of the axis.
        """

        # validate params
        assert axis in self.params['solver'], 'Key `solver` should contain key `' + axis + '` for axis parameters'
        self.axes[axis] = dict()

        # extract frequently used variables
        _axis = self.params['solver'][axis]

        # validate variable
        assert 'var' in _axis, 'Key `' + axis + '` should contain key `var` for the name of the variable'
        self.axes[axis]['var'] = _axis['var']

        # if axis values are provided
        _val = _axis.get('val', None)
        if _val is not None and type(_val) == list:
            # set values
            self.axes[axis]['val'] = _val

        # generate values
        else:
            # validate range
            assert 'min' in _axis and 'max' in _axis, 'Key `' + axis + '` should contain keys `min` and `max` to define axis range'

            # set values
            _val = np.linspace(_axis['min'], _axis['max'], _axis.get('dim', 101))
            self.axes[axis]['val'] = _val

    def get_multithreaded_results(self, func, var, val):
        """Method to obtain results of multithreaded execution of a given function.

        Parameters
        ----------
        func : function
            Function used to calculate.

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
            _thread = threading.Thread(target=func, args=(_system_params, val[i], logger, results, ))
            threads.append(_thread)
            # start thread
            _thread.start()
        
        # join all threads
        main_thread = threading.main_thread()
        for _thread in threading.enumerate():
            if _thread is not main_thread:
                _thread.join()

        # return sorted results
        return sorted(results)

    def get_multiprocessed_results(self, func, var, val):
        """Method to obtain results of multiprocessed execution of a given function.

        Parameters
        ----------
        func : function
            Function used to calculate.

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
            results.append(pool.apply(func, args=(_system_params, val[i], logger)))

        # return sorted results
        return sorted(results)

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