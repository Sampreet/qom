#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to handle axes loopers."""

__name__ = 'qom.loopers.axes'
__authors__ = ["Sampreet Kalita"]
__created__ = "2020-12-21"
__updated__ = "2023-07-12"

# dependencies
import numpy as np

# qom modules
from .base import BaseLooper

class XLooper(BaseLooper):
    """Class to interface a 1D looper.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params)``, where ``system_params`` is a dictionary of the updated parameters for the system for that iteration of the looper.
    params : dict
        Parameters of the looper containing the key ``'X'``, each with the keys ``'var'`` and ``'val'`` (or ``'min'``, ``'max'`` and ``'dim'``) for the name of the parameter to loop and its corresponding values (or minimum and maximum values along with dimension). Refer to **Notes** of :class:`qom.loopers.base.BaseLooper` for all available options.
    params_system : dict, optional
        Parameters of the system. If not provided, new keys are created for the looper variables.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.
    """

    # attributes
    name = 'XLooper'
    """str : Name of the looper."""
    desc = "1D Looper"
    """str : Description of the looper."""
    
    def __init__(self, func, params:dict, params_system:dict={}, cb_update=None, parallel:bool=False, p_index:int=0, p_start:float=None):
        """Class constructor for XLooper."""

        # initialize super class
        super().__init__(
            func=func,
            params=params,
            params_system=params_system,
            cb_update=cb_update,
            parallel=parallel,
            p_index=p_index,
            p_start=p_start
        )

    def loop(self):
        """Method to calculate the output of a given function for each X-axis point.

        Returns
        -------
        results : dict
            Axes and calculated values containing the keys ``'X'`` and ``'V'``.
        """

        # get X-axis values
        _xs, _vs = self.get_X_results()

        # update attributes
        self.results = dict()
        self.results['X'] = _xs
        self.results['V'] = _vs

        # display completion
        if self.params['show_progress']:
            self.updater.update_progress(
                pos=1,
                dim=1,
                status="-" * (26 - len(self.name)) + "Looping axes values",
                reset=False
            )
            self.updater.update_info(
                status="-" * 42 + "Results Obtained"
            )

        return self.results

class XYLooper(BaseLooper):
    """Class to interface a 2D looper.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params)``, where ``system_params`` is a dictionary of the updated parameters for the system for that iteration of the looper.
    params : dict
        Parameters of the looper containing the key ``'X'`` and ``'Y'``, each with the keys ``'var'`` and ``'val'`` (or ``'min'``, ``'max'`` and ``'dim'``) for the name of the parameter to loop and its corresponding values (or minimum and maximum values along with dimension). Refer to **Notes** of :class:`qom.loopers.base.BaseLooper` for all available options.
    params_system : dict, optional
        Parameters of the system. If not provided, new keys are created for the looper variables.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.
    """

    # attributes
    name = 'XYLooper'
    """str : Name of the looper."""
    desc = "2D Looper"
    """str : Description of the looper."""
    
    def __init__(self, func, params:dict, params_system:dict, cb_update=None, parallel:bool=False, p_index:int=0, p_start:float=None):
        """Class constructor for XYLooper."""

        # initialize super class
        super().__init__(
            func=func,
            params=params,
            params_system=params_system,
            cb_update=cb_update,
            parallel=parallel,
            p_index=p_index,
            p_start=p_start
        )

    def loop(self):
        """Method to calculate the output of a given function for each X-axis and Y-axis points.

        Returns
        -------
        results : dict
            Axes and calculated values containing the keys ``'X'``, ``'Y'`` and ``'V'``. If the value of the parameter ``'grad'`` is set to ``True`` and ``'grad_position'`` is not ``'all'``, then the key ``'Y'`` is not returned.
        """

        # extract frequently used variables
        y_var = self.axes['Y']['var']
        y_idx = self.axes['Y']['idx']
        y_val = self.axes['Y']['val']

        # initialize variables
        _xs = list()
        _ys = list()
        _vs = list()
        self.pos = 0
        self.dim = len(y_val)

        # iterate Y-axis values
        for k in range(len(y_val)):
            # update position for progress
            self.pos = k

            # update system parameter
            _val = y_val[k]
            if y_idx is not None:
                # handle non system parameter
                if self.params_system.get(y_var, None) is None:
                    self.params_system[y_var] = [0 for _ in range(y_idx + 1)]
                self.params_system[y_var][y_idx] = _val
            else:
                self.params_system[y_var] = _val

            # get X-axis values
            _temp_xs, _temp_vs = self.get_X_results()

            # upate lists
            _xs.append(_temp_xs)
            _ys.append([_val] * len(_temp_xs))
            _vs.append(_temp_vs)

        # update attributes
        self.results = dict()
        # gradient at approximate position
        if self.params['grad'] and not self.params['grad_position'] == 'all':
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
        if self.params['show_progress']:
            self.updater.update_progress(
                pos=1,
                dim=1,
                status="-" * (26 - len(self.name)) + "Looping axes values",
                reset=False
            )
            self.updater.update_info(
                status="-" * 41 + "Results Obtained"
            )

        return self.results

class XYZLooper(BaseLooper):
    """Class to interface a 3D looper.

    Parameters
    ----------
    func : callable
        Function to loop, formatted as ``func(system_params)``, where ``system_params`` is a dictionary of the updated parameters for the system for that iteration of the looper.
    params : dict
        Parameters of the looper containing the key ``'X'``, ``'Y'`` and ``'Z'``, each with the keys ``'var'`` and ``'val'`` (or ``'min'``, ``'max'`` and ``'dim'``) for the name of the parameter to loop and its corresponding values (or minimum and maximum values along with dimension). Refer to **Notes** of :class:`qom.loopers.base.BaseLooper` for all available options.
    params_system : dict, optional
        Parameters of the system. If not provided, new keys are created for the looper variables.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.
    """

    # attributes
    name = 'XYZLooper'
    """str : Name of the looper."""
    desc = "3D Looper"
    """str : Description of the looper."""
    
    def __init__(self, func, params:dict, params_system:dict, cb_update=None, parallel:bool=False, p_index:int=0, p_start:float=None):
        """Class constructor for XYZLooper."""

        # initialize super class
        super().__init__(
            func=func,
            params=params,
            params_system=params_system,
            cb_update=cb_update,
            parallel=parallel,
            p_index=p_index,
            p_start=p_start
        )

    def loop(self):
        """Method to calculate the output of a given function for each X-axis, Y-axis and Z-axis points.

        Returns
        -------
        results : dict
            Axes and calculated values containing the keys ``'X'``, ``'Y'``. ``'Z'`` and ``'V'``. If the value of the parameter ``'grad'`` is set to ``True`` and ``'grad_position'`` is not ``'all'``, then the key ``'Z'`` is not returned.
        """

        # extract frequently used variables
        show_progress = self.params['show_progress']
        y_var = self.axes['Y']['var']
        z_var = self.axes['Z']['var']
        y_idx = self.axes['Y']['idx']
        z_idx = self.axes['Z']['idx']
        y_val = self.axes['Y']['val']
        z_val = self.axes['Z']['val']

        # initialize axes
        _xs = list()
        _ys = list()
        _zs = list()
        _vs = list()
        self.pos = 0
        self.dim = len(y_val) * len(z_val)

        # iterate Y-axis and Z-axis values
        for k in range(self.dim):
            # update position for progress
            self.pos = k

            # get values
            _y = y_val[int(k % len(y_val))]
            _z = z_val[int(k / len(y_val))]

            # update system parametes
            if y_idx is not None:
                # handle non system parameter
                if self.params_system.get(y_var, None) is None:
                    self.params_system[y_var] = [0 for _ in range(y_idx + 1)]
                self.params_system[y_var][y_idx] = _y
            else:
                self.params_system[y_var] = _y
            if z_idx is not None:
                # handle non system parameter
                if self.params_system.get(z_var, None) is None:
                    self.params_system[z_var] = [0 for _ in range(z_idx + 1)]
                self.params_system[z_var][z_idx] = _z
            else:
                self.params_system[z_var] = _z

            # get X-axis values
            _temp_xs, _temp_vs = self.get_X_results()

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
        if self.params['grad'] and not self.params['grad_position'] == 'all':
            self.results['X'] = list()
            self.results['Y'] = list()
            self.results['V'] = list()
            for i in range(len(_xs)):
                _temp_xs = list()
                _temp_ys = list()
                _temp_vs = list()
                for j in range(len(_xs[i])):
                    idx = self.get_grad_index(axis_values=_xs[i][j])
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
        if show_progress:
            self.updater.update_progress(
                pos=1,
                dim=1,
                status="-" * (26 - len(self.name)) + "Looping axes values",
                reset=False
            )
            self.updater.update_info(
                status="-" * 40 + "Results Obtained"
            )

        return self.results