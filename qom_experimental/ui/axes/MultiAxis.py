#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to handle a multi axis."""

__name__    = 'qom_experimental.ui.axes.MultiAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2020-10-19'

# dependencies
import logging
import numpy as np

# dev dependencies
from qom_experimental.ui.axes.BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

class MultiAxis(BaseAxis):
    """Class to handle a multi axis.

    Inherits :class:`qom.ui.axes.BaseAxis`.
    """

    def __init__(self, axis_data):
        """Class constructor for MultiAxis.

        Parameters
        ----------
            axis_data : int or list or dict
                Data for the axis.
        """

        # initialize super class
        super().__init__(axis_data)

        # set var
        self.var = axis_data.get('var', 'multi_axis')

        # set name
        self.name = axis_data.get('name', self.var)

        # set unit
        self.unit = axis_data.get('unit', '')

        # set legends
        self.legends = ['{name} = {value} {unit}'.format(label=self.name, value=v, unit=self.unit) for v in self.val]