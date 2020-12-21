#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a 1D looper."""

__name__    = 'qom.loopers.XLooper'
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

class XLooper(BaseLooper):
    """Class to interface a 1D looper.
    
    Inherits :class:`qom.systems.BaseSystem`.

    Parameters
    ----------
    params : dict
        Parameters for the system.
    """

    def __init__(self, params: dict):
        """Class constructor for XLooper."""

        # initialize super class
        super().__init__(params)

        # set axes
        self._set_axis('X')

    def loop(self, func, multithread=True):
        """Method to calculate the output of a given function for each X-axis point.
        
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

        # initialize axes
        _xs = list()
        _ys = list()
        results = list()

        # display initialization
        logger.info('Initializing {name} calculation...\t\n'.format(name=self.params['solver']['name']))

        # if multithreading is enabled
        if multithread:
            # obtain sorted results
            results = self.get_multithreaded_results(func, self.axes['X']['var'], self.axes['X']['val'])
        else:
            # iterate
            for i in range(dim):
                # calculate value
                _val = self.axes['X']['val'][i]
                system_params[self.axes['X']['var']] = _val[i]
                # calculate value
                func(system_params, _val, logger, results)

        # structure results
        for i in range(dim):
            _x = results[i][0]
            _y = results[i][1]

            # handle multi-value result
            if type(_y) == list:
                for j in range(len(_y)):
                    _xs.append(_x)
                    _ys.append(_y[j])
            else:
                _xs.append(_x)
                _ys.append(_y)

        # update attributes
        self.axes['X']['val'] = _xs
        self.values = _ys

        # display completion
        logger.info('----------------Values Obtained----------------\t\n')



        


