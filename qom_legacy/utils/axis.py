#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module for axis utilities."""

__name__    = 'qom_legacy.utils.axis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2020-10-21'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle index-based initialization.

class DynamicAxis():
    """Utility class to create a dynamic axis.

    Properties
    ----------
        size : int
            Length of the reference axis.

        values : list 
            Values of the variable.
    """

    def __init__(self, size=None):
        """Class constructor for DynamicAxis.

        Parameters
        ----------
            size : int 
                Dimensions of the reference axis.
        """

        if size is not None:
            self.size = size
        if len(size) == 1:
            self.values = []
        if len(size) == 2:
            self.values = [[] for _ in range(size[0])]

    @property
    def size(self):
        """Property size.

        Returns
        -------
            size : int
                Length of the reference axis.
        """

        return self.__size

    @size.setter
    def size(self, size):
        """Setter for size.

        Parameters
        ----------
            size : int
                Dimensions of the reference axis.
        """

        self.__size = size    

    @property
    def values(self):
        """Property values.

        Returns
        -------
            values : list
                Values of the axis.
        """

        return self.__values

    @values.setter
    def values(self, values):
        """Setter for values.

        Parameters
        ----------
            values : list
                Values of the axis.
        """

        self.__values = values

class StaticAxis():
    """Utility class to format corrdinates from dictionary.

    Properties
    ----------
        var : str
            Variable of the axis.

        label : list
            Label of the axis.

        unit : list
            Display unit of the axis.

        values : list
            Values of the variable.

        ticks : list
            Values of the axis ticks.

        colors : list 
            Colors for line plots.

        legends : list 
            Legends for the values.

        linestyles : list
            Linestyles of the line plots.

        sizes : list
            Sizes of the scatter plots.
    """

    @property
    def var(self):
        """Property var.

        Returns
        -------
            var : str
                Variable of the axis.
        """

        return self.__var

    @var.setter
    def var(self, var):
        """Setter for var.

        Parameters
        ----------
            var : str
                Variable of the axis.
        """

        self.__var = var

    @property
    def index(self):
        """Property index.

        Returns
        -------
            index : str
                Index of the variable.
        """

        return self.__index

    @index.setter
    def index(self, index):
        """Setter for index.

        Parameters
        ----------
            index : str
                Index of the variable.
        """

        self.__index = index

    @property
    def label(self):
        """Property label.

        Returns
        -------
            label : str
                Label of the axis.
        """

        return self.__label

    @label.setter
    def label(self, label):
        """Setter for label.

        Parameters
        ----------
            label : str
                Label of the axis.
        """

        if label == '':
            self.__label = self.__var
            return

        self.__label = label

    @property
    def unit(self):
        """Property unit.

        Returns
        -------
            unit : str
                Unit of the axis.
        """

        return self.__unit

    @unit.setter
    def unit(self, unit):
        """Setter for unit.

        Parameters
        ----------
            unit : str
                Unit of the axis.
        """

        self.__unit = unit

    @property
    def values(self):
        """Property values.

        Returns
        -------
            values : list
                Values of the axis.
        """

        return self.__values

    @values.setter
    def values(self, values):
        """Setter for values.

        Parameters
        ----------
            values : list
                Values of the axis.
        """

        self.__values = values

    @property
    def ticks(self):
        """Property ticks.

        Returns
        -------
            ticks : list
                Ticks of the axis.
        """

        return self.__ticks

    @ticks.setter
    def ticks(self, ticks):
        """Setter for ticks.

        Parameters
            ticks : list
                Ticks of the axis.
        """

        self.__ticks = ticks

    @property
    def tick_labels(self):
        """Property tick labels.

        Returns
        -------
            ticks : list
                Tick labels of the axis.
        """

        return self.__tick_labels

    @tick_labels.setter
    def tick_labels(self, tick_labels):
        """Setter for tick labels.

        Parameters
            tick_labels : list
                Tick labels of the axis.
        """

        self.__tick_labels = tick_labels

    @property
    def colors(self):
        """Property colors.

        Returns
        -------
            colors : list
                Colors of the axis.
        """

        return self.__colors

    @colors.setter
    def colors(self, colors):
        """Setter for colors.

        Parameters
        ----------
            colors : list
                Colors of the axis.
        """

        if type(colors) is not list or len(colors) == 0:
            self.__colors = ['r' for i in range(len(self.__values))]
            return

        self.__colors = colors

    @property
    def legends(self):
        """Property legends.

        Returns
        -------
            legends : list 
                Legends of the axis.
        """

        return ['{label} = {value} {unit}'.format(label=self.__label, value=value, unit=self.__unit) for value in self.__values]

    @property
    def linestyles(self):
        """Property linestyles.

        Returns
        -------
            linestyles : list
                Linestyles of the line plots.
        """

        return self.__linestyles

    @linestyles.setter
    def linestyles(self, linestyles):
        """Setter for linestyles.

        Parameters
        ----------
            linestyles : list
                Linestyles of the line plots.
        """

        if type(linestyles) is not list or len(linestyles) == 0:
            self.__linestyles = ['-' for i in range(len(self.__values))]
            return

        self.__linestyles = linestyles

    @property
    def sizes(self):
        """Property sizes.

        Returns
        -------
            sizes : list
                Sizes of the scatter plots.
        """

        return self.__sizes

    @sizes.setter
    def sizes(self, sizes):
        """Setter for sizes.

        Parameters
        ----------
            sizes : list
                Sizes of the scatter plots.
        """

        if type(sizes) is not list or len(sizes) == 0:
            self.__sizes = [2 for i in range(len(self.__values))]
            return

        self.__sizes = sizes

    def __init__(self, axis_data):
        """Class constructor for StaticAxis.

        Parameters
        ----------
            axis_data : dict
                Dictionary of the data for the axis.
        """

        # variable
        self.var = axis_data['var']
        # index
        self.index = axis_data.get('index', None)
        # label
        self.label = axis_data.get('label', self.__var)
        # unit
        self.unit = axis_data.get('unit', '')
        # values
        _values = axis_data.get('values', None)
        if _values is not None and len(_values) != 0:
            self.values = _values
        else: 
            self.values = self.init_array(axis_data.get('min', 0), axis_data.get('max', 1), axis_data.get('steps', 5))
        # ticks
        _tick_labels = axis_data.get('tick_labels', None)
        if _tick_labels is not None:
            self.ticks = self.init_array(self.__values[0], self.__values[-1], len(_tick_labels))
            self.tick_labels = _tick_labels
        else:
            self.ticks = self.init_array(self.__values[0], self.__values[-1], axis_data.get('tick_steps', 5))
            self.tick_labels = self.__ticks 
        # colors
        self.colors = axis_data.get('colors', [])
        # linestyles
        self.linestyles = axis_data.get('linestyles', [])
        # sizes
        self.sizes = axis_data.get('sizes', [])

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

        