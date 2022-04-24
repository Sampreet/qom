#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a 2D looper."""

__name__    = 'qom.loopers.XYLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-21'
__updated__ = '2022-03-19'

# dependencies
import logging

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
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined under the "looper" dictionary in ``params`` supersede individual method arguments. Refer :class:`qom.loopers.BaseLooper` for a complete list of supported options.
    """

    # attributes
    code = 'XYLooper'
    name = '2D Looper'
    
    def __init__(self, func, params: dict, cb_update=None):
        """Class constructor for XYLooper."""

        # initialize super class
        super().__init__(func=func, params=params, code=self.code, name=self.name, cb_update=cb_update)

        # set axes
        self._set_axis(axis='X')
        self._set_axis(axis='Y')

        # display initialization
        logger.info('--------------------Looper Initialized-----------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Looper Initialized', progress=None)

    def loop(self, grad: bool=False, grad_position='all', grad_mono_idx: int=0, mode: str='serial', show_progress_x: bool=False, show_progress_y: bool=True):
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
                "all"           all values.
                "mean"          mean of the axis values.
                "mono_mean"     mean of the monotonic patches in calculated values.
                "mono_min"      local minima of the monotonic patches.
                "mono_max"      local maxima of the monotonic patches.
                ==============  ====================================================
        grad_mono_idx: int, optional
            Index of the monotonic patch.
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
            Option to display the progress for the calculation of results in X-axis. Default is `False`.
        show_progress_y : bool, optional
            Option to display the progress for the calculation of results in Y-axis. Default is `True`.

        Returns
        -------
        results : dict
            Axes and calculated values containing the keys "X", "Y" and "V". If ``grad`` is ``True`` and ``grad_position`` is not "all", key "Y" is not returned.
        """

        # supersede arguments by looper parameters
        grad = self.params['looper'].get('grad', grad)
        grad_position = self.params['looper'].get('grad_position', grad_position)
        grad_mono_idx = self.params['looper'].get('grad_mono_idx', grad_mono_idx)
        mode = self.params['looper'].get('mode', mode)
        show_progress_x = self.params['looper'].get('show_progress_x', show_progress_x)
        show_progress_y = self.params['looper'].get('show_progress_y', show_progress_y)

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
            if show_progress_y:
                self._update_progress(pos=k, dim=len(y_val))

            # update system parameter
            _val = y_val[k]
            if y_idx is not None:
                # handle non system parameter
                if system_params.get(y_var, None) is None:
                    system_params[y_var] = [0 for _ in range(y_idx + 1)]
                system_params[y_var][y_idx] = _val
            else:
                system_params[y_var] = _val

            # get X-axis values
            _temp_xs, _temp_vs = self._get_X_results(grad=grad, mode=mode, show_progress_x=show_progress_x)

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
                idx = self._get_grad_index(axis_values=_xs[i], grad_position=grad_position, grad_mono_index=grad_mono_idx)
                self.results['X'].append(_ys[i][idx])
                self.results['V'].append(_vs[i][idx])
        # no gradient calculation or gradients at all positions
        else:
            self.results['X'] = _xs
            self.results['Y'] = _ys
            self.results['V'] = _vs

        # display completion
        logger.info('--------------------Results Obtained-------------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Results Obtained', progress=None, reset=True)

        return self.results