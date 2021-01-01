#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle a multi-value axis."""

__name__    = 'qom.ui.axes.MultiAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2021-01-01'

# TODO: set color and style variants.

# dependencies
import logging
import numpy as np

# dev dependencies
from qom.ui.axes.BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

class MultiAxis(BaseAxis):
    """Class to handle a multi-value axis.

    Inherits :class:`qom.ui.axes.BaseAxis`.

    Parameters
    ----------
    axis_data : int or list or dict
        Data for the axis.
    """

    def __init__(self, axis_data={}):
        """Class constructor for MultiAxis."""

        # initialize super class
        super().__init__(axis_data)

        # set var
        self.var = axis_data.get('var', 'multi_axis')

        # set name
        self.name = axis_data.get('name', '')

        # set unit
        self.unit = axis_data.get('unit', '')

        # set legends
        self.legends = ['{name} = {value} {unit}'.format(name=self.name, value=v, unit=self.unit) for v in self.val]

        # set colors
        _colors = axis_data.get('colors', [])
        # if colors are defined
        if type(_colors) is list and len(_colors) == self.dim:
            self.colors = _colors
        # else set individual colors
        else:
            self.colors = ['r' for i in range(self.dim)]

        # set sizes
        _sizes = axis_data.get('sizes', [])
        # if sizes are defined
        if type(_sizes) is list and len(_sizes) == self.dim:
            self.sizes = _sizes
        # else set individual sizes
        else:
            self.sizes = [2 for i in range(self.dim)]

        # set styles
        _styles = axis_data.get('styles', [])
        # if styles are defined
        if type(_styles) is list and len(_styles) == self.dim:
            self.styles = _styles
        # else set individual styles
        else:
            self.styles = ['-' for i in range(self.dim)]