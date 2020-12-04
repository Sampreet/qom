#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface axes."""

__name__    = 'qom.ui.axes.BaseAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2020-12-04'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# TODO: Randomize colors, styles and sizes.

class BaseAxis():
    """Class to interface axes.

    Initializes `val`, `dim`, `bound`, `ticks` and `tick_labels` properties. Inherited objects need to set the other properties individually.

    Parameters
    ----------
        axis_data : int or list or dict
            Data for the axis.
    """

    @property
    def var(self):
        """str: Variable of the axis."""

        return self.__var

    @var.setter
    def var(self, var):
        self.__var = var

    @property
    def val(self):
        """list: Values of the axis."""

        return self.__val

    @val.setter
    def val(self, val):
        self.__val = val

    @property
    def dim(self):
        """int: Dimension of the axis."""

        return self.__dim

    @dim.setter
    def dim(self, dim):
        self.__dim = dim

    @property
    def name(self):
        """str: Display name of the axis."""

        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def unit(self):
        """str: Unit of the axis."""

        return self.__unit

    @unit.setter
    def unit(self, unit):
        self.__unit = unit

    @property
    def bound(self):
        """str: Option to check user-defined bounds:
            * 'none' : Not bounded.
            * 'lower' : Lower bound.
            * 'upper' : Upper bound.
            * 'both' : Both lower and upper bound.
        """

        return self.__bound

    @bound.setter
    def bound(self, bound):
        self.__bound = bound

    @property
    def ticks(self):
        """list: Ticks of the axis."""

        return self.__ticks

    @ticks.setter
    def ticks(self, ticks):
        self.__ticks = ticks

    @property
    def tick_labels(self):
        """list: Tick labels of the axis."""

        return self.__tick_labels

    @tick_labels.setter
    def tick_labels(self, tick_labels):
        self.__tick_labels = tick_labels

    @property
    def label(self):
        """str: Label of the axis."""

        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def legends(self):
        """list: Legends of the axis."""

        return self.__legends

    @legends.setter
    def legends(self, legends):
        self.__legends = legends

    @property
    def colors(self):
        """list: Colors for plots."""

        return self.__colors

    @colors.setter
    def colors(self, colors):
        self.__colors = colors

    @property
    def styles(self):
        """list: Styles of the plots."""

        return self.__styles

    @styles.setter
    def styles(self, styles):
        self.__styles = styles

    @property
    def sizes(self):
        """list: Sizes of the plots."""

        return self.__sizes

    @sizes.setter
    def sizes(self, sizes):
        self.__sizes = sizes

    def __init__(self, axis_data):
        """Class constructor for BaseAxis."""

        # if values
        if type(axis_data) is list:
            axis_data = {
                'val': axis_data
            }

        # validate parameter
        assert type(axis_data) is dict, 'Axis data should either be a `list` of values, or a `dict` containing "min", "max" and "dim" keys.'

        # frequently used variables
        _min = -1
        _max = 1
        _dim = 5
        
        # set val
        _val = axis_data.get('val', [])
        # if values are defined
        if type(_val) is list and len(_val) != 0:
            self.val = _val
        # else initizlize data
        else:
            self.val = self.init_array(axis_data.get('min', _min), axis_data.get('max', _max), axis_data.get('dim', _dim))

        # if values are not of type string, reset range
        if type(self.val[0]) is not str:
            _min = min(self.val)
            _max = max(self.val)

        # set dim
        self.dim = len(self.val)

        # check axis bounds
        if 'tick_min' in axis_data and 'tick_max' in axis_data:
            self.bound = 'both'
        elif 'tick_min' in axis_data:
            self.bound = 'lower'
        elif 'tick_max' in axis_data:
            self.bound = 'upper'
        else:
            self.bound = 'none'

        # set ticks
        _ticks = axis_data.get('ticks', [])
        # if ticks are defined
        if type(_ticks) is list and len(_ticks) != 0:
            self.ticks = _ticks
            # update bound
            self.bound = 'both'
        # else initialize ticks
        else:
            self.ticks = self.init_array(axis_data.get('tick_min', _min), axis_data.get('tick_max', _max), axis_data.get('tick_dim', _dim))

        # set tick labels
        _tick_labels = axis_data.get('tick_labels', [])
        # if ticks labels are defined
        if type(_tick_labels) is list and len(_tick_labels) != 0:
            self.tick_labels = _tick_labels
            # update bound
            self.bound = 'both'
        # else same as ticks
        else:
            self.tick_labels = self.ticks 

        # supersede tick labels over ticks
        if len(self.tick_labels) != len(self.ticks):
            self.ticks = self.init_array(1, len(self.tick_labels), len(self.tick_labels))

    def init_array(self, mini, maxi, num):
        """Function to initialize an array given a range and number of elements.

        Parameters
        ----------
        mini : int
            Minimum value of the range.
        maxi : int 
            Maximum value of the range.
        num : int
            Number of elements to consider.
        """
    
        values = (mini + np.arange(num) * (maxi - mini) / (num - 1))

        return values.tolist()
