#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a 1D looper."""

__name__    = 'qom.loopers.XLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2022-03-19'

# dependencies
import logging

# qom modules
from .BaseLooper import BaseLooper

# module logger
logger = logging.getLogger(__name__)

class XLooper(BaseLooper):
    """Class to interface a 1D looper.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params, val, logger, results)``, where ``system_params`` is a dictionary of the parameters for the system, ``val`` is the current value of the looping parameter, ``logger`` is an instance of the module logger and ``results`` is a list of tuples each containing ``val`` and the value calculated within the function.
    params : dict
        Parameters for the looper and optionally, the system and the plotter. The "looper" key is a dictionary containing the key "X", with the keys "var" and "val" for the name of the parameter to loop and its corresponding values, along with additional options (refer notes).
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.
    
    .. note:: All the options defined under the "looper" dictionary in ``params`` supersede individual method arguments. Refer :class:`qom.loopers.BaseLooper` for a complete list of supported options.
    """

    # attributes
    code = 'XLooper'
    name = '1D Looper'
    
    def __init__(self, func, params: dict, cb_update=None):
        """Class constructor for XLooper."""

        # initialize super class
        super().__init__(func=func, params=params, code=self.code, name=self.name, cb_update=cb_update)

        # set axes
        self._set_axis(axis='X')

        # display initialization
        logger.info('---------------------Looper Initialized-----------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Looper Initialized', progress=None)

    def loop(self, grad: bool=False, mode: str='serial', show_progress_x: bool=True):
        """Method to calculate the output of a given function for each X-axis point.
        
        Parameters
        ----------
        grad : bool, optional
            Option to calculate gradients with respect to the X-axis.
        mode : str, optional
            Mode of computation. Options are:
                ==================  ====================================================
                value               meaning
                ==================  ====================================================
                "multiprocess"      multi-processor execution.
                "multithread"       multi-thread execution.
                "serial"            single-thread execution (fallback).
                ==================  ====================================================
        show_progress_x : bool, optional
            Option to display the progress for the calculation of results in X-axis. Default is `True`.

        Returns
        -------
        results : dict
            Axes and calculated values containing the keys "X" and "V".
        """

        # supersede arguments by looper parameters
        grad = self.params['looper'].get('grad', grad)
        mode = self.params['looper'].get('mode', mode)
        show_progress_x = self.params['looper'].get('show_progress_x', show_progress_x)

        # get X-axis values
        _xs, _vs = self._get_X_results(grad=grad, mode=mode, show_progress_x=show_progress_x)

        # update attributes
        self.results = {}
        self.results['X'] = _xs
        self.results['V'] = _vs

        # display completion
        logger.info('---------------------Results Obtained-------------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Results Obtained', progress=None, reset=True)

        return self.results