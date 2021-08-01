#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a 2D looper."""

__name__    = 'qom.loopers.XYLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2021-08-01'

# dependencies
from typing import Union
import logging
import numpy as np

# qom modules
from .BaseLooper import BaseLooper

# module logger
logger = logging.getLogger(__name__)

class XYLooper(BaseLooper):
    """Class to interface a 2D looper.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params, val, logger, results)``, where ``system_params`` is a dictionary of the parameters for the system, ``val`` is the current value of the looping parameter, ``logger`` is an instance of the module logger and ``results`` is a list of tuples each containing ``val`` and the value calculated within the function.
    params : dict
        Parameters for the looper and optionally, the system and the plotter. The "looper" key is a dictionary containing the keys "X" and "Y", each with the keys "var" and "val" for the name of the parameter to loop and its corresponding values, along with additional options (refer notes).


    .. note:: All the options defined under the "looper" dictionary in ``params`` supersede individual function arguments. Refer :class:`qom.loopers.BaseLooper` for a complete list of supported options.
    """

    def __init__(self, func, params: dict):
        """Class constructor for XYLooper."""

        # initialize super class
        super().__init__(func=func, params=params, code='xy_looper', name='2D Looper')

        # set axes
        self._set_axis(axis='X')
        self._set_axis(axis='Y')

        # display initialization
        logger.info('--------------------Looper Initialized-----------------\t\n')

    def loop(self, grad: bool=False, grad_position='all', grad_mono_idx: int=0, mode: str='serial'):
        """Method to calculate the output of a given function for each X-axis and Y-axis point.
        
        Parameters
        ----------
        grad : bool, optional
            Option to calculate gradients with respect to the X-axis.
        grad_position: str or float, optional
            A value denoting the position or a mode to calculate the position. For a position other than "all" and "mean", the ``grad_mono_idx`` parameter should be filled. The different positions can be:
                ==============  ====================================================
                value           meaning
                ==============  ====================================================
                "all"           consider all values.
                "mean"          mean of the axis values.
                "mono_mean"     mean of the monotonic patches in calculated values.
                "mono_min"      local minima of the monotonic patches.
                "mono_max"      local maxima of the monotonic patches.
                ==============  ====================================================
        grad_mono_idx: int, optional
            Index of the monotonic patch.
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
        results : dict
            Axes and calculated values containing the keys "X", "Y" and "V". If ``grad`` is ``True`` and ``grad_position`` is not "all", key "Y" is not returned.
        """

        # supersede looper parameters
        grad = self.params['looper'].get('grad', grad)
        grad_position = self.params['looper'].get('grad_position', grad_position)
        grad_mono_idx = self.params['looper'].get('grad_mono_idx', grad_mono_idx)

        # validate parameters
        supported_types = Union[str, int, float, np.float32, np.float64].__args__
        assert isinstance(grad_position, supported_types), 'Parameter ``grad_position`` should be either of the types: {}'.format(supported_types)

        # extract frequently used variables
        system_params = self.params['system']
        y_var = self.axes['Y']['var']
        y_idx = self.axes['Y']['idx']
        y_val = self.axes['Y']['val']

        # initialize axes
        _xs = list()
        _ys = list()
        _vs = list()

        # iterate Y-axis values
        for k in range(len(y_val)):
            # update progress
            self.update_progress(pos=k, dim=len(y_val))

            # update system parameter
            _val = y_val[k]
            if y_idx is not None:
                system_params[y_var][y_idx] = _val
            else:
                system_params[y_var] = _val

            # get X-axis values
            _temp_xs, _temp_vs = self.get_X_results(grad=grad, mode=mode)

            # upate lists
            _xs.append(_temp_xs)
            _ys.append([_val] * len(_temp_xs))
            _vs.append(_temp_vs)

        # update attributes
        self.results = {}
        # gradient at approximate position
        if grad and not grad_position == 'all':
            self.results['X'] = list()
            self.results['V'] = list()
            for i in range(len(_xs)):
                idx = self.get_grad_index(axis_values=_xs[i])
                self.results['X'].append(_ys[i][idx])
                self.results['V'].append(_vs[i][idx])
        # no gradient calculation or gradients at all positions
        else:
            self.results['X'] = _xs
            self.results['Y'] = _ys
            self.results['V'] = _vs

        # display completion
        logger.info('--------------------Results Obtained-------------------\t\n')

        return self.results