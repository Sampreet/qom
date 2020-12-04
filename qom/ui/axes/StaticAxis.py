#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle a static axis."""

__name__    = 'qom.ui.axes.StaticAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2020-12-04'

# dependencies
import logging
import numpy as np

# dev dependencies
from qom.ui.axes.BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle index-based initialization.

class StaticAxis(BaseAxis):
    """Class to handle a static axis.

    Inherits :class:`qom.utils.axes.BaseAxis`.

    Parameters
    ----------
    axis_data : int or list or dict
        Data for the axis.
    """

    def __init__(self, axis_data={}):
        """Class constructor for StaticAxis."""

        # initialize super class
        super().__init__(axis_data)

        # set var
        self.var = axis_data.get('var', 'static_axis')

        # set name
        self.name = axis_data.get('name', '')

        # set unit
        self.unit = axis_data.get('unit', '')

        # set label
        self.label = self.name + ' (' + self.unit + ')' if self.unit != '' else self.name