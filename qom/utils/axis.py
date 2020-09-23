#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for axis utilities."""

__name__    = 'qom.utils.axis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2020-09-23'

# dependencies
import logging
import numpy as np

# dev dependencies
from qom.ui import figure

# module logger
logger = logging.getLogger(__name__)

class DynamicAxis(object):
    """Utility class to create a dynamic axis.

    Inherits :class:`object` for 2.x compatibility.

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

        if size != None:
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

class StaticAxis(object):
    """Utility class to format corrdinates from dictionary.

    Inherits :class:`object` for 2.x compatibility.

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

        legends : list 
            Legends for the values.

        colors : list 
            Colors for line plots.

        linestyles : list
            Linestyles for line plots.
    """

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
        if 'index' in axis_data: 
            self.index = axis_data['index']
        # label
        if 'label' in axis_data:
            self.label = axis_data['label']
        # unit
        if 'unit' in axis_data:
            self.unit = axis_data['unit']
        # values
        if 'values' in axis_data and len(axis_data['values']) != 0:
            self.values = axis_data['values']
        else: 
            self.values = self.init_array(axis_data['min'], axis_data['max'], axis_data['steps'])
        # ticks
        if 'ticks' in axis_data:
            _num = axis_data['ticks']
        else:
            _num = 5
        self.ticks = self.init_array(axis_data['min'], axis_data['max'], _num)
        # colors
        if 'colors' in axis_data:
            self.colors = axis_data['colors']
        # linestyles
        if 'linestyles' in axis_data:
            self.linestyles = axis_data['linestyles']
        # sizes
        if 'sizes' in axis_data:
            self.sizes = axis_data['sizes']

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

        if self.__label == None:
            return r'$' + self.__var + '$'

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
            self.__label = r'$' + self.__var + '$'
            return

        self.__label = r'' + label + ''

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

        if unit == '':
            self.__unit = ''
            return

        self.__unit = '~\\mathrm{' + unit + '}'

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
    def colors(self):
        """Property colors.

        Returns
        -------
            colors : list
                Colors of the axis.
        """

        if not self.__colors:
            self.__colors = ['b' for i in range(len(self.__values))]

        return self.__colors

    @colors.setter
    def colors(self, colors):
        """Setter for colors.

        Parameters
        ----------
            colors : list
                Colors of the axis.
        """

        self.__colors = colors

    @property
    def linestyles(self):
        """Property linestyles.

        Returns
        -------
            linestyles : list
                Linestyles of the line plots.
        """

        if not self.__linestyles:
            self.__linestyles = ['-' for i in range(len(self.__values))]

        return self.__linestyles

    @linestyles.setter
    def linestyles(self, linestyles):
        """Setter for linestyles.

        Parameters
        ----------
            linestyles : list
                Linestyles of the line plots.
        """

        self.__linestyles = linestyles

    @property
    def sizes(self):
        """Property sizes.

        Returns
        -------
            sizes : list
                Sizes of the scatter plots.
        """

        if not self.__sizes:
            self.__sizes = [100 for i in range(len(self.__values))]

        return self.__sizes

    @sizes.setter
    def sizes(self, sizes):
        """Setter for sizes.

        Parameters
        ----------
            sizes : list
                Sizes of the scatter plots.
        """

        self.__sizes = sizes

    @property
    def legends(self):
        """Property legends.

        Returns
        -------
            legends : list 
                Legends of the axis.
        """

        return [r'$' + '{label} = {value} {unit}'.format(label=self.__label, value=value, unit=self.__unit) + '$' for value in self.__values]

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

        