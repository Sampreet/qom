#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to handle a dynamic axis."""

__name__    = 'qom.ui.axes.DynamicAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2022-06-11'

# dependencies
import logging

# qom modules
from .BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

class DynamicAxis(BaseAxis):
    """Class to handle a dynamic axis.

    Parameters
    ----------
    axis : str
        Name of the axis, or "X", "Y", "Z" or "V".
    axis_params : dict or list
        Values for the axis supporting a list of values or a dictionary containing the range of values with keys "min", "max", "dim" and "scale" or the values themselves under key "val".
    plotter_params : dict
        Parameters for the plotter. Along with the keys defined in :class:`qom.ui.axes.BaseAxis`, additionally supported keys are:
            ==============  ====================================================
            key             value
            ==============  ====================================================
            "name"          (*str*) display name of the axis. Default is 'DynamicAxis'.
            "unit"          (*str*) unit of the plots.
            ==============  ====================================================
    """

    def __init__(self, axis, axis_params, plotter_params):
        """Class constructor for DynamicAxis."""

        # initialize super class
        super().__init__(axis, axis_params, plotter_params)

        # set name
        self.name = plotter_params.get(axis.lower() + '_name', 'DynamicAxis')

        # set unit
        self.unit = plotter_params.get(axis.lower() + '_unit', self.axis_defaults['unit'])

        # update label
        if self.label == '' and not 'DynamicAxis' in self.name:
            self.label = self.name if self.unit == '' else '{name} ({unit})'.format(name=self.name, unit=self.unit)