#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a 3D looper."""

__name__    = 'qom.loopers.XYZLooper'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-28'
__updated__ = '2021-03-22'

# dependencies
from typing import Union
import logging
import numpy as np

# qom modules
from .BaseLooper import BaseLooper

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_position = Union[str, int, float, np.float32, np.float64]

class XYZLooper(BaseLooper):
    """Class to interface a 3D looper.
    
    Inherits :class:`qom.systems.BaseSystem`.

    Parameters
    ----------
    func : function
        Function to loop.
    params : dict
        Parameters for the system, looper and figure.
    """

    def __init__(self, func, params: dict):
        """Class constructor for XYZLooper."""

        # initialize super class
        super().__init__(func, params, 'XYZLooper', '3D Looper')

        # set axes
        self._set_axis('X')
        self._set_axis('Y')
        self._set_axis('Z')

        # display initialization
        logger.info('-------------------Looper Initialized-----------------\t\n')

    def loop(self, mode: str='serial', grad: bool=False, grad_position: t_position='all', grad_mono_idx: int=0, plot: bool=False):
        """Method to calculate the output of a given function for each X-axis Y-axis and Z-axis point.
        
        Parameters
        ----------
        mode : str, optional
            Mode of execution:
                'serial': Single-thread computation.
                'multithread': Multi-thread computation.
                'multiprocess': Multi-processor computation.
        grad : bool, optional
            Option to calculate gradients with respect to the first axis, superseded by looper parameter `grad`.
        grad_position: str or float, optional
            A value denoting the position or a mode to calculate the position, superseded by looper parameter `grad_position`. For a mode other than 'mean', the `mono_idx` parameter should be filled. The different modes can be:
                'all': Consider all values.
                'mean': Mean of the axis values.
                'mono_mean': Mean of the monotonic patches in calculated values.
                'mono_min': Local minima of the monotonic patches.
                'mono_max': Local maxima of the monotonic patches.
        grad_mono_idx: int, optional
            Index of the monotonic patch, superseded by looper parameter `grad_mono_idx`.
        plot: bool, optional
            Option to plot the results.

        Returns
        -------
        results : dict
            Axes and calculated values.
        """

        # extract frequently used variables
        system_params = self.params['system']
        ys = self.axes['Y']['val']
        zs = self.axes['Z']['val']
        dim = len(ys) * len(zs)

        # supersede looper parameters
        grad = self.params['looper'].get('grad', grad)
        grad_position = self.params['looper'].get('grad_position', grad_position)
        grad_mono_idx = self.params['looper'].get('grad_mono_idx', grad_mono_idx)
        plot = self.params['looper'].get('plot', plot)

        # initialize axes
        _xs = list()
        _ys = list()
        _zs = list()
        _vs = list()

        # iterate Y-axis and Z-axis values
        for k in range(dim):
            # update progress
            self.update_progress(k, dim)

            # get values
            _y = ys[int(k % len(ys))]
            _z = zs[int(k / len(ys))]

            # update system parametes
            system_params[self.axes['Y']['var']] = _y
            system_params[self.axes['Z']['var']] = _z

            # get X-axis values
            _temp_xs, _temp_vs = self.get_X_results(mode, grad)

            # upate lists
            _xs.append(_temp_xs)
            _ys.append([_y] * len(_temp_xs))
            _zs.append([_z] * len(_temp_xs))
            _vs.append(_temp_vs)

        # reshape results
        _, _x_dim = np.shape(_xs)
        _xs = np.reshape(_xs, (len(zs), len(ys), _x_dim)).tolist()
        _ys = np.reshape(_ys, (len(zs), len(ys), _x_dim)).tolist()
        _zs = np.reshape(_zs, (len(zs), len(ys), _x_dim)).tolist()
        _vs = np.reshape(_vs, (len(zs), len(ys), _x_dim)).tolist()

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
        logger.info('-------------------Values Obtained--------------------\t\n')

        # plot results
        if plot:
            self.plot_results()
    
            # update log
            logger.info('--------------------Results Plotted--------------------\t\n')

        return self.results



        


