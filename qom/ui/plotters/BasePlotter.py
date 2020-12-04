#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface plots."""

__name__    = 'qom.ui.plotters.BasePlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-06'
__updated__ = '2020-12-04'

# dependencies
import logging
import numpy as np
import seaborn as sns

# dev dependencies
from qom.ui.axes import *

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle legends.
# TODO: Fix get_limits.

class BasePlotter():
    """Class to interface plots.

    Initializes `plot_params` and `axes` properties.
    
    Parameters
    ----------
    plot_params : dict
        Parameters of the plot.
    Axes : dict
        Axes used for the plot as :class:`qom.utils.axis.StaticAxis`.
    """

    # attributes
    plot_types_1D = ['line', 'lines', 'scatter', 'scatters']
    plot_types_2D = ['contour', 'contourf', 'pcolormesh']
    plot_types_3D = ['surface', 'surface_cx', 'surface_cy', 'surface_cz']
    bins = 11
    cmaps = {
        'blr': sns.diverging_palette(250, 15, s=75, l=40, n=bins, center='light', as_cmap=True),
        'rlb': sns.diverging_palette(15, 250, s=75, l=40, n=bins, center='light', as_cmap=True),
        'glr': sns.diverging_palette(150, 15, s=75, l=40, n=bins, center='light', as_cmap=True)
    }

    @property
    def axes(self):
        """:class:`qom.ui.axes.*`: Axes for the figure."""

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        self.__axes = axes

    @property
    def plot_params(self):
        """dict: Parameters of the plot."""

        return self.__plot_params
    
    @plot_params.setter
    def plot_params(self, plot_params):
        self.__plot_params = plot_params

    def __init__(self, plot_params, Axes):
        """Class constructor for MPLPlotter."""

        # frequently used variables
        _type = plot_params.get('type', 'line')

        # set plot params
        self.plot_params = {
            'type': _type,
            'title': plot_params.get('title', ''),
            'cmap': self.cmaps.get(plot_params.get('cmap', 'blr'), 'viridis'),
            'font_dicts': {
                'label': self.__get_font_dict(plot_params, 'label'), 
                'tick': self.__get_font_dict(plot_params, 'tick'),
                'math': plot_params.get('font_math', 'cm')
            },
            'X': {
                'label': plot_params.get('x_label', ''),
                'ticks': plot_params.get('x_ticks', None),
                'tick_labels': plot_params.get('x_tick_labels', None)

            },
            'Y': {
                'label': plot_params.get('y_label', ''),
                'ticks': plot_params.get('y_ticks', None),
                'tick_labels': plot_params.get('y_tick_labels', None)

            },
            'Z': {
                'label': plot_params.get('z_label', ''),
                'ticks': plot_params.get('z_ticks', None),
                'tick_labels': plot_params.get('z_tick_labels', None)

            },
            'legend': {
                'show': plot_params.get('show_legend', False),
                'location': plot_params.get('legend_location', 'best')
            },
            'cbar': {
                'show': plot_params.get('show_cbar', True),
                'title': plot_params.get('cbar_title', ''),
                'x_label': plot_params.get('cbar_x_label', ''),
                'y_label': plot_params.get('cbar_y_label', ''),
                'ticks': plot_params.get('cbar_ticks', None),
                'tick_labels': plot_params.get('cbar_tick_labels', None),
            }
        }
        
        # list of supported axes
        _supported_axes = [DynamicAxis, MultiAxis, StaticAxis]

        # get X-axis
        _X = Axes.get('X', {})
        # handle NoneType
        if _X is None:
            _X = {}
        # if not in supported axis, convert to StaticAxis
        if type(_X) not in _supported_axes:
            _X = StaticAxis(_X)

        # get Y-axis
        _Y = Axes.get('Y', {})
        # handle NoneType
        if _Y is None:
            _Y = {}
        # if not in supported axis, convert to DynamicAxis if 1D plot, else StaticAxis
        if type(_Y) not in _supported_axes:
            _Y = DynamicAxis(_Y) if _type in self.plot_types_1D else StaticAxis(_Y)

        # get Z-axis
        _Z = Axes.get('Z', {})
        # handle NoneType
        if _Z is None:
            _Z = {}
        # if not in supported axis, convert to MultiAxis if 1D plot, else DynamicAxis
        if type(_Z) not in _supported_axes:
            _Z = MultiAxis(_Z) if _type in self.plot_types_1D else DynamicAxis(_Z)

        # set axes
        self.axes = {
            'X': _X,
            'Y': _Y,
            'Z': _Z
        }

        # supersede plot_params over axis data
        for axis in ['X', 'Y', 'Z']:
            # set axis label
            _label = self.plot_params[axis]['label']
            if _label != '':
                self.axes[axis].label = _label
            # set ticks and tick labels
            _ticks = self.plot_params[axis]['ticks']
            if _ticks is not None:
                self.axes[axis].ticks = _ticks
                self.axes[axis].bound = 'both'
                self.axes[axis].tick_labels = _ticks
            # update tick labels
            _tick_labels = self.plot_params[axis]['tick_labels']
            if _tick_labels is not None:
                self.axes[axis].tick_labels = _tick_labels

    def __get_font_dict(self, plot_params, text_type): 
        """Method to generate a dictionary of font properties for a given type of text.

        Parameters
        ----------
        plot_params : dict
            Plot parameters passed.
        text_type : str
            Type of text:
                * 'label' : for axes labels.
                * 'tick' : for axes ticks.

        Returns
        -------
        font_dict : dict
            Dictionary of font properties.
        """

        # properties
        _family = plot_params.get(text_type + '_font_family', 'Times New Roman')
        _style = plot_params.get(text_type + '_font_style', 'normal')
        _variant = plot_params.get(text_type + '_font_variant', 'normal')
        _weight = plot_params.get(text_type + '_font_weight', 500)
        _stretch = plot_params.get(text_type + '_font_stretch', 500)
        _size = 20.0 if text_type == 'label' else 16.0
        _size = plot_params.get(text_type + '_font_size', _size)

        # font dictionary
        _font_dict = {
            'family': _family,
            'style': _style,
            'variant': _variant,
            'weight': _weight,
            'stretch': _stretch,
            'size': _size
        }

        # return
        return _font_dict

    def get_limits(self, mini, maxi, res=2):
        """Function to get limits from the minimum and maximum values of an array upto a certain resolution.

        Parameters
        ----------
        mini : list  
            Minimum value of the array.
        maxi : list  
            Maximum value of the array.
        res : int
            Resolution after the first significant digit in the decimal number system.

        Returns
        -------
        mini : float
            Formatted minimum value.
        maxi : float
            Formatted maximum value.
        prec : int
            Precision of rounding off.
        """

        # get minimum maximum
        _mini = mini
        _maxi = maxi
        _mult_min = 10**res
        _mult_max = 10**res

        # handle negative values
        if _mini < 0:
            _mini *= - 1
        if _maxi < 0:
            _maxi *= - 1

        # update multiplier
        if _mini != 0 :
            _mult_min = 10**(np.ceil(-np.log10(_mini)) + res - 1)
        if _maxi != 0:
            _mult_max = 10**(np.ceil(-np.log10(_maxi)) + res - 1)
        _mult = min(10**res, min(_mult_min, _mult_max))

        # round off
        _mini = np.floor(mini * _mult) / _mult
        _maxi = np.ceil(maxi * _mult) / _mult
        _prec = int(np.round(np.log10(_mult)))

        # return
        return _mini, _maxi, _prec