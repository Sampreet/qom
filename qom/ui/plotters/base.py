#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to interface plotters."""

__name__    = 'qom.ui.plotters.base'
__authors__ = ["Sampreet Kalita"]
__created__ = "2020-10-06"
__updated__ = "2023-07-10"

# dependencies
from decimal import Decimal
import logging
import numpy as np
import seaborn as sns

# qom modules
from ...io import Updater

# TODO: Validate parameters.

class BasePlotter():
    """Class to interface plotters.

    Initializes `axes`, `bins`, `params` and `updater`.
    
    Parameters
    ----------
    axes : dict
        Axes for the plot containing one or more keys for the axes (`'X'`, 'Y' or 'Z'), each either a list of values, or dictionary containing the following keys (arranged in the descending order of their priorities):
            ========    ====================================================
            key         value
            ========    ====================================================
            'var'       (*str*) name of the parameter to loop. Its value defaults to the axis name in lower case if the axis is a sequence of values and not a dictionary.
            'val'       (*list* or *numpy.ndarray*) values of the parameter. The remaining keys are not checked if its value is given. Otherwise, the values of `'min'`, `'max'`, `'dim'` and `'scale'` are used to obtain `'val'`.
            'min'       (*float*) minimum value of the parameter. Default is `-5.0`.
            'max'       (*float*) maximum value of the parameter. Default is `5.0`.
            'dim'       (*int*) number of values from 'min' to 'max', both inclusive. Default is `101`.
            'scale'     (*str*) step scale of the values. Options are `'log'` for logarithmic and `'linear'` for linear. Default is `'linear'`
            ========    ====================================================
    params : dict
        Parameters of the plot. Currently supported keys are:
            ========================    ====================================================
            key                         value
            ========================    ====================================================
            'annotations'               (*list*) annotation dictionaries for the plot. Refer to ``Notes`` below for currently supported keys.
            'bins'                      (*int*) number of colors for the plot. Default is `11`.
            'cbar_position'             (*str*) position of the color bar. Options are `'top'`, `'right'`, `'bottom'` and `'left'`. Default is `'right'`.
            'cbar_tick_labels'          (*list*) tick labels of the color bar.
            'cbar_ticks'                (*list*) ticks of the color bar.
            'cbar_title'                (*str*) title of the color bar. Default is `''`.
            'cbar_x_label'              (*str*) X-axis label of the color bar. Default is `''`.
            'cbar_y_label'              (*str*) Y-axis label of the color bar. Default is `''`.
            'colors'                    (*list*) colors of the 1D plots. If not provided, the palette colors are used.
            'component'                 (*str*) component of complex value. Options are `'real'` or `'imag'`. Default is `'real'`.
            'font_math'                 (*str*) math renderer for fonts. Options are `'dejavusans'`, `'dejavuserif'`, `'cm'`, `'stix'` and `'stixsans'`. Default is `'cm'`.
            'height'                    (*float*) height of the plot. Default is `5.0`.
            'legend_labels'             (*list*) labels of the legend. If a twin axis exists, the legend is not displayed.
            'legend_location'           (*bool*) location of the legend. Options are `'best'`, `'center'`, `'center left'`, `'center right'`, `'lower center'`, `'lower left'`, `'lower right'`, `'right'`, `'upper center'`, `'upper left'` and `'upper right'`. Default is `'best'`.
            'palette'                   (*str*) color palette of the plot. Refer to `default_palettes` attribute for available options. Default is `'RdBu_r'`.
            'show_cbar'                 (*bool*) option to show the color bar. Default is `False`.
            'show_legend'               (*bool*) option to show the legend. Default is `False`.
            'sizes'                     (*list*) size values for 1D plots. If not provided, a default value of `1.0` is used for each plot.
            'styles'                    (*list*) styles for 1D plots. If not provided, styles are set serially from `default_linestyles` (for line plots) and `default_markers` (for scatter plots) attributes.
            'type'                      (*str*) type of the plot. Refer to ``Notes`` below for all available options. Default is `'lines'`.
            'view_aspect'               (*list*) aspect ratios of the 3D axes. Default is `[1.0, 1.0, 1.0]`.
            'view_elevation'            (*float*) elevation for 3D view on Z-axis. Default is `32.0`.
            'view_rotation'             (*float*) rotation for 3D view about Z-axis in degrees. Default is `215.0`.
            'vertical_spans'            (*list*) vertical background spanning dictionaries for the plot. Refer to ``Notes`` below for currently supported keys.
            'width'                     (*float*) width of the plot. Default is `'5.0'`.
            ========================    ====================================================
    cb_update : callable
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.

    Notes
    -----
        Currently supported values of 'type' are:
            ================    ====================================================
            value               meaning
            ================    ====================================================
            'contour'           contour plot.
            'contourf'          filled contour plot.
            'density'           density plot.
            'density_unit'      density plot with unit sphere.
            'line'              single-line plot.
            'line_3d'           single-line plot in 3D.
            'lines'             multi-line plot.
            'lines_3d'          multi-line plot in 3D.
            'pcolormesh'        mesh color plot.
            'scatter'           single-scatter plot.
            'scatter_3d'        single-scatter plot in 3D.
            'scatters'          multi-scatter plot.
            'scatters_3d'       multi-scatter plot in 3D.
            'surface'           surface plot.
            'surface_cx'        surface plot with projection on X-axis.
            'surface_cy'        surface plot with projection on Y-axis.
            'surface_cz'        surface plot with projection on Z-axis.
            ================    ====================================================
        
        The properties of each axis (`'X'`, `'Y'`, `'Z'`, `'V'` and `'V_twin'`) can be set by prefixing the specific property with the lower-case name of the axis and an underscore, e.g. `'v_label'`. Currently supported keys are:
            ================    ================================================
            key                 value
            ================    ================================================
            'label'             (*str*) text of the axis label. If not provided, the values of `'name'` and `'unit'` are used for the label.
            'label_color'       (*str* or *int*) color of the axis label as an index from the color palette or a supported color string. Default is `'k'`.
            'label_pad'         (*int*) padding of the axis label. Default is `4`.
            'limits'            (*list*) minimum and maximum limits for the axis.
            'name'              (*str*) display name of the axis.
            'scale'             (*str*) step scale for the values. Options are `'linear'` (fallback) and `'log'`. Default is `'linear'`.
            'tick_color'        (*str* or *int*) color of the axis label as an index from the color palette or a supported color string. Default is `'k'`.
            'tick_dim'          (*float*) dimension of the ticks. Default is `'5'`.
            'tick_labels'       (*list*) tick labels of the plots.
            'tick_pad'          (*int*) padding of the tick labels. Default is `'8'`.
            'tick_position'     (*str*) position of ticks on the plot. Options are `'both-in'`, `'both-out'`, `'bottom-in'`, `'bottom-out'`, `'left-in'`, `'left-out'`, `'right-in'`, `'right-out'`, `'top-in'` and `'top-out'`. Default is `'both-in'`.
            'ticks'             (*list*) ticks of the plots.
            'ticks_minor'       (*list*) positions of minor ticks of the plots.
            'unit'              (*str*) unit of the plots.
            ================    ================================================

        The font properties of each text type (`'label'`, `legend'`, `'tick'` and `'title'`) can be set by prefixing the specific property with the lower-case name of the type and an underscore, e.g. `'label_font_family'`. Currently supported keys are:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'font_family'       (*str*) font family for the labels. Default is `'Times New Roman'`.
            'font_size'         (*float*) font size for the labels. Default is `20.0` for `'label'` and `'title'` and `16.0` for `'legend'` and `'tick'`.
            'font_stretch'      (*int*) font stretch for the labels. Default is `500`.
            'font_style'        (*str*) font style for the labels. Default is `'normal'`.
            'font_variant'      (*str*) font variant for the labels. Default is `'normal'`.
            'font_weight'       (*int*) font weightt for the labels. Default is `500`.
            ================    ====================================================

        The `'annotations'` array currently supports dictionaries with the following keys:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'text'              (*str*) the text. Default is `''`.
            'xy'                (*tuple*) tuple of positions of the text on the figure in fractions. Default is `(0.2, 0.8)`.
            'color'             (*str* or *int*) color of the axis label as an index from the color palette or a supported color string. Default is `'k'`.
            'font_dict_type'    (*str*) the type of font dictionary. Options are `'label'`, `'legend'`, `'tick'` and `'title'`. Default is `'label'`.
            'orientation'       (*str*) the orientation of the text. Options are `'horizontal'` and `'vertical'`. Default is `'horizontal'`.
            ================    ====================================================

        The `'vertical_spans'` array currently supports dictionaries with the following keys:
            ========    ====================================================
            key         value
            ========    ====================================================
            'limits'    (*list*) the minimum and maximum X-axis values as a tuple. Default is `(0.0, 0.0)`.
            'color'     (*str* or *int*) color of the axis label as an index from the color palette or a supported color string. Default is `'k'`.
            'alpha'     (*float*) the opacity value. Default is `0.25`.
            ========    ====================================================

    .. note:: Color palettes and font properties are currently backed by `matplotlib`. 
    """

    # color palettes
    custom_palettes = {
        'blr': ['Blues_r', 'Reds'],
        'glr': ['Greens_r', 'Reds'],
        'rlb': ['Reds_r', 'Blues']
    }
    """dict : Custom diverging palettes."""
    default_palettes = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'icefire', 'icefire_r', 'inferno', 'inferno_r', 'magma', 'magma_r', 'mako', 'mako_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 'rocket_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 'winter', 'winter_r']
    """list : Default `seaborn` palettes."""
    
    # types of plots
    types_1D = ['line', 'lines', 'scatter', 'scatters']
    """list : Types of 1D plots."""
    types_2D = ['contour', 'contourf', 'pcolormesh']
    """list : Types of 2D plots."""
    types_3D = ['density', 'density_unit', 'line_3d', 'lines_3d', 'scatter_3d', 'scatters_3d', 'surface', 'surface_cx', 'surface_cy', 'surface_cz']
    """list : Types of 3D plots."""

    # required parameter keys for each type of plot
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
    """dict : Required parameter keys for each type of plot."""

    # 1D plot styles
    default_linestyles = ['-', '--', '-.', ':']
    """list : Default linestyles for line plots."""
    default_markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']
    """list : Default markers for scatter plots."""

    # default parameters of the plotter
    plotter_defaults = {
        'annotations': list(),
        'bins': 11,
        'cbar_position': 'right',
        'cbar_tick_labels': None,
        'cbar_ticks': None,
        'cbar_title': '',
        'cbar_x_label': '',
        'cbar_y_label': '',
        'colors': None,
        'component': 'real',
        'font_math': 'cm',
        'font_family': 'Times New Roman',
        'font_size_large': 20.0,
        'font_size_small': 16.0,
        'font_stretch': 500,
        'font_style': 'normal',
        'font_variant': 'normal',
        'font_weight': 500,
        'height': 5.0,
        'legend_labels': list(),
        'legend_location': 'best',
        'palette': 'RdBu_r',
        'show_cbar': False,
        'show_legend': False,
        'sizes': None,
        'styles': None,
        'title': '',
        'type': 'lines',
        'view_aspect': [1.0, 1.0, 1.0],
        'view_elevation': 32.0,
        'view_rotation': 215.0,
        'vertical_spans': list(),
        'width': 5.0,
    }
    """dict : Default parameters of the plotter."""

    def __init__(self, axes:dict, params:dict, cb_update):
        """Class constructor for BasePlotter."""

        # select axes
        self.axes = {
            'X': BaseAxis(
                axis='X',
                params=axes.get('X', None),
                params_plotter=params
            ),
            'Y': BaseAxis(
                axis='Y',
                params=axes.get('Y', None),
                params_plotter=params
            ),
            'Z': BaseAxis(
                axis='Z',
                params=axes.get('Z', None),
                params_plotter=params
            ),
            'V': BaseAxis(
                axis='V',
                params=axes.get('V', None),
                params_plotter=params
            ),
            'V_twin': BaseAxis(
                axis='V_twin',
                params=axes.get('V_twin', None),
                params_plotter=params
            )
        }

        # set palette colors
        _palette = params.get('palette', self.plotter_defaults['palette'])
        _bins = params.get('bins', self.plotter_defaults['bins'])
        self.palette_colors = self.get_colors(
            palette=_palette,
            bins=_bins
        )

        # set params
        self.params = {
            'annotations': params.get('annotations', self.plotter_defaults['annotations']),
            'bins': _bins,
            'cbar': {
                'show': params.get('show_cbar', self.plotter_defaults['show_cbar']),
                'title': params.get('cbar_title', self.plotter_defaults['cbar_title']),
                'position': params.get('cbar_position', self.plotter_defaults['cbar_position']),
                'x_label': params.get('cbar_x_label', self.plotter_defaults['cbar_x_label']),
                'y_label': params.get('cbar_y_label', self.plotter_defaults['cbar_y_label']),
                'ticks': params.get('cbar_ticks', self.plotter_defaults['cbar_ticks']),
                'tick_labels': params.get('cbar_tick_labels', self.plotter_defaults['cbar_tick_labels'])
            },
            'colors': params.get('colors', self.plotter_defaults['colors']),
            'component': params.get('component', self.plotter_defaults['component']),
            'font_math': params.get('font_math', self.plotter_defaults['font_math']),
            'font_dicts': {
                'label': self._get_font_dict(
                    params=params,
                    font_dict_type='label'
                ),
                'legend': self._get_font_dict(
                    params=params,
                    font_dict_type='legend'
                ),
                'tick': self._get_font_dict(
                    params=params,
                    font_dict_type='tick'
                ),
                'title': self._get_font_dict(
                    params=params,
                    font_dict_type='title'
                ),
            },
            'height': params.get('height', self.plotter_defaults['height']),
            'legend': {
                'show': params.get('show_legend', self.plotter_defaults['show_legend']),
                'labels': params.get('legend_labels', self.plotter_defaults['legend_labels']),
                'location': params.get('legend_location', self.plotter_defaults['legend_location'])
            },
            'palette': _palette,
            'sizes': params.get('sizes', self.plotter_defaults['sizes']),
            'styles': params.get('styles', self.plotter_defaults['styles']),
            'title': params.get('title', self.plotter_defaults['title']),
            'type': params.get('type', self.plotter_defaults['type']),
            'view': {
                'aspect': params.get('view_aspect', self.plotter_defaults['view_aspect']),
                'elevation': params.get('view_elevation', self.plotter_defaults['view_elevation']),
                'rotation': params.get('view_rotation', self.plotter_defaults['view_rotation'])
            },
            'vertical_spans': params.get('vertical_spans', self.plotter_defaults['vertical_spans']),
            'width': params.get('width', self.plotter_defaults['width'])
        }

        # set updater
        self.updater = Updater(
            logger=logging.getLogger('qom.ui.plotters.' + self.name),
            cb_update=cb_update
        )

    def _get_font_dict(self, params:dict, font_dict_type:str): 
        """Method to generate a dictionary of font properties for a given type of text.

        Parameters
        ----------
        params : dict
            Plot parameters passed.
        font_dict_type : {`'label'`, `legend'`, `'tick'`, `'title'`}
            Type of font dictionary.

        Returns
        -------
        font_dict : dict
            Dictionary of font properties.
        """

        # properties
        _family = params.get(font_dict_type + '_font_family', self.plotter_defaults['font_family'])
        _size = self.plotter_defaults['font_size_large'] if 'label' in font_dict_type or 'title' in font_dict_type else self.plotter_defaults['font_size_small']
        _size = params.get(font_dict_type + '_font_size', _size)
        _stretch = params.get(font_dict_type + '_font_stretch', self.plotter_defaults['font_stretch'])
        _style = params.get(font_dict_type + '_font_style', self.plotter_defaults['font_style'])
        _variant = params.get(font_dict_type + '_font_variant', self.plotter_defaults['font_variant'])
        _weight = params.get(font_dict_type + '_font_weight', self.plotter_defaults['font_weight'])

        # font dictionary
        _font_dict = {
            'family': _family,
            'size': _size,
            'stretch': _stretch,
            'style': _style,
            'variant': _variant,
            'weight': _weight
        }

        # return
        return _font_dict

    def get_colors(self, palette:str='RdBu_r', bins:int=11):
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
        assert type(palette) is str or type(palette) is list, "Parameter `palette` should be either a string or a list"

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

    def get_limits(self, mini:float, maxi:float, res:int=2):
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

class BaseAxis():
    """Class to interface axes.

    Initializes `bound`, `dim`, `label`, `label_color`, `label_pad`, `limits`, `name`, `scale`, `tick_dim`, `tick_labels`, `tick_pad`, `tick_position`, `ticks`, `ticks_minor`, `unit` and `val`. Inherited objects need to set the other properties individually.

    Parameters
    ----------
    axis : {`'X'`, `'Y'`, `'Z'`, `'V'`, `'V_twin'`}
        Name of the axis.
    params : dict or list
        Parameters of the axis as a list of values, or a dictionary. Refer to :class:`qom.ui.plotters.base.BasePlotter` for currently supported keys.
    params_plotter : dict
        Parameters for the plotter. Refer to ``Notes`` of :class:`qom.ui.plotters.base.BasePlotter` for all available options.
    """

    axis_defaults = {
        'label': '',
        'label_color': 'k',
        'label_pad': 4,
        'limits': None, 
        'name': '',
        'scale': 'linear',
        'tick_color': 'k',
        'tick_dim': 5,
        'tick_labels': None,
        'tick_pad': 8,
        'tick_position': 'both-in',
        'ticks': list(),
        'ticks_minor': None,
        'unit': ''
    }
    """dict : Default parameters of the axis."""

    def __init__(self, axis, params, params_plotter):
        """Class constructor for BaseAxis."""

        # set parameters
        _params = dict()
        for key in self.axis_defaults:
            _params[key] = params_plotter.get(axis.lower() + '_' + key, self.axis_defaults[key])

        # handle list
        if type(params) is list:
            params = np.array(params)

        # convert to dictionary
        if type(params) is np.ndarray:
            params = {
                'val': params
            }

        # if values available
        if params is not None:
            _val = params.get('val', None)
            # validate and update values
            if _val is not None:
                assert len(_val) != 0, "Key `'{}'` should contain key `'val'` with a non-empty array".format(axis)
                self.val = _val
            # validate and initialize values
            else:
                assert 'min' in params and 'max' in params, "Key '{}' should contain keys 'min' and 'max' to define axis range".format(axis)
                self.val = self._init_array(np.float_(params['min']), np.float_(params['max']), int(params.get('dim', 101)), str(params.get('scale', 'linear')))

            # update range
            _min = 0 if type(self.val[0]) is str else np.min(self.val)
            _max = len(self.val) if type(self.val[0]) is str else np.max(self.val)
        # no values available
        else:
            self.val = self._init_array(1, _params['tick_dim'], int(_params['tick_dim']), _params['scale'])

            # update range
            _min = self.val[0]
            _max = self.val[-1]

        # set dimension
        self.dim = len(self.val)

        # set name
        self.name = _params['name']

        # set unit
        self.unit = _params['unit']

        # set label
        self.label = _params['label']
        if self.label == '':
            self.label = self.name if self.unit == '' else '{name} ({unit})'.format(name=self.name, unit=self.unit)

        # set label color
        self.label_color = _params['label_color']

        # set label padding
        self.label_pad = int(_params['label_pad'])

        # set scale
        self.scale = _params['scale']

        # set tick color
        self.tick_color = _params['tick_color']

        # set tick dimension
        self.tick_dim = _params['tick_dim']

        # set tick padding
        self.tick_pad = int(_params['tick_pad'])

        # set tick position
        self.tick_position = _params['tick_position']

        # set ticks
        _ticks = _params['ticks']
        # handle list
        if type(_ticks) is list:
            _ticks = np.array(_ticks)
        # if ticks are defined
        if type(_ticks) is np.ndarray and len(_ticks) != 0:
            self.ticks = _ticks
            self.tick_dim = len(_ticks)
            self.bound = True
            self.limits = _params['limits'] if _params['limits'] is not None else [np.min(_ticks), np.max(_ticks)]
        # else initialize ticks
        else:
            self.ticks = self._init_array(_min, _max, self.tick_dim, self.scale)
            self.bound = False

        # set minor ticks
        self.ticks_minor = _params['ticks_minor']

        # set tick labels
        _tick_labels = _params['tick_labels']
        # if ticks labels are defined
        if type(_tick_labels) is list and len(_tick_labels) != 0:
            self.tick_labels = _tick_labels
        # else same as ticks
        else:
            self.tick_labels = self.ticks 

        # supersede ticks by tick labels
        if len(self.tick_labels) != len(self.ticks):
            self.ticks = self._init_array(1, len(self.tick_labels), len(self.tick_labels), self.scale)

    def _init_array(self, mini, maxi, dim: int, scale:str):
        """Function to initialize an array given a range and number of elements.

        Parameters
        ----------
        mini : int
            Minimum value of the range.
        maxi : int
            Maximum value of the range.
        dim : int
            Number of elements to consider.
        scale : {`'linear'`, `'log'`}
            Step scale for the values.

        Returns
        -------
        values : numpy.ndarray
            Initialized array.
        """

        # set values
        if scale == 'log': 
            values = np.logspace(np.log10(mini), np.log10(maxi), dim)
        else:
            values = np.linspace(mini, maxi, dim)
            # truncate values
            _step_size = (Decimal(str(maxi)) - Decimal(str(mini))) / (dim - 1)
            _decimals = - _step_size.as_tuple().exponent
            values = np.around(values, _decimals)

        return values