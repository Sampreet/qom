#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface plotters."""

__name__    = 'qom.ui.plotters.BasePlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-06'
__updated__ = '2021-01-11'

# dependencies
from typing import Union
import logging
import numpy as np
import seaborn as sns

# qom modules
from ..axes import *

# module logger
logger = logging.getLogger(__name__)

# data types
t_axis = Union[DynamicAxis, MultiAxis, StaticAxis]

# TODO: Fix `get_limits`.

class BasePlotter():
    """Class to interface plotters.

    Initializes `axes` and `params` properties.
    
    Parameters
    ----------
    axes : dict
        Axes for the plot.
    params : dict
        Parameters of the plot.
    """

    # attributes
    types_1D = ['line', 'lines', 'scatter', 'scatters']
    types_2D = ['contour', 'contourf', 'pcolormesh']
    types_3D = ['surface', 'surface_cx', 'surface_cy', 'surface_cz']
    bins = 11
    cmaps = {
        'blr': sns.diverging_palette(250, 15, s=75, l=40, n=bins, center='light', as_cmap=True),
        'rlb': sns.diverging_palette(15, 250, s=75, l=40, n=bins, center='light', as_cmap=True),
        'glr': sns.diverging_palette(150, 15, s=75, l=40, n=bins, center='light', as_cmap=True)
    }

    @property
    def axes(self):
        """dict: Axes for the plot."""

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        self.__axes = axes

    @property
    def params(self):
        """dict: Parameters of the plot."""

        return self.__params
    
    @params.setter
    def params(self, params):
        self.__params = params

    def __init__(self, axes, params):
        """Class constructor for MPLPlotter."""

        # frequently used variables
        _type = params.get('type', 'line')
        _min = -1
        _max = 1

        # get parameters for axes
        _axes_params = dict()
        for axis in ['X', 'Y', 'Z', 'V']:
            _dim = 5
            # extract axis
            _axis = axes.get(axis, {
                'dim': _dim,
                'max': _max,
                'min': _min
            })

            # conver list to dict
            if type(_axis) is list:
                _axis = {
                    'val': _axis
                }
                
            # validate axis data
            _valid = True
            if type(_axis) is dict:
                for key in ['dim', 'max', 'min']:
                    if not key in _axis:
                        _valid = False
                        break
                _val = _axis.get('val', list())
                if len(_val) > 0:
                    _valid = True
            else:
                _valid = False
            assert _valid, 'Axis data should either be a `list` of values, or a `dict` containing `min`, `max` and `dim` keys or a single `val` key with a non-empty list.'

            # update dimension
            _dim = _axis.get('dim', None)
            if _dim is None:
                _dim = len(_axis['val'])
                
            # update parameters
            _axis['bound'] = params.get(axis.lower() + '_bound', 'none')
            _axis['colors'] = params.get(axis.lower() + '_colors', None)
            _axis['label'] = params.get(axis.lower() + '_label', '')
            _axis['name'] = params.get(axis.lower() + '_name', '')
            _axis['sizes'] = params.get(axis.lower() + '_sizes', None)
            _axis['styles'] = params.get(axis.lower() + '_styles', None)
            _axis['tick_labels'] = params.get(axis.lower() + '_tick_labels', None)
            _axis['ticks'] = params.get(axis.lower() + '_ticks', None)
            _axis['unit'] = params.get(axis.lower() + '_unit', '')
                
            # update axis
            _axes_params[axis] = _axis

        # set axes
        self.axes = {
            'X': StaticAxis(_axes_params['X']),
            'Y': MultiAxis(_axes_params['Y']) if _type in self.types_1D else StaticAxis(_axes_params['Y']),
            'Z': StaticAxis(_axes_params['Z']),
            'V': DynamicAxis(_axes_params['V'])
        }

        # set params
        self.params = {
            'type': _type,
            'title': params.get('title', ''),
            'cmap': self.cmaps.get(params.get('cmap', 'blr'), 'viridis'),
            'font_dicts': {
                'label': self.__get_font_dict(params, 'label'), 
                'tick': self.__get_font_dict(params, 'tick'),
                'math': params.get('font_math', 'cm')
            },
            'legend': {
                'show': params.get('show_legend', False),
                'location': params.get('legend_location', 'best')
            },
            'cbar': {
                'show': params.get('show_cbar', True),
                'title': params.get('cbar_title', ''),
                'x_label': params.get('cbar_x_label', ''),
                'y_label': params.get('cbar_y_label', ''),
                'ticks': params.get('cbar_ticks', None),
                'tick_labels': params.get('cbar_tick_labels', None),
            }
        }

    def __get_font_dict(self, params, text_type): 
        """Method to generate a dictionary of font properties for a given type of text.

        Parameters
        ----------
        params : dict
            Plot parameters passed.
        text_type : str
            Type of text:
                'label': for axes labels.
                'tick': for axes ticks.

        Returns
        -------
        font_dict : dict
            Dictionary of font properties.
        """

        # properties
        _family = params.get(text_type + '_font_family', 'Times New Roman')
        _style = params.get(text_type + '_font_style', 'normal')
        _variant = params.get(text_type + '_font_variant', 'normal')
        _weight = params.get(text_type + '_font_weight', 500)
        _stretch = params.get(text_type + '_font_stretch', 500)
        _size = 20.0 if text_type == 'label' else 16.0
        _size = params.get(text_type + '_font_size', _size)

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

    def get_limits(self, mini, maxi, res=3):
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