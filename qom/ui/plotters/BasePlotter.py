#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface plots."""

__name__    = 'qom.ui.plotters.BasePlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-06'
__updated__ = '2020-11-17'

# dependencies
import logging
import numpy as np
import seaborn as sns

# dev dependencies
from qom.ui.axes import *

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle legends.

class BasePlotter():
    """Class to interface plots.

    Attributes
    ----------
        plot_types_1D : list
            List of supported 1D plots:
                'line' : Line plot.
                'lines' : Multi-line plot.
                'scatter' : Scatter plot.
                'scatters' : Multi-scatter plot

        plot_types_2D : list
            List of supported 2D plots:
                'pcolormesh' : Color plot.
        
        plot_types_3D : list
            List of supported 3D plots:
                'surface' : Surface plot.

        cmaps : dict 
            Dictionary of supported maps for 2D and 3D color plots.

    Properties
    ----------
        axes : :class:`qom.ui.axes.*`
            Axes for the figure.

        plot_params : dict
            Parameters of the plot.
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
        """Property axes.

        Returns
        -------
            axes : :class:`qom.ui.axes.*`
                Axes for the figure.
        """

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        """Setter for axes.

        Parameters
        ----------
            axes : :class:`qom.ui.axes.*`
                Axes for the figure.
        """

        self.__axes = axes

    @property
    def plot_params(self):
        """Property plot_params.

        Returns
        -------
            plot_params : dict
                Parameters of the plot.
        """

        return self.__plot_params
    
    @plot_params.setter
    def plot_params(self, plot_params):
        """Setter for plot_params.

        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.
        """

        self.__plot_params = plot_params

    def __init__(self, plot_params, Axes):
        """Class constructor for MPLPlotter.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            Axes : dict
                Axes used for the plot as :class:`qom.utils.axis.StaticAxis`.
        """

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
                'show': plot_params.get('show_legend', False)
            },
            'cbar': {
                'show': plot_params.get('show_cbar', True),
                'title': plot_params.get('cbar_title', ''),
                'label': plot_params.get('cbar_label', ''),
                'ticks': plot_params.get('cbar_ticks', None),
                'tick_labels': plot_params.get('cbar_tick_labels', None)
            }
        }
        
        # convert axes if supported
        _supported_axes = [list, dict, DynamicAxis, MultiAxis, StaticAxis]
        # X-axis
        _X = Axes.get('X', StaticAxis())
        assert type(_X) in _supported_axes or _X is None, 'Axes should either be lists, dicts or qom.ui.axes.* or None'
        if _X is None:
            _X = {}
        elif type(_X) is list:
            _X = {'val': _X}
        if type(_X) is dict:
            _X = StaticAxis(_X)
        # y-axis
        _Y = Axes.get('Y', DynamicAxis() if _type in self.plot_types_1D else StaticAxis())
        assert type(_Y) in _supported_axes or _Y is None, 'Axes should either be lists, dicts or qom.ui.axes.* or None'
        if _Y is None:
            _Y = {}
        elif type(_Y) is list:
            _Y = {'val': _Y}
        if type(_Y) is dict:
            _Y = DynamicAxis({'val': _Y}) if _type in self.plot_types_1D else StaticAxis({'val': _Y})
        # z-axis
        _Z = Axes.get('Z', MultiAxis() if _type in self.plot_types_1D else DynamicAxis())
        assert type(_Z) in _supported_axes or _Z is None, 'Axes should either be lists, dicts or qom.ui.axes.* or None'
        if _Z is None:
            _Z = {}
        elif type(_Z) is list:
            _Z = {'val': _Z}
        if type(_Z) is dict:
            _Z = MultiAxis({'val': _Z}) if _type in self.plot_types_1D else DynamicAxis({'val': _Z})

        # set axes
        self.axes = {
            'X': _X,
            'Y': _Y,
            'Z': _Z
        }

        # supersede plot_params over axis ticks
        for axis in ['X', 'Y', 'Z']:
            _label = self.plot_params[axis]['label']
            if _label != '':
                self.axes[axis].label = _label
            _ticks = self.plot_params[axis]['ticks']
            if _ticks is not None:
                self.axes[axis].ticks = _ticks
                self.axes[axis].bound = 'both'
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
                    label : for axes labels.
                    tick : for axes ticks.

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
        _size = 16.0 if text_type == 'label' else 12.0
        _size = plot_params.get(text_type + '_font_size', _size)

        _font_dict = {
            'family': _family,
            'style': _style,
            'variant': _variant,
            'weight': _weight,
            'stretch': _stretch,
            'size': _size
        }

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

        return _mini, _maxi, _prec