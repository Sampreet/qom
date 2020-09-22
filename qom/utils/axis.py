#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for axis utilities."""

__name__    = 'qom.utils.axis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-17'
__updated__ = '2020-09-17'

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

    Properties:
        size (int): Length of the reference axis.
        values (list): Values of the variable.
    """

    def __init__(self, size=None):
        """Class constructor for DynamicAxis.

        Args:
            num (int): Length of the reference axis.
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

        Returns:
            int: Length of the reference axis.
        """

        return self.__size

    @size.setter
    def size(self, value):
        """Setter function for size.

        Args:
            value (int): Length of the reference axis.
        """

        self.__size = value    

    @property
    def values(self):
        """Property values.

        Returns:
            list: Values of the axis.
        """

        return self.__values

    @values.setter
    def values(self, value):
        """Setter function for values.

        Args:
            value (list): Values of the axis.
        """

        self.__values = value

class StaticAxis(object):
    """Utility class to format corrdinates from dictionary.

    Inherits :class:`object` for 2.x compatibility.

    Properties:
        var (str): Variable of the axis.
        label (str): Label of the axis.
        unit (str): Display unit of the axis.
        values (list): Values of the variable.
        ticks (list): Values of the axis ticks.
        legends (list): Legends for the values.
        colors (list): Colors for line plots.
        linestyles (list): Linestyles for line plots.
    """

    def __init__(self, axis_data):
        """Class constructor for StaticAxis.

        Args:
            axis_data (dict): Dictionary of the data for the axis.
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

    @property
    def var(self):
        """Property variable.

        Returns:
            str: Variable of the axis.
        """

        return self.__var

    @var.setter
    def var(self, value):
        """Setter function for variable.

        Args:
            value (str): Variable of the axis.
        """

        self.__var = value

    @property
    def index(self):
        """Property index.

        Returns:
            str: Index of the variable.
        """

        return self.__index

    @index.setter
    def index(self, value):
        """Setter function for index.

        Args:
            str: Index of the variable.
        """

        self.__index = value

    @property
    def label(self):
        """Property label.

        Returns:
            str: Label of the axis.
        """

        if self.__label == None:
            return r'$' + self.__var + '$'

        return self.__label

    @label.setter
    def label(self, value):
        """Setter function for label.

        Args:
            value (str): Label of the axis.
        """

        if value == '':
            self.__label = r'$' + self.__var + '$'
            return

        self.__label = r'' + value + ''

    @property
    def unit(self):
        """Property unit.

        Returns:
            str: Unit of the axis.
        """

        return self.__unit

    @unit.setter
    def unit(self, value):
        """Setter function for unit.

        Args:
            value (str): Unit of the axis.
        """
        if value == '':
            self.__unit = value
            return
        self.__unit = '~\\mathrm{' + value + '}'

    @property
    def values(self):
        """Property values.

        Returns:
            list: Values of the axis.
        """

        return self.__values

    @values.setter
    def values(self, value):
        """Setter function for values.

        Args:
            value (list): Values of the axis.
        """

        self.__values = value

    @property
    def ticks(self):
        """Property ticks.

        Returns:
            list: Ticks of the axis.
        """

        return self.__ticks

    @ticks.setter
    def ticks(self, value):
        """Setter function for ticks.

        Args:
            value (list): Ticks of the axis.
        """

        self.__ticks = value

    @property
    def legends(self):
        """Property legends.

        Returns:
            list: Legends of the axis.
        """

        return [r'$' + '{label} = {value} {unit}'.format(label=self.__label, value=value, unit=self.__unit) + '$' for value in self.__values]

    @property
    def colors(self):
        """Property colors.

        Returns:
            list: Colors of the axis.
        """

        return self.__colors

    @colors.setter
    def colors(self, value):
        """Setter function for colors.

        Args:
            value (list): Colors of the axis.
        """

        self.__colors = value

    @property
    def linestyles(self):
        """Property linestyles.

        Returns:
            list: Linestyles of the axis.
        """

        return self.__linestyles

    @linestyles.setter
    def linestyles(self, value):
        """Setter function for linestyles.

        Args:
            value (list): Linestyles of the axis.
        """

        self.__linestyles = value

    def init_array(self, mini, maxi, num):
        """Function to initialize an array given a range and number of elements.

        Args:
            mini (int): Minimum value of the range.
            maxi (int): Maximum value of the range.
            num (int): Number of elements to consider.
        """
    
        values = (mini + np.arange(num) * (maxi - mini) / (num - 1))

        return values.tolist()

        