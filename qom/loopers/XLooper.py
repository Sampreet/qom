#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a 1D looper."""

__name__    = 'qom.loopers.XLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2021-01-01'

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
    func : function
        Function to loop.
    params : dict
        Parameters for the system, looper and figure.
    """

    def __init__(self, func, params: dict):
        """Class constructor for XLooper."""

        # initialize super class
        super().__init__(func, params)

        # set axes
        self._set_axis('X')

        # display initialization
        logger.info('---------------------Looper Initialized-----------------\t\n')

    def loop(self, mode: str='serial', grad: bool=False, plot: bool=False):
        """Method to calculate the output of a given function for each X-axis point.
        
        Parameters
        ----------
        mode : str, optional
            Mode of execution:
                'serial': Single-thread computation.
                'multithread': Multi-thread computation.
                'multiprocess': Multi-processor computation.
        grad : bool, optional
            Option to calculate gradients, superseded by looper parameter `grad`.
        plot: bool, option
            Option to plot the results.
        """

        # supersede looper parameters
        grad = self.params['looper'].get('grad', grad)
        plot = self.params['looper'].get('plot', plot)

        # get X-axis values
        _xs, _vs = self.get_X_results(mode, grad)

        # update attributes
        self.results = {}
        self.results['X'] = _xs
        self.results['V'] = _vs

        # display completion
        logger.info('---------------------Values Obtained--------------------\t\n')

        # plot results
        if plot:
            self.plot_results()
    
            # update log
            logger.info('---------------------Results Plotted--------------------\t\n')