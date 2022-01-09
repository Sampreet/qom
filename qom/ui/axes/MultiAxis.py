#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to handle a multi-value axis."""

__name__    = 'qom.ui.axes.MultiAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2022-01-02'

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
    params : dict or list
        Parameters for the axis supporting a list of values or a dictionary of parameters. Refer :class:`qom.ui.axes.BaseAxis` for currently supported keys.
    """

    def __init__(self, params={}):
        """Class constructor for MultiAxis."""

        # initialize super class
        super().__init__(params)

        # set var
        self.var = params.get('var', 'multi_axis')

        # set name
        self.name = params.get('name', '')

        # set unit
        self.unit = params.get('unit', '')

        # set params
        self.legend = params.get('legend', '')
        if self.name == '' and self.var == 'multi_axis':
            self.legend = ['{value} {unit}'.format(value=v, unit=self.unit) for v in self.val]
        elif self.legend == '':
            self.legend = ['{name} = {value} {unit}'.format(name=self.name if self.name != '' else self.var, value=v, unit=self.unit) for v in self.val]

        # set colors
        _colors = params.get('colors', [])
        # if colors are defined
        if type(_colors) is list and len(_colors) != 0:
            self.colors = _colors
        # else set default colors
        else:
            self.colors = None

        # set sizes
        _sizes = params.get('sizes', [])
        # if sizes are defined
        if type(_sizes) is list and len(_sizes) != 0:
            self.sizes = _sizes
        # else set default sizes
        else:
            self.sizes = None

        # set styles
        _styles = params.get('styles', [])
        # if styles are defined
        if type(_styles) is list and len(_styles) != 0:
            self.styles = _styles
        # else set default styles
        else:
            self.styles = None