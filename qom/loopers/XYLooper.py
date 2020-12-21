#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a 2D looper."""

__name__    = 'qom.loopers.XYLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2020-12-21'

# dependencies
import logging
import numpy as np

# qom modules
from qom.loopers.BaseLooper import BaseLooper

# module logger
logger = logging.getLogger(__name__)

class XYLooper(BaseLooper):
    """Class to interface a 2D looper.
    
    Inherits :class:`qom.systems.BaseSystem`.

    Parameters
    ----------
    params : dict
        Parameters for the system.
    """

    def __init__(self, params: dict):
        """Class constructor for XYLooper."""

        # initialize super class
        super().__init__(params)

        # set axes
        self._set_axis('X')
        self._set_axis('Y')

    def loop(self, func, multithread=True):
        """Method to calculate the output of a given function for each X-axis and Y-axis point.
        
        Parameters
        ----------
        func : function
            Function used to calculate.

        multithread : bool, optional
            Option to use multithreading.
        """

        # extract frequently used variables
        system_params = self.params['system']
        dim = len(self.axes['X']['val'])
        ys = self.axes['Y']['val']

        # initialize axes
        _xs = list()
        _ys = list()
        _zs = list()

        # display initialization
        logger.info('Initializing {name} calculation...\t\n'.format(name=self.params['solver']['name']))

        # iterate Y-axis values
        for k in range(len(ys)):
            # update progress
            self.update_progress(k, len(ys))

            # initialize axes
            _temp_xs = list()
            _temp_zs = list()
            results = list()

            # update system parameter
            system_params[self.axes['Y']['var']] = ys[k]

            # if multithreading is enabled
            if multithread:
                # obtain sorted results
                results = self.get_multithreaded_results(func, self.axes['X']['var'], self.axes['X']['val'])
            else:
                # iterate
                for i in range(dim):
                    # update system parameter
                    _val = self.axes['X']['val'][i]
                    system_params[self.axes['X']['var']] = _val
                    # calculate value
                    func(system_params, _val, logger, results)


            # structure results
            for i in range(dim):
                _x = results[i][0]
                _z = results[i][1]

                # handle multi-value result
                if type(_z) == list:
                    for j in range(len(_z)):
                        _temp_xs.append(_x)
                        _temp_zs.append(_z[j])
                else:
                    _temp_xs.append(_x)
                    _temp_zs.append(_z)

            # upate lists
            _xs.append(_temp_xs)
            _ys.append([ys[k]]*len(_temp_xs))
            _zs.append(_temp_zs)

        # update attributes
        self.axes['X']['val'] = _xs
        self.axes['Y']['val'] = _ys
        self.values = _zs

        # display completion
        logger.info('----------------Values Obtained----------------\t\n')



        


