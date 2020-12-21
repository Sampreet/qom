#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a 1D looper with multiple cases."""

__name__    = 'qom.loopers.XZLooper'
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

class XZLooper(BaseLooper):
    """Class to interface a 1D looper with multiple cases.
    
    Inherits :class:`qom.systems.BaseSystem`.

    Parameters
    ----------
    params : dict
        Parameters for the system.
    """

    def __init__(self, params: dict):
        """Class constructor for XZLooper."""

        # initialize super class
        super().__init__(params)

        # set axes
        self._set_axis('X')
        self._set_axis('Z')

    def loop(self, func, multithread=True):
        """Method to calculate the output of a given function for each X-axis point for multiple Z-axis cases.
        
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
        zs = self.axes['Z']['val']

        # initialize axes
        _xs = list()
        _ys = list()
        _zs = list()

        # display initialization
        logger.info('Initializing {name} calculation...\t\n'.format(name=self.params['solver']['name']))

        # iterate Z-axis values
        for k in range(len(zs)):
            # update progress
            self.update_progress(k, len(zs))

            # initialize axes
            _temp_xs = list()
            _temp_ys = list()
            results = list()

            # update system parameter
            system_params[self.axes['Z']['var']] = zs[k]

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
                _y = results[i][1]

                # handle multi-value result
                if type(_y) == list:
                    for j in range(len(_y)):
                        _temp_xs.append(_x)
                        _temp_ys.append(_y[j])
                else:
                    _temp_xs.append(_x)
                    _temp_ys.append(_y)

            # upate lists
            _xs.append(_temp_xs)
            _ys.append(_temp_ys)
            _zs.append(zs[k]*len(_temp_xs))

        # update attributes
        self.axes['X']['val'] = _xs
        self.axes['Z']['val'] = _zs
        self.values = _ys

        # display completion
        logger.info('----------------Values Obtained----------------\t\n')



        


