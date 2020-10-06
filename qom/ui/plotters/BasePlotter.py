#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface plots."""

__name__    = 'qom.ui.plotters.BasePlotter'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-06'
__updated__ = '2020-10-06'

# dependencies
import logging
import seaborn as sns

# module logger
logger = logging.getLogger(__name__)

# TODO: Add inheritable methods.

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
        plot_type : str
            Type of plot. Default is `line`.
        
        font_dicts : dict
            Font properties for labels and ticks.

        axes : :class:`matplotlib.*` or :class:`plotly.*`
            Axes for the figure.

        values : dict
            Values of the axes as lists.

        plot : :class:`matplotlib.*` or :class:`plotly.*`
            Plot for the figure.

        head : :class:`matplotlib.*` or :class:`plotly.*`
            Point to indicate the current position.

        cbar : :class:`matplotlib.*` or :class:`plotly.*`
            Colorbar for the figure.
            
        labels : dict
            Dictionaries of axes labels.
    """

    # attributes
    plot_types_1D = ['line', 'lines', 'scatter', 'scatters']
    plot_types_2D = ['contourf', 'pcolormesh']
    plot_types_3D = ['surface', 'surface_cx', 'surface_cy', 'surface_cz']
    bins = 11
    cmaps = {
        'blr': sns.diverging_palette(250, 15, s=75, l=40, n=bins, center='light', as_cmap=True),
        'rlb': sns.diverging_palette(15, 250, s=75, l=40, n=bins, center='light', as_cmap=True),
        'glr': sns.diverging_palette(150, 15, s=75, l=40, n=bins, center='light', as_cmap=True)
    }

    @property
    def plot_type(self):
        """Property plot type.

        Returns
        -------
            plot_type : str
                Type of plot. Default is `line`.
        """

        return self.__plot_type
    
    @plot_type.setter
    def plot_type(self, plot_type):
        """Setter for plot type.

        Parameters
        ----------
            plot_type : str
                Type of plot. Default is `line`.
        """

        self.__plot_type = plot_type

    @property
    def font_dicts(self):
        """Property font dictionary.

        Returns
        -------
            font_dicts : dict
                Font properties for labels and ticks.
        """

        return self.__font_dicts
    
    @font_dicts.setter
    def font_dicts(self, font_dicts):
        """Setter for font dictionary.

        Returns
        -------
            font_dicts : dict
                Font properties for labels and ticks.
        """

        self.__font_dicts = font_dicts

    @property
    def labels(self):
        """Property labels.

        Returns
        -------
            labels : dict
                Dictionaries of axes labels.
        """

        return self.__labels
    
    @labels.setter
    def labels(self, labels):
        """Setter for fonts.

        Returns
        -------
            labels : dict
                Dictionaries of axes labels.
        """

        self.__labels = labels

    @property
    def axes(self):
        """Property axes.

        Returns
        -------
            axes : :class:`matplotlib.axes.Axes`
                Axes for the figure. Default is :class:`matplotlib.axes.Axes`.
        """

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        """Setter for axes.

        Parameters
        ----------
            axes : :class:`matplotlib.axes.Axes`
                Axes for the figure. Default is :class:`matplotlib.axes.Axes`.
        """

        self.__axes = axes

    @property
    def values(self):
        """Property values.

        Returns
        -------
            values : list
                Values of the axes.
        """

        return self.__values
    
    @values.setter
    def values(self, values):
        """Setter for values.

        Parameters
        ----------
            values : list
                Values of the axes.
        """

        self.__values = values

    @property
    def plot(self):
        """Property plot.

        Returns
        -------
            plot : :class:`matplotlib.*`
                Plot for the figure.
        """

        return self.__plot
    
    @plot.setter
    def plot(self, plot):
        """Setter for plot.

        Parameters
        ----------
            plot : :class:`matplotlib.*`
                Plot for the figure.
        """

        self.__plot = plot

    @property
    def head(self):
        """Property head.

        Returns
        -------
            head : :class:`matplotlib.lines.Line2D`
                Line to indicate the point of processing.
        """

        return self.__head
    
    @head.setter
    def head(self, head):
        """Setter for head.

        Returns
        -------
            head : :class:`matplotlib.lines.Line2D`
                Line to indicate the point of processing.
        """

        self.__head = head

    @property
    def cbar(self):
        """Property cbar.

        Returns
        -------
            cbar : :class:`matplotlib.colorbar.Colorbar`
                Colorbar for 2D color figures.
        """

        return self.__cbar
    
    @cbar.setter
    def cbar(self, cbar):
        """Setter for cbar.

        Returns
        -------
            cbar : :class:`matplotlib.colorbar.Colorbar`
                Colorbar for 2D color figures.
        """

        self.__cbar = cbar

    def __init__(self, plot_params, Axes):
        """Class constructor for MPLPlotter.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            Axes : dict
                Axes used for the plot as :class:`qom.utils.axis.StaticAxis`.
        """

        # set plot type
        self.plot_type = plot_params.get('type', 'line')

        # set label and tick fonts
        self.font_dicts = dict()
        self.__font_dicts['label'] = self.__get_font_dict(plot_params, 'label')
        self.__font_dicts['tick'] = self.__get_font_dict(plot_params, 'tick')

        # default labels
        _x_label = Axes['X'].label if Axes.get('X', None) is not None else ''
        _y_label = Axes['Y'].label if Axes.get('Y', None) is not None else ''
        _z_label = Axes['Z'].label if Axes.get('Z', None) is not None else ''
        self.labels = {
            'X': plot_params.get('x_label', _x_label),
            'Y': plot_params.get('y_label', _y_label),
            'Z': plot_params.get('z_label', _z_label),
            'cbar': plot_params.get('cbar_label', '')
        }

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
        _family = plot_params.get(text_type + 'font_family', 'Times New Roman')
        _style = plot_params.get(text_type + 'font_style', 'normal')
        _variant = plot_params.get(text_type + 'font_variant', 'normal')
        _weight = plot_params.get(text_type + 'font_weight', 500)
        _stretch = plot_params.get(text_type + 'font_stretch', 500)
        _size = 16.0 if text_type == 'label' else 12.0
        _size = plot_params.get(text_type + 'font_size', _size)

        _font_dict = {
            'family': _family,
            'style': _style,
            'variant': _variant,
            'weight': _weight,
            'stretch': _stretch,
            'size': _size
        }

        return _font_dict