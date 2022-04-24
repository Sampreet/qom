#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to handle a multi-value axis."""

__name__    = 'qom.ui.axes.MultiAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2022-04-24'

# TODO: set color and style variants.

# dependencies
import logging

# qom modules
from .BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

class MultiAxis(BaseAxis):
    """Class to handle a multi-value axis.

    Parameters
    ----------
    axis : str
        Name of the axis, "X", "Y", "Z" or "V".
    axis_params : dict or list
        Values for the axis supporting a list of values or a dictionary containing the range of values with keys "min", "max", "dim" and "scale" or the values themselves under key "val".
    plotter_params : dict
        Parameters for the plotter. Along with the keys defined in :class:`qom.ui.axes.BaseAxis`, additionally supported keys are:
            ==============  ====================================================
            key             value
            ==============  ====================================================
            "colors"        (*list*) colors for plots.
            "legend"        (*list*) legend of the plots.
            "name"          (*str*) display name of the axis.
            "sizes"         (*list*) sizes of the plots.
            "styles"        (*list*) styles of the plots.
            "unit"          (*str*) unit of the plots.
            ==============  ====================================================
    """

    def __init__(self, axis, axis_params, plotter_params):
        """Class constructor for MultiAxis."""

        # initialize super class
        super().__init__(axis, axis_params, plotter_params)

        # set name
        self.name = plotter_params.get(axis.lower() + '_name', 'MultiAxis')

        # set unit
        self.unit = plotter_params.get(axis.lower() + '_unit', self.axis_defaults['unit'])

        # set params
        _legend = plotter_params.get(axis.lower() + '_legend', self.axis_defaults['legend'])
        # if legend are defined
        if type(_legend) is list and len(_legend) != 0:
            self.legend = _legend
        # else set legend from name value and unit
        else:
            if self.name == 'MultiAxis':
                self.legend = ['{value} {unit}'.format(value=v, unit=self.unit) for v in self.val]
            else:
                self.legend = ['{name} = {value} {unit}'.format(name=self.name, value=v, unit=self.unit) for v in self.val]

        # set colors
        _colors = plotter_params.get(axis.lower() + '_colors', self.axis_defaults['colors'])
        # if colors are defined
        if type(_colors) is list and len(_colors) != 0:
            self.colors = _colors
        # else set default colors
        else:
            self.colors = None

        # set sizes
        _sizes = plotter_params.get(axis.lower() + '_sizes', self.axis_defaults['sizes'])
        # if sizes are defined
        if type(_sizes) is list and len(_sizes) != 0:
            self.sizes = _sizes
        # else set default sizes
        else:
            self.sizes = None

        # set styles
        _styles = plotter_params.get(axis.lower() + '_styles', self.axis_defaults['styles'])
        # if styles are defined
        if type(_styles) is list and len(_styles) != 0:
            self.styles = _styles
        # else set default styles
        else:
            self.styles = None