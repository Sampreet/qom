#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle a dynamic axis."""

__name__    = 'qom.ui.axes.DynamicAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2021-01-06'

# dependencies
import logging
import numpy as np

# dev dependencies
from qom.ui.axes.BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

class DynamicAxis(BaseAxis):
    """Class to handle a dynamic axis.

    Inherits :class:`qom.ui.axes.BaseAxis`.

    Parameters
    ----------
    axis_data : int or list or dict
        Data for the axis.
    """

    def __init__(self, axis_data={}):
        """Class constructor for DynamicAxis."""

        # initialize super class
        super().__init__(axis_data)

        # set var 
        self.var = axis_data.get('var', 'dynamic_axis')

        # set name
        self.name = axis_data.get('name', '')

        # set unit
        self.unit = axis_data.get('unit', '')

        # set bound
        self.bound = axis_data.get('bound', 'none')

        # set label
        if axis_data.get('label', '') == '':
            self.label = self.name + ' (' + self.unit + ')' if self.unit != '' else self.name
        # supersede axis_data
        else:
            self.label = axis_data['label']