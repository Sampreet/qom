#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface plotters."""

__name__    = 'qom.ui.plotters.BasePlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-06'
__updated__ = '2022-11-08'

# dependencies
import logging
import numpy as np
import seaborn as sns

# qom modules
from ..axes import *

# module logger
logger = logging.getLogger(__name__)

# TODO: Validate parameters.
# TODO: Verify `get_limits`.

class BasePlotter():
    """Class to interface plotters.

    Initializes ``axes``, ``bins`` and ``params`` properties.
    
    Parameters
    ----------
    axes : dict
        Axes for the plot containing one or more keys for the axes ("X", "Y" or "Z"), each either a list of values, or dictionary containing "min", "max" and "dim" keys or a single "val" key with a non-empty list. Refer :class:`qom.ui.axes.BaseAxis` for currently supported keys.
    params : dict
        Parameters of the plot. Currently supported keys are:
            ======================  ====================================================
            key                     value
            ======================  ====================================================
            "annotations"           (*list*) annotation dictionaries for the plot containing keys "s" for the text, "xy" for the tuple of positions of the text on the figure in fractions, "color" for the color of the text, and "font_dict" for the type of font dictionary to copy. Options are "label" or "tick".
            "bins"                  (*int*) number of colors for the plot.
            "cbar_position"         (*str*) position of the color bar. Options are are "top", "right" (default), "bottom" and "left".
            "cbar_tick_labels"      (*list*) tick labels of the color bar.
            "cbar_ticks"            (*list*) ticks of the color bar.
            "cbar_title"            (*str*) title of the color bar.
            "cbar_x_label"          (*str*) X-axis label of the color bar.
            "cbar_y_label"          (*str*) Y-axis label of the color bar.
            "component"             (*str*) component of complex value. Options are "real" or "imag".
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
            "v_label"               (*str*) label of the V-axis.
            "v_label_pad"           (*int*) label padding of the V-axis.
            "v_name"                (*str*) display name of the V-axis.
            "v_scale"               (*str*) scale of the V-axis. Options are "linear" and "log".
            "v_tick_dim"            (*int*) tick dimension of the V-axis.
            "v_tick_labels"         (*list*) tick labels of the V-axis.
            "v_tick_pad"            (*int*) tick padding of the V-axis.
            "v_tick_position"       (*str*) tick position of the V-axis. Options are "both" (default), "bottom", "left", "right" or "top".
            "v_ticks"               (*list*) ticks of the V-axis.
            "v_ticks_minor"         (*list*) positions of minor ticks of the V-axis.
            "v_unit"                (*str*) unit of the V-axis.
            "view_aspect"           (*list*) aspect ratios of the 3D axes.
            "view_elevation"        (*float*) elevation for 3D view on Z-axis.
            "view_rotation"         (*float*) rotation for 3D view about Z-axis.
            "vspan"                 (*list*) vertical background spanning dictionaries for the plot containing keys "xmin" for the minimum X-axis value, "xmax" for the maximum X-axis value, "color_idx" for the index of the color, and "alpha" for opacity value.
            "width"                 (*float*) width of the plot.
            "x_label"               (*str*) label of the X-axis.
            "x_label_pad"           (*int*) label padding of the X-axis.
            "x_name"                (*str*) display name of the X-axis.
            "x_scale"               (*str*) scale of the X-axis. Options are "linear" and "log".
            "x_tick_dim"            (*int*) tick dimension of the X-axis.
            "x_tick_labels"         (*list*) tick labels of the X-axis.
            "x_tick_pad"            (*int*) tick padding of the X-axis.
            "x_tick_position"       (*str*) tick position of the X-axis. Options are "both" (default), "bottom", "left", "right" or "top".
            "x_ticks"               (*list*) ticks of the X-axis.
            "x_ticks_minor"         (*list*) positions of minor ticks of the X-axis.
            "x_unit"                (*str*) unit of the X-axis.
            "y_colors"              (*str*) colors for plots.
            "y_label"               (*str*) label of the Y-axis.
            "y_label_pad"           (*int*) label padding of the Y-axis.
            "y_legend"              (*list*) legend of the plots.
            "y_name"                (*str*) display name of the Y-axis.
            "y_scale"               (*str*) scale of the Y-axis. Options are "linear" and "log".
            "y_sizes"               (*list*) sizes of the Y-axis.
            "y_styles"              (*list*) styles of the Y-axis.
            "y_tick_dim"            (*int*) tick dimension of the Y-axis.
            "y_tick_labels"         (*list*) tick labels of the Y-axis.
            "y_tick_pad"            (*int*) tick padding of the Y-axis.
            "y_tick_position"       (*str*) tick position of the Y-axis. Options are "both" (default), "bottom", "left", "right" or "top".
            "y_ticks"               (*list*) ticks of the Y-axis.
            "y_ticks_minor"         (*list*) positions of minor ticks of the Y-axis.
            "y_unit"                (*str*) unit of the Y-axis.
            "z_label"               (*str*) label of the Z-axis.
            "z_label_pad"           (*int*) label padding of the Z-axis.
            "z_name"                (*str*) display name of the Z-axis.
            "z_scale"               (*str*) scale of the Z-axis. Options are "linear" and "log".
            "z_tick_dim"            (*int*) tick dimension of the Z-axis.
            "z_tick_labels"         (*list*) tick labels of the Z-axis.
            "z_tick_pad"            (*int*) tick padding of the Z-axis.
            "z_tick_position"       (*str*) tick position of the Z-axis. Options are "both" (default), "bottom", "left", "right" or "top".
            "z_ticks"               (*list*) ticks of the Z-axis.
            "z_ticks_minor"         (*list*) positions of minor ticks of the Z-axis.
            "z_unit"                (*str*) unit of the Z-axis.
            ======================  ====================================================

    Notes
    -----
    Values for the keys with font paramters are currently backed by :class:`matplotlib`. Currently supported values of "\*_bound" are "both", "lower", "none" (default) and "upper". Currently supported values of "\*_scale" are "linear" (default) and "log". Currently supported values of "type" are:
        ==================  ====================================================
        value               meaning
        ==================  ====================================================
        "contour"           contour plot.
        "contourf"          filled contour plot.
        "density"           density plot.
        "density_unit"      density plot with unit sphere.
        "line"              single-line plot.
        "line_3d"           single-line plot in 3D.
        "lines"             multi-line plot.
        "lines_3d"          multi-line plot in 3D.
        "pcolormesh"        mesh color plot.
        "scatter"           single-scatter plot.
        "scatter_3d"        single-scatter plot in 3D.
        "scatters"          multi-scatter plot.
        "scatters_3d"       multi-scatter plot in 3D.
        "surface"           surface plot.
        "surface_cx"        surface plot with projection on X-axis.
        "surface_cy"        surface plot with projection on Y-axis.
        "surface_cz"        surface plot with projection on Z-axis.
        ==================  ====================================================

    .. note:: All the options defined in ``params`` supersede individual function arguments.
    """

    # attributes
    custom_palettes = {
        'blr': ['Blues_r', 'Reds'],
        'glr': ['Greens_r', 'Reds'],
        'rlb': ['Reds_r', 'Blues']
    }
    default_linestyles = ['-', '--', '-.', ':']
    default_markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']
    default_palettes = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'icefire', 'icefire_r', 'inferno', 'inferno_r', 'magma', 'magma_r', 'mako', 'mako_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 'rocket_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 'winter', 'winter_r']
    required_params = {
        'line': ['bins', 'height', 'palette', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale'],
        'lines': ['bins', 'height', 'legend_location', 'palette', 'show_legend', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale', 'y_label', 'y_legend', 'y_scale'],
        'scatter': ['bins', 'height', 'palette', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale'],
        'scatters': ['bins', 'height', 'legend_location', 'palette', 'show_legend', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale', 'y_label', 'y_legend', 'y_scale'],
        'contour': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale'],
        'contourf': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale'],
        'pcolormesh': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale'],
        'surface': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale'],
        'surface_cx': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale'],
        'surface_cy': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale'],
        'surface_cz': ['bins', 'cbar_position', 'cbar_title', 'height', 'palette', 'show_cbar', 'title', 'v_label', 'v_scale', 'width', 'x_label', 'x_scale', 'y_label', 'y_scale']
    }
    types_1D = ['line', 'lines', 'scatter', 'scatters']
    types_2D = ['contour', 'contourf', 'pcolormesh']
    types_3D = ['density', 'density_unit', 'line_3d', 'lines_3d', 'scatter_3d', 'scatters_3d', 'surface', 'surface_cx', 'surface_cy', 'surface_cz']
    ui_defaults = {
        'annotations': list(),
        'bins': 11,
        'cbar_position': 'right',
        'cbar_tick_labels': None,
        'cbar_ticks': None,
        'cbar_title': '',
        'cbar_x_label': '',
        'cbar_y_label': '',
        'component': 'real',
        'font_math': 'cm',
        'font_size_large': 20.0,
        'font_size_small': 16.0,
        'height': 4.8,
        'legend_location': 'best',
        'palette': 'RdBu_r',
        'show_cbar': False,
        'show_legend': False,
        'title': '',
        'type': 'contourf',
        'view_aspect': [1.0, 1.0, 1.0],
        'view_elevation': 32.0,
        'view_rotation': 215.0,
        'v_label': '$v$',
        'v_scale': 'linear',
        'vspan': list(),
        'width': 4.8,
        'x_label': '$x$',
        'x_scale': 'linear',
        'y_label': '$y$',
        'y_legend': [],
        'y_scale': 'linear',
        'z_label': '$x$',
        'z_scale': 'linear'
    }

    def __init__(self, axes: dict, params: dict):
        """Class constructor for BasePlotter."""

        # frequently used variables
        _palette = params.get('palette', self.ui_defaults['palette'])
        _bins = params.get('bins', self.ui_defaults['bins'])

        # se;ect axes
        self.axes = {
            'X': StaticAxis('X', axes, params),
            'Y': MultiAxis('Y', axes, params),
            'Z': StaticAxis('Z', axes, params),
            'V': DynamicAxis('V', axes, params),
            'V_twin': DynamicAxis('V_twin', axes, params)
        }

        # update bins
        self.bins = _bins

        # set params
        self.params = {
            'type': params.get('type', self.ui_defaults['type']),
            'title': params.get('title', self.ui_defaults['title']),
            'colors': self.get_colors(_palette, _bins),
            'palette': _palette,
            'font_dicts': {
                'label': self._get_font_dict(params, 'label'), 
                'tick': self._get_font_dict(params, 'tick'),
                'legend': self._get_font_dict(params, 'legend'),
                'math': params.get('font_math', self.ui_defaults['font_math'])
            },
            'legend': {
                'show': params.get('show_legend', self.ui_defaults['show_legend']),
                'location': params.get('legend_location', self.ui_defaults['legend_location']),
            },
            'cbar': {
                'show': params.get('show_cbar', self.ui_defaults['show_cbar']),
                'title': params.get('cbar_title', self.ui_defaults['cbar_title']),
                'position': params.get('cbar_position', self.ui_defaults['cbar_position']),
                'x_label': params.get('cbar_x_label', self.ui_defaults['cbar_x_label']),
                'y_label': params.get('cbar_y_label', self.ui_defaults['cbar_y_label']),
                'ticks': params.get('cbar_ticks', self.ui_defaults['cbar_ticks']),
                'tick_labels': params.get('cbar_tick_labels', self.ui_defaults['cbar_tick_labels'])
            },
            'component': params.get('component', self.ui_defaults['component']),
            'annotations': params.get('annotations', self.ui_defaults['annotations']),
            'height': params.get('height', self.ui_defaults['height']),
            'view': {
                'aspect': params.get('view_aspect', self.ui_defaults['view_aspect']),
                'elevation': params.get('view_elevation', self.ui_defaults['view_elevation']),
                'rotation': params.get('view_rotation', self.ui_defaults['view_rotation'])
            },
            'vspan': params.get('vspan', self.ui_defaults['vspan']),
            'width': params.get('width', self.ui_defaults['width'])
        }

    def _get_font_dict(self, params: dict, text_type: str): 
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
        _size = self.ui_defaults['font_size_large'] if text_type == 'label' else self.ui_defaults['font_size_small']
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
        palette : str or list
            Default or diverging color palette.
        bins : int
            Number of bins.
        
        Returns
        -------
        colors : list
            Colors in the palette.
        """

        # validate parameters
        assert type(palette) is str or type(palette) is list, 'Parameter ``palette`` should be either a string or a list'

        # if named color palette
        if type(palette) is str:
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
        
        # if list
        else:
            colors = palette

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
        _mini = np.real(mini)
        _maxi = np.real(maxi)
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
        _mini = np.floor(np.real(mini) * _mult) / _mult
        _maxi = np.ceil(np.real(maxi) * _mult) / _mult
        _prec = int(np.round(np.log10(_mult)))

        # return
        return _mini, _maxi, _prec