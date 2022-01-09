#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface a 3D looper."""

__name__    = 'qom.loopers.XYZLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-28'
__updated__ = '2022-01-09'

# dependencies
from typing import Union
import logging
import numpy as np

# qom modules
from .BaseLooper import BaseLooper

# module logger
logger = logging.getLogger(__name__)

class XYZLooper(BaseLooper):
    """Class to interface a 3D looper.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params, val, logger, results)``, where ``system_params`` is a dictionary of the parameters for the system, ``val`` is the current value of the looping parameter, ``logger`` is an instance of the module logger and ``results`` is a list of tuples each containing ``val`` and the value calculated within the function.
    params : dict
        Parameters for the looper and optionally, the system and the plotter. The "looper" key is a dictionary containing the keys "X", "Y" and "Z", each with the keys "var" and "val" for the name of the parameter to loop and its corresponding values, along with additional options (refer notes).
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is an integer and ``reset`` is a boolean.

    .. note:: All the options defined under the "looper" dictionary in ``params`` supersede individual function arguments. Refer :class:`qom.loopers.BaseLooper` for a complete list of supported options.
    """

    # attributes
    code = 'xyz_looper'
    name = '3D Looper'
    
    def __init__(self, func, params: dict, cb_update=None):
        """Class constructor for XYZLooper."""

        # initialize super class
        super().__init__(func=func, params=params, code=self.code, name=self.name, cb_update=cb_update)

        # set axes
        self._set_axis(axis='X')
        self._set_axis(axis='Y')
        self._set_axis(axis='Z')

        # display initialization
        logger.info('-------------------Looper Initialized-----------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Looper Initialized', progress=None)

    def loop(self, grad: bool=False, grad_position='all', grad_mono_idx: int=0, mode: str='serial'):
        """Method to calculate the output of a given function for each X-axis Y-axis and Z-axis point.
        
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
            Axes and calculated values containing the keys "X", "Y", "Z" and "V". If ``grad`` is ``True`` and ``grad_position`` is not "all", key "Z" is not returned.
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
        z_var = self.axes['Z']['var']
        y_idx = self.axes['Y']['idx']
        z_idx = self.axes['Z']['idx']
        y_val = self.axes['Y']['val']
        z_val = self.axes['Z']['val']
        dim = len(y_val) * len(z_val)

        # initialize axes
        _xs = list()
        _ys = list()
        _zs = list()
        _vs = list()

        # iterate Y-axis and Z-axis values
        for k in range(dim):
            # update progress
            self.update_progress(pos=k, dim=dim)

            # get values
            _y = y_val[int(k % len(y_val))]
            _z = z_val[int(k / len(y_val))]

            # update system parametes
            if y_idx is not None:
                # handle non system parameter
                if system_params.get(y_var, None) is None:
                    system_params[y_var] = [0 for _ in range(y_idx + 1)]
                system_params[y_var][y_idx] = _y
            else:
                system_params[y_var] = _y
            if z_idx is not None:
                # handle non system parameter
                if system_params.get(z_var, None) is None:
                    system_params[z_var] = [0 for _ in range(z_idx + 1)]
                system_params[z_var][z_idx] = _z
            else:
                system_params[z_var] = _z

            # get X-axis values
            _temp_xs, _temp_vs = self.get_X_results(grad=grad, mode=mode)

            # upate lists
            _xs.append(_temp_xs)
            _ys.append([_y] * len(_temp_xs))
            _zs.append([_z] * len(_temp_xs))
            _vs.append(_temp_vs)

        # reshape results
        _, _x_dim = np.shape(_xs)
        _xs = np.reshape(_xs, (len(z_val), len(y_val), _x_dim)).tolist()
        _ys = np.reshape(_ys, (len(z_val), len(y_val), _x_dim)).tolist()
        _zs = np.reshape(_zs, (len(z_val), len(y_val), _x_dim)).tolist()
        _vs = np.reshape(_vs, (len(z_val), len(y_val), _x_dim)).tolist()

        # update attributes
        self.results = {}
        # gradient at approximate position
        if grad and not grad_position == 'all':
            self.results['X'] = list()
            self.results['Y'] = list()
            self.results['V'] = list()
            for i in range(len(_xs)):
                _temp_xs = list()
                _temp_ys = list()
                _temp_vs = list()
                for j in range(len(_xs[i])):
                    idx = self.get_index(_xs[i][j])
                    _temp_xs.append(_ys[i][j][idx])
                    _temp_ys.append(_zs[i][j][idx])
                    _temp_vs.append(_vs[i][j][idx])
                self.results['X'].append(_temp_xs)
                self.results['Y'].append(_temp_ys)
                self.results['V'].append(_temp_vs)
        # no gradient calculation or gradients at all positions
        else:
            self.results['X'] = _xs
            self.results['Y'] = _ys
            self.results['Z'] = _zs
            self.results['V'] = _vs

        # display completion
        logger.info('-------------------Results Obtained-------------------\t\n')
        if self.cb_update is not None:
            self.cb_update(status='Results Obtained', progress=None, reset=True)

        return self.results