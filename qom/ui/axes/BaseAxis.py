#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface axes."""

__name__    = 'qom.ui.axes.BaseAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2021-08-27'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# TODO: Randomize colors, styles and sizes.

class BaseAxis():
    """Class to interface axes.

    Initializes ``val``, ``dim``, ``bound``, ``ticks`` and ``tick_labels`` properties. Inherited objects need to set the other properties individually.

    Parameters
    ----------
    params : dict or list
        Parameters for the axis supporting a list of values or a dictionary of parameters. Currently supported keys are:
            ==============  ====================================================
            key             value
            ==============  ====================================================
            "bound"         (*str*) option to check user-defined bounds, assuming either of "both", "lower", "none" or "upper".
            "colors"        (*str*) colors for plots.
            "dim"           (*int*) dimension of the axis.
            "label"         (*str*) label of the axis.
            "legend"        (*list*) legend of the plots.
            "max"           (*float*) max value of the axis.
            "min"           (*float*) min value of the axis.
            "name"          (*str*) display name of the axis.
            "sizes"         (*list*) sizes of the plots.
            "styles"        (*list*) styles of the plots.
            "tick_labels"   (*list*) tick labels of the plots.
            "ticks"         (*list*) ticks of the plots.
            "unit"          (*str*) unit of the plots.
            "val"           (*list*) values of the plots.
            "var"           (*str*) variable of the plots.
            ==============  ====================================================
    """

    @property
    def bound(self):
        """str: Option to check user-defined bounds:
            ==========  ====================================================
            value       meaning
            ==========  ====================================================
            "both"      both upper and lower bounds.
            "lower"     lower bound.
            "none"      not bounded (fallback).
            "upper"     uper bound.
            ==========  ====================================================
        """

        return self.__bound

    @bound.setter
    def bound(self, bound):
        self.__bound = bound

    @property
    def colors(self):
        """list: Colors for plots."""

        return self.__colors

    @colors.setter
    def colors(self, colors):
        self.__colors = colors

    @property
    def dim(self):
        """int: Dimension of the axis."""

        return self.__dim

    @dim.setter
    def dim(self, dim):
        self.__dim = dim

    @property
    def label(self):
        """str: Label of the axis."""

        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def legend(self):
        """list: Legends of the axis."""

        return self.__legend

    @legend.setter
    def legend(self, legend):
        self.__legend = legend

    @property
    def name(self):
        """str: Display name of the axis."""

        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def sizes(self):
        """list: Sizes of the plots."""

        return self.__sizes

    @sizes.setter
    def sizes(self, sizes):
        self.__sizes = sizes

    @property
    def styles(self):
        """list: Styles of the plots."""

        return self.__styles

    @styles.setter
    def styles(self, styles):
        self.__styles = styles

    @property
    def tick_labels(self):
        """list: Tick labels of the axis."""

        return self.__tick_labels

    @tick_labels.setter
    def tick_labels(self, tick_labels):
        self.__tick_labels = tick_labels

    @property
    def ticks(self):
        """list: Ticks of the axis."""

        return self.__ticks

    @ticks.setter
    def ticks(self, ticks):
        self.__ticks = ticks

    @property
    def unit(self):
        """str: Unit of the axis."""

        return self.__unit

    @unit.setter
    def unit(self, unit):
        self.__unit = unit

    @property
    def val(self):
        """list: Values of the axis."""

        return self.__val

    @val.setter
    def val(self, val):
        self.__val = val

    @property
    def var(self):
        """str: Variable of the axis."""

        return self.__var

    @var.setter
    def var(self, var):
        self.__var = var

    def __init__(self, params):
        """Class constructor for BaseAxis."""

        # frequently used variables
        _min = -1
        _max = 1
        _dim = 5
        
        # set val
        _val = params.get('val', list())
        if type(_val) is list and len(_val) > 0:
            self.val = _val
        else:
            # initizlize values
            self.val = self.init_array(params.get('min', _min), params.get('max', _max), params.get('dim', _dim))

        # reset range if not string
        if type(self.val[0]) is not str:
            _min = min(self.val)
            _max = max(self.val)

        # set dim
        self.dim = len(self.val)

        # set ticks
        _ticks = params.get('ticks', list())
        # if ticks are defined
        if type(_ticks) is list and len(_ticks) != 0:
            self.ticks = _ticks
            self.bound = 'both'
        # else initialize ticks
        else:
            self.ticks = self.init_array(params.get('tick_min', _min), params.get('tick_max', _max), params.get('tick_dim', _dim))
            self.bound = 'none'

        # set tick labels
        _tick_labels = params.get('tick_labels', [])
        # if ticks labels are defined
        if type(_tick_labels) is list and len(_tick_labels) != 0:
            self.tick_labels = _tick_labels
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
