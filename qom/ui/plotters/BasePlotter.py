#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface plotters."""

__name__    = 'qom.ui.plotters.BasePlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-06'
__updated__ = '2021-08-19'

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

# TODO: Refine `get_colors`.
# TODO: Verify `get_limits`.

class BasePlotter():
    """Class to interface plotters.

    Initializes ``axes`` and ``params`` properties.
    
    Parameters
    ----------
    axes : dict
        Axes for the plot containing one or more keys for the axes ("X", "Y" or "Z"), each either a list of values, or dictionary containing "min", "max" and "dim" keys or a single "val" key with a non-empty list. Refer :class:`qom.ui.axes.BaseAxis` for currently supported keys.
    params : dict
        Parameters of the plot. Currently supported keys are:
            ======================  ====================================================
            key                     value
            ======================  ====================================================
            "bins"                  (*int*) number of colors for the plot.
            "cbar_position"         (*str*) position of the color bar. Currently supported values are "top", "right" (default), "bottom" and "left".
            "cbar_tick_labels"      (*list*) tick labels of the color bar.
            "cbar_ticks"            (*list*) ticks of the color bar.
            "cbar_title"            (*str*) title of the color bar.
            "cbar_x_label"          (*str*) X-axis label of the color bar.
            "cbar_y_label"          (*str*) Y-axis label of the color bar.
            "font_math"             (*str*) math renderer for fonts. 
            "height"                (*float*) height of the plot.
            "label_font_family"     (*str*) font family for the label.
            "label_font_size"       (*float*) font size for the label.
            "label_font_stretch"    (*int*) font stretch for the label.
            "label_font_style"      (*str*) font style for the label.
            "label_font_variant"    (*str*) font variant for the label.
            "label_font_weight"     (*int*) font weightt for the label.
            "legend_location"       (*bool*) location the legend. Currently supported locations are "best" (default), "center", "center left", "center right", "lower center", "lower left", "lower right", "right", "upper center", "upper left" and "upper right".
            "palette"               (*str*) color palette of the plot (refer attributes).
            "show_cbar"             (*bool*) option to show the color bar.
            "show_legend"           (*bool*) option to show the legend.
            "tick_font_family"      (*str*) font family for the tick.
            "tick_font_size"        (*float*) font size for the tick.
            "tick_font_stretch"     (*int*) font stretch for the tick.
            "tick_font_style"       (*str*) font style for the tick.
            "tick_font_variant"     (*str*) font variant for the tick.
            "tick_font_weight"      (*int*) font weightt for the tick.
            "title"                 (*str*) title of the plot.
            "type"                  (*str*) type of the plot (refer notes).
            "v_bound"               (*str*) option to check user-defined bounds.
            "v_label"               (*str*) label of the V-axis.
            "v_name"                (*str*) display name of the V-axis.
            "v_scale"               (*str*) scale of the V-axis.
            "v_sizes"               (*list*) sizes of the V-axis.
            "v_styles"              (*list*) styles of the V-axis.
            "v_tick_labels"         (*list*) tick labels of the V-axis.
            "v_ticks"               (*list*) ticks of the V-axis.
            "v_unit"                (*str*) unit of the V-axis.
            "width"                 (*float*) width of the plot.
            "x_bound"               (*str*) bounds of the X-axis.
            "x_label"               (*str*) label of the X-axis.
            "x_name"                (*str*) display name of the X-axis.
            "x_scale"               (*str*) scale of the X-axis.
            "x_sizes"               (*list*) sizes of the X-axis.
            "x_styles"              (*list*) styles of the X-axis.
            "x_tick_labels"         (*list*) tick labels of the X-axis.
            "x_ticks"               (*list*) ticks of the X-axis.
            "x_unit"                (*str*) unit of the X-axis.
            "y_bound"               (*str*) bounds of the Y-axis.
            "y_colors"              (*str*) colors for plots.
            "y_label"               (*str*) label of the Y-axis.
            "y_legend"              (*list*) legend of the plots.
            "y_name"                (*str*) display name of the Y-axis.
            "y_scale"               (*str*) scale of the Y-axis.
            "y_sizes"               (*list*) sizes of the Y-axis.
            "y_styles"              (*list*) styles of the Y-axis.
            "y_tick_labels"         (*list*) tick labels of the Y-axis.
            "y_ticks"               (*list*) ticks of the Y-axis.
            "y_unit"                (*str*) unit of the Y-axis.
            "z_bound"               (*str*) bounds of the Z-axis.
            "z_label"               (*str*) label of the Z-axis.
            "z_name"                (*str*) display name of the Z-axis.
            "z_scale"               (*str*) scale of the Z-axis.
            "z_sizes"               (*list*) sizes of the Z-axis.
            "z_styles"              (*list*) styles of the Z-axis.
            "z_tick_labels"         (*list*) tick labels of the Z-axis.
            "z_ticks"               (*list*) ticks of the Z-axis.
            "z_unit"                (*str*) unit of the Z-axis.
            ======================  ====================================================

    Notes
    -----
    Values for the keys with font paramters are currently backed by :class:`matplotlib`. Currently supported values of "\*_bounds" are "both", "lower", "none" (default) and "upper". Currently supported values of "\*_scale" are "linear" (default) and "log". Currently supported values of "type" are:
        ==============  ====================================================
        value           meaning
        ==============  ====================================================
        "contour"       contour plot.
        "contourf"      filled contour plot.
        "line"          single-line plot.
        "lines"         multi-line plot.
        "pcolormesh"    mesh color plot.
        "scatter"       single-scatter plot.
        "scatters"      multi-scatter plot.
        "surface"       surface plot.
        "surface_cx"    surface plot with projection on X-axis.
        "surface_cy"    surface plot with projection on Y-axis.
        "surface_cz"    surface plot with projection on Z-axis.
        ==============  ====================================================

    .. note:: All the options defined in ``params`` supersede individual function arguments.
    """

    # attributes
    types_1D = ['line', 'lines', 'scatter', 'scatters']
    types_2D = ['contour', 'contourf', 'pcolormesh']
    types_3D = ['surface', 'surface_cx', 'surface_cy', 'surface_cz']
    default_palettes = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'icefire', 'icefire_r', 'inferno', 'inferno_r', 'magma', 'magma_r', 'mako', 'mako_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 'rocket_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 'winter', 'winter_r']
    custom_palettes = {
        'blr': ['Blues_r', 'Reds'],
        'glr': ['Greens_r', 'Reds'],
        'rlb': ['Reds_r', 'Blues']
    }
    bins = 11

    def __init__(self, axes: dict, params: dict):
        """Class constructor for MPLPlotter."""

        # frequently used variables
        _type = params.get('type', 'line')
        _axes_params = self.__get_axes_params(axes, params)
        _palette = params.get('palette', 'RdBu_r')
        _bins = params.get('bins', self.bins)

        # se;ect axes
        self.axes = {
            'X': StaticAxis(_axes_params['X']),
            'Y': MultiAxis(_axes_params['Y']) if _type in self.types_1D else StaticAxis(_axes_params['Y']),
            'Z': StaticAxis(_axes_params['Z']),
            'V': DynamicAxis(_axes_params['V'])
        }

        # update bins
        self.bins = _bins

        # set params
        self.params = {
            'type': _type,
            'title': params.get('title', ''),
            'colors': self.get_colors(_palette, _bins),
            'palette': _palette,
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
                'position': params.get('cbar_position', 'right'),
                'x_label': params.get('cbar_x_label', ''),
                'y_label': params.get('cbar_y_label', ''),
                'ticks': params.get('cbar_ticks', None),
                'tick_labels': params.get('cbar_tick_labels', None),
            },
            'v_scale': params.get('v_scale', 'linear'),
            'x_scale': params.get('x_scale', 'linear'),
            'y_scale': params.get('y_scale', 'linear'),
            'z_scale': params.get('z_scale', 'linear'),
            'width': params.get('width', 5.0),
            'height': params.get('height', 5.0)
        }

    def __get_axes_params(self, axes: dict, params: dict):
        """Method to set parameters for the axes.

        Parameters
        ----------
        axes : dict
            Data for the axes.

        Returns
        -------
        axes_params : dict
            Parameters for the axes.
        """

        # frequently used variables
        _min = -1
        _max = 1

        # initialize
        axes_params = dict()

        # for each axis
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
            assert _valid, 'Axis data should either be a `list` of values, or a dictionary containing "min", "max" and `dim` keys or a single `val` key with a non-empty list.'

            # update dimension
            _dim = _axis.get('dim', None)
            if _dim is None:
                _dim = len(_axis['val'])
                
            # update parameters
            _axis['bound'] = params.get(axis.lower() + '_bound', 'none')
            _axis['colors'] = params.get(axis.lower() + '_colors', None)
            _axis['label'] = params.get(axis.lower() + '_label', '')
            _axis['legend'] = params.get(axis.lower() + '_legend', '')
            _axis['name'] = params.get(axis.lower() + '_name', '')
            _axis['sizes'] = params.get(axis.lower() + '_sizes', None)
            _axis['styles'] = params.get(axis.lower() + '_styles', None)
            _axis['tick_labels'] = params.get(axis.lower() + '_tick_labels', None)
            _axis['ticks'] = params.get(axis.lower() + '_ticks', None)
            _axis['unit'] = params.get(axis.lower() + '_unit', '')
                
            # update axis
            axes_params[axis] = _axis
        
        return axes_params

    def __get_font_dict(self, params: dict, text_type: str): 
        """Method to generate a dictionary of font properties for a given type of text.

        Parameters
        ----------
        params : dict
            Plot parameters passed.
        text_type : str
            Type of text:
                ==========  ====================================================
                value       meaning
                ==========  ====================================================
                "label"     properties for axes labels.
                "tick"      properties for axes ticks.
                ==========  ====================================================

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

    def get_colors(self, palette: str='RdBu', bins: int=11):
        """Method to obtain the colors in a color palette.

        Parameters
        ----------
        palette : str
            Default or diverging color palette.
        bins : int
            Number of bins.
        
        Returns
        -------
        colors : list
            Colors in the palette.
        """

        # default color palettes
        if not palette in self.custom_palettes:
            colors = sns.color_palette(palette, n_colors=bins, as_cmap=False)

        # custom color palettes
        else:
            # frequently used variables
            _palettes = self.custom_palettes[palette]
            _dim = len(_palettes)
            _bins = int(bins / _dim) + bins % _dim
            
            # list of colors
            colors = sns.color_palette(_palettes[0], n_colors=_bins, as_cmap=False)
            for i in range(1, _dim):
                colors += sns.color_palette(_palettes[i], n_colors=_bins, as_cmap=False)

        return colors

    def get_limits(self, mini: float, maxi: float, res: int=2):
        """Function to get limits from the minimum and maximum values of an array upto a certain resolution.

        Parameters
        ----------
        mini : float  
            Minimum value of the array.
        maxi : float  
            Maximum value of the array.
        res : int
            Resolution after the first significant digit in the decimal number system. Default is 2.

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


