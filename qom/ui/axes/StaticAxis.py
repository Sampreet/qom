#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to handle a static axis."""

__name__    = 'qom.ui.axes.StaticAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2021-08-02'

# dependencies
import logging

# qom modules
from .BaseAxis import BaseAxis

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle index-based initialization.

class StaticAxis(BaseAxis):
    """Class to handle a static axis.

    Parameters
    ----------
    params : dict or list
        Parameters for the axis supporting a list of values or a dictionary of parameters. Refer :class:`qom.ui.axes.BaseAxis` for currently supported keys.
    """

    def __init__(self, params={}):
        """Class constructor for StaticAxis."""

        # initialize super class
        super().__init__(params)

        # set var
        self.var = params.get('var', 'static_axis')

        # set name
        self.name = params.get('name', '')

        # set unit
        self.unit = params.get('unit', '')

        # set label
        if params.get('label', '') == '':
            self.label = self.name + ' (' + self.unit + ')' if self.unit != '' else self.name
        # supersede axis_data
        else:
            self.label = params['label']