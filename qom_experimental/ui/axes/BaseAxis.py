#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface axes."""

__name__    = 'qom_experimental.ui.axes.BaseAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2020-10-19'

# dependencies
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

class BaseAxis():
    """Class to interface axes.

    Inherited objects need to set the properties `var`, `name`, `unit`, `label` and `legends` individually.

    Properties
    ----------
        var : str
            Variable of the axis.

        val : list
            Values of the variable.
        
        dim : int
            Dimension of the axis.

        name : str
            Display name of the axis.

        unit : list
            Display unit of the axis.

        ticks : list
            Values of the axis ticks.

        tick_labels : list
            Labels of the axis ticks.

        label : str
            Label of the axis.

        legends : list 
            Legends for the values.

        colors : list 
            Colors for plots.

        styles : list
            Styles of the plots.

        sizes : list
            Sizes of the plots.
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
    def val(self):
        """Property val.

        Returns
        -------
            val : list
                Values of the axis.
        """

        return self.__val

    @val.setter
    def val(self, val):
        """Setter for val.

        Parameters
        ----------
            val : list
                Values of the axis.
        """

        self.__val = val

    @property
    def dim(self):
        """Property dim.

        Returns
        -------
            dim : int
                Dimension of the axis.
        """

        return self.__dim

    @dim.setter
    def dim(self, dim):
        """Setter for dim.

        Parameters
        ----------
            dim : int
                Dimension of the axis.
        """

        self.__dim = dim

    @property
    def name(self):
        """Property name.

        Returns
        -------
            name : str
                Display name of the axis.
        """

        return self.__name

    @name.setter
    def name(self, name):
        """Setter for name.

        Parameters
        ----------
            name : str
                Display name of the axis.
        """

        self.__name = name

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
        """Property tick_labels.

        Returns
        -------
            ticks : list
                Tick labels of the axis.
        """

        return self.__tick_labels

    @tick_labels.setter
    def tick_labels(self, tick_labels):
        """Setter for tick_labels.

        Parameters
            tick_labels : list
                Tick labels of the axis.
        """

        self.__tick_labels = tick_labels

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

        self.__label = label

    @property
    def legends(self):
        """Property legends.

        Returns
        -------
            legends : list 
                Legends of the axis.
        """

        return self.__legends

    @legends.setter
    def legends(self, legends):
        """Setter for legends.

        Parameters
        ----------
            legends : list 
                Legends of the axis.
        """

        self.__legends = legends

    @property
    def colors(self):
        """Property colors.

        Returns
        -------
            colors : list
                Colors for plots.
        """

        return self.__colors

    @colors.setter
    def colors(self, colors):
        """Setter for colors.

        Parameters
        ----------
            colors : list
                Colors for plots.
        """

        self.__colors = colors

    @property
    def styles(self):
        """Property styles.

        Returns
        -------
            styles : list
                Styles of the plots.
        """

        return self.__styles

    @styles.setter
    def styles(self, styles):
        """Setter for styles.

        Parameters
        ----------
            styles : list
                Styles of the plots.
        """

        self.__styles = styles

    @property
    def sizes(self):
        """Property sizes.

        Returns
        -------
            sizes : list
                Sizes of the plots.
        """

        return self.__sizes

    @sizes.setter
    def sizes(self, sizes):
        """Setter for sizes.

        Parameters
        ----------
            sizes : list
                Sizes of the plots.
        """

        self.__sizes = sizes

    def __init__(self, axis_data):
        """Class constructor for BaseAxis.

        Parameters
        ----------
            axis_data : int or list or dict
                Data for the axis.
        """

        # if dimension
        if type(axis_data) is int:
            axis_data = {
                'dim': axis_data
            }

        # if values
        elif type(axis_data) is list:
            axis_data = {
                'val': axis_data
            }

        # validate parameter
        assert type(axis_data) is dict, "Axis data is not a dictionary."

        # frequently used variables
        _min = -1
        _max = 1
        _dim = 5
        
        # set val
        _val = axis_data.get('val', [])
        if type(_val) is list and len(_val) != 0:
            self.val = _val
        else:
            self.val = self.init_array(axis_data.get('min', _min), axis_data.get('max', _max), axis_data.get('dim', _dim))

        # set dim
        self.dim = len(self.val)

        # validate parameter
        assert type(axis_data) is dict

        # set ticks
        _ticks = axis_data.get('ticks', [])
        if type(_ticks) is list and len(_ticks) != 0:
            self.ticks = _ticks
        else:
            self.ticks = self.init_array(axis_data.get('tick_min', self.val[0]), axis_data.get('tick_max', self.val[-1]), axis_data.get('tick_dim', self.dim))

        # set tick labels
        _tick_labels = axis_data.get('tick_labels', [])
        if type(_tick_labels) is list and len(_tick_labels) != 0:
            self.tick_labels = _tick_labels
        else:
            self.tick_labels = self.ticks 

        # supersede tick labels over ticks
        if len(self.tick_labels) != len(self.ticks):
            self.ticks = self.init_array(axis_data.get('tick_min', self.val[0]), axis_data.get('tick_max', self.val[-1]), len(self.tick_labels))

        # set colors
        _colors = axis_data.get('colors', [])
        if type(_colors) is list or len(_colors) != 0:
            self.colors = _colors
        else:
            self.colors = ['r' for i in range(len(self.val))]
            return

        # set styles
        _styles = axis_data.get('styles', [])
        if type(_styles) is list or len(_styles) != 0:
            self.styles = _styles
        else:
            self.styles = ['-' for i in range(len(self.val))]
            return

        # set sizes
        _sizes = axis_data.get('sizes', [])
        if type(_sizes) is list or len(_sizes) != 0:
            self.sizes = _sizes
        else:
            self.sizes = ['-' for i in range(len(self.val))]
            return

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
