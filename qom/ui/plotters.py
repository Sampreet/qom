#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to handle matplotlib and pyplot plots."""

__name__    = 'qom.ui.plotters'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-03'
__updated__ = '2020-10-03'

# dependencies
from matplotlib.font_manager import FontProperties 
from matplotlib.lines import Line2D
import logging
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# module logger
logger = logging.getLogger(__name__)

# TODO: Add annotations.
# TODO: Options for `ticklabel_format`.
# TODO: Handle contour, contourf plots.
# TODO: Handle 3D.

class PlotterMPL():
    """Class to generate matplotlib plots.

    Attributes
    ----------
        plot_types_1D : list
            List of supported 1D plots:
                line: Line plot.
                lines: Multi-line plot.
                scatter: Scatter plot.
                scatters: Multi-scatter plot

        plot_types_2D : list
            List of supported 2D plots:
                pcolormesh: Color plot.
        
        plot_types_3D : list
            List of supported 3D plots.

    Properties
    ----------
        plot_type : str
            Type of plot. Default is `line`.
        
        font_props : dict
            Font properties for labels and ticks as :class:`matplotlib.font_manager.FontProperties`.

        axes : :class:`matplotlib.axes.Axes` or :class:`mpl_toolkits.mplot3d.Axes3D`
            Axes for the figure. Default is :class:`matplotlib.axes.Axes`.

        plot : :class:`matplotlib.*`
            Variable plot classes depending on the type of figure.

        head : :class:`matplotlib.lines.Line2D`
            Line to indicate the point of processing.

        cbar : :class:`matplotlib.colorbar.Colorbar`
            Colorbar for 2D color figures.
            
        labels : dict
            Dictionaries of axes labels.
    """

    # attributes
    plot_types_1D = ['line', 'lines', 'scatter', 'scatters']
    plot_types_2D = ['pcolormesh']
    plot_types_3D = []

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
    def font_props(self):
        """Property font properties.

        Returns
        -------
            font_props : dict
                Font properties for labels and ticks as :class:`matplotlib.font_manager.FontProperties`.
        """

        return self.__font_props
    
    @font_props.setter
    def font_props(self, font_props):
        """Setter for font properties.

        Returns
        -------
            font_props : dict
                Font properties for labels and ticks as :class:`matplotlib.font_manager.FontProperties`.
        """

        self.__font_props = font_props

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
        self.font_props = dict()
        self.__font_props['label'] = self.__get_font_properties(plot_params, 'label')
        self.__font_props['tick'] = self.__get_font_properties(plot_params, 'tick')
        # update math fonts
        plt.rcParams['mathtext.fontset'] = plot_params.get('font_math', 'cm')

        # set axes
        self.axes = plt.gca(projection='3d' if self.__plot_type in self.plot_types_3D else None)

        # update title
        plt.title(plot_params.get('title', ''), fontdict=self.__get_font_dict(self.__font_props['label']))

        # update ticks
        plt.xticks(fontproperties=self.__font_props['tick'])
        plt.yticks(fontproperties=self.__font_props['tick'])
        plt.ticklabel_format(axis='both', style='plain')

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
        # update labels
        plt.xlabel(self.__labels.get('X'), fontdict=self.__get_font_dict(self.__font_props['label']))
        plt.ylabel(self.__labels.get('Y'), fontdict=self.__get_font_dict(self.__font_props['label']))

        # initialize 1D plot
        if self.__plot_type in self.plot_types_1D:
            _xs = Axes['X'].values if Axes.get('X', None) is not None else [0, 1]
            _x_ticks = Axes['X'].ticks if Axes.get('X', None) is not None else [0, 1]
            _x_tick_labels = Axes['X'].tick_labels if Axes.get('X', None) is not None else [0, 1]
            # for line and scatter plots
            _colors = [plot_params.get('color', 'b')] 
            _legends = [plot_params.get('legend', '')] 
            _linestyles = [plot_params.get('linestyles', '-')] 
            _sizes = [plot_params.get('sizes', 2)] 
            # for multi-line and multi-scatter plots
            if Axes.get('Z', None) is not None:
                _colors = Axes['Z'].colors
                _legends = Axes['Z'].legends
                _linestyles = Axes['Z'].linestyles
                _sizes = Axes['Z'].sizes
            # initialize 1D plot
            self.__init_1D(_xs, _x_ticks, _x_tick_labels, _colors, _legends, _linestyles, _sizes)

        # initialize 2D plot
        elif self.__plot_type in self.plot_types_2D:
            _xs = Axes['X'].values if Axes.get('X', None) is not None else [0, 1]
            _x_ticks = Axes['X'].ticks if Axes.get('X', None) is not None else [0, 1]
            _x_tick_labels = Axes['X'].tick_labels if Axes.get('X', None) is not None else [0, 1]
            _ys = Axes['Y'].values if Axes.get('Y', None) is not None else [0, 1]
            _y_ticks = Axes['Y'].ticks if Axes.get('Y', None) is not None else [0, 1]
            _y_tick_labels = Axes['Y'].tick_labels if Axes.get('Y', None) is not None else [0, 1]
            _cbar = plot_params.get('cbar', True)
            _color_grad = plot_params.get('color_grad', 'blr')
            _shading = plot_params.get('shading', 'gouraud')

            self.__init_2D(_xs, _ys, _x_ticks, _y_ticks, _x_tick_labels, _y_tick_labels, _cbar, _color_grad, _shading)

        # initialize 3D plot
        else:
            pass

    def __get_font_properties(self, plot_params, text_type): 
        """Method to generate font properties for a given type of text.

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
            font_properties : :class:`matplotlib.font_manager.FontProperties`
                Font properties.
        """

        # properties
        _family = plot_params.get(text_type + 'font_family', 'Times New Roman')
        _style = plot_params.get(text_type + 'font_style', 'normal')
        _variant = plot_params.get(text_type + 'font_variant', 'normal')
        _weight = plot_params.get(text_type + 'font_weight', 500)
        _stretch = plot_params.get(text_type + 'font_stretch', 500)
        _size = 16.0 if text_type == 'label' else 12.0
        _size = plot_params.get(text_type + 'font_size', _size)

        return FontProperties(
            family=_family,
            style=_style,
            variant=_variant,
            weight=_weight,
            stretch=_stretch,
            size=_size
        )

    def __get_font_dict(self, font_properties):
        """Method to obtain a dictionary for given font properties.
         
        Parameters
        ----------
            font_properties : :class:`matplotlib.font_manager.FontProperties`
                Font properties.

        Returns
        -------
            font_dict : dict
                Dictionary for font properties.
        """

        return {
            'family': font_properties.get_family(),
            'style': font_properties.get_style(),
            'variant': font_properties.get_variant(),
            'weight': font_properties.get_weight(),
            'stretch': font_properties.get_stretch(),
            'size': font_properties.get_size()
        }

    def __init_1D(self, xs, x_ticks, x_tick_labels, colors, legends, linestyles, sizes):
        """Method to initialize 1D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.

            x_ticks : list
                Ticks for the X-axis.

            x_tick_labels : list
                Tick_labels for the X-axis.

            colors : list
                Colors for the plots.

            legends : list
                Legends for the plots.

            linestyles : list
                Linestyles for line plots.

            sizes : list
                Marker sizes for scatter plots.
        """

        # frequently used variables
        _dim = len(legends)

        # update axes
        if type(xs[0]) is not str:
            self.__axes.set_xlim(xs[0], xs[-1])

        # line plots
        if self.__plot_type == 'line' or self.__plot_type == 'lines':
            # collection
            self.plot = [Line2D([], [], color=colors[i], linestyle=linestyles[i]) for i in range(_dim)]
            [self.__axes.add_line(self.__plot[i]) for i in range(_dim)]
            # heads
            self.head = [Line2D([], [], color=colors[i], linestyle=linestyles[i], marker='o') for i in range(_dim)]
            [self.__axes.add_line(self.__head[i]) for i in range(_dim)]

        # scatter plots
        elif self.__plot_type == 'scatter' or self.__plot_type == 'scatters':
            self.plot = [self.__axes.scatter([], [], c=colors[i], s=sizes[i]) for i in range(_dim)]  
        
        # update ticks
        plt.xticks(ticks=x_ticks, labels=x_tick_labels)

        # update legends
        if legends is not None and legends[0] != '':
            _l = plt.legend(legends, loc='best')            
            plt.setp(_l.texts, fontproperties=self.__font_props['label'])

    def __init_2D(self, xs, ys, x_ticks, y_ticks, x_tick_labels, y_tick_labels, cbar=True, color_grad='blr', shading='gouraud'):
        """Method to initialize 2D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.
                
            ys : list
                Y-axis values.

            x_ticks : list
                Ticks for the X-axis.

            y_ticks : list
                Ticks for the Y-axis.

            x_tick_labels : list
                Tick_labels for the X-axis.

            y_tick_labels : list
                Tick_labels for the Y-axis.

            cbar : bool, optional
                Option to plot colorbar.

            color_grad : str, optional
                Color gradients for the plot:
                    'blr' : Blue-Light-Red.
                    'rlb' : Red-Light-Blue.
                    'glr' : Green-Light-Red.

            shading : str, optional
                Shading of the plot.
        """

        # update axes
        self.__axes.set_xlim(xs[0], xs[-1])
        self.__axes.set_ylim(ys[0], ys[-1])

        # generate color map
        if color_grad == 'blr':
            _cmap = sns.diverging_palette(250, 15, s=75, l=40, n=9, center='light', as_cmap=True)
        if color_grad == 'rlb':
            _cmap = sns.diverging_palette(15, 250, s=75, l=40, n=9, center='light', as_cmap=True)
        if color_grad == 'glr':
            _cmap = sns.diverging_palette(150, 15, s=75, l=40, n=9, center='light', as_cmap=True)

        # initailize values
        _X, _Y = np.meshgrid(xs, ys)
        _nans = np.zeros((len(ys), len(xs)))
        _nans[:] = np.NaN

        # pcolormesh plot
        if self.__plot_type == 'pcolormesh':
            self.plot = self.__axes.pcolormesh(_X, _Y, _nans, shading=shading, cmap=_cmap)

        # pcolormesh plot
        if self.__plot_type == 'contourf':
            self.plot = self.__axes.contourf(_X, _Y, _nans, cmap=_cmap)
        
        # update ticks
        plt.xticks(ticks=x_ticks, labels=x_tick_labels)
        plt.yticks(ticks=y_ticks, labels=y_tick_labels)

        # add color bar
        if cbar:
            self.cbar = plt.colorbar(self.__plot)
            # labels
            self.__cbar.set_label(self.__labels['cbar'], fontproperties=self.__font_props['label'])
            # ticks
            plt.setp(self.__cbar.ax.get_yticklabels(), fontproperties=self.__font_props['tick'])

    def update(self, X=None, Y=None, Z=None, head=False):
        """Method to update plot.
        
        Parameters
        ----------
            X : list, optional
                X-axis data as :class:`qom.utils.axis.DynamicAxis`.
                
            Y : list, optional
                Y-axis data as :class:`qom.utils.axis.DynamicAxis`.
                
            Z : list, optional
                Z-axis data as :class:`qom.utils.axis.DynamicAxis`.

            head : boolean, optional
                Option to display the head for line-type plots. Default is False.
        """

        # single-line plot
        if self.__plot_type == 'line':
            self.__update_1D([X.values], [Y.values], dim=X.size[0], head=head)
        # multi-line plot
        if self.__plot_type == 'lines':
            self.__update_1D(X.values, Y.values, dim=X.size[1], head=head)
        # scatter plot
        if self.__plot_type == 'scatter':
            self.__update_1D([X.values], [Y.values], head=head)
        # scatter plot
        if self.__plot_type == 'scatters':
            self.__update_1D(X.values, Y.values, head=head)
        
        # 2D plot
        if self.__plot_type == 'contourf':
            self.__update_2D(Z.values)
        if self.__plot_type == 'pcolormesh':
            self.__update_2D(Z.values)

    def __update_1D(self, xs, ys, dim=None, head=False):
        """Method to udpate 1D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.
                
            ys : list
                Y-axis values.
                
            dim : int
                Dimension of the X-axis.

            head : boolean
                Option to display the head for line-type plots.
        """
        
        # update line plots
        if self.__plot_type == 'line' or self.__plot_type == 'lines':
            for j in range(len(self.__plot)):
                self.__plot[j].set_xdata(xs[j])
                self.__plot[j].set_ydata(ys[j])
                if head and len(xs[j]) != dim and len(xs[j]) != 0:
                    self.__head[j].set_xdata(xs[j][-1:])
                    self.__head[j].set_ydata(ys[j][-1:])
                else:
                    self.__head[j].set_xdata([])
                    self.__head[j].set_ydata([])

        # update scatter plots
        if self.__plot_type == 'scatter' or self.__plot_type == 'scatters':
            for j in range(len(self.__plot)):
                XY = np.c_[xs[j], ys[j]]
                self.__plot[j].set_offsets(XY)
                
        # handle nan values for limits
        _minis = []
        _maxis = []
        for j in range(len(ys)):
            # calculate minimum and maximum values
            if len(ys[j]) != 0:
                # handle NaN values
                _no_nan = [y if y == y else 0 for y in ys[j]]

                # update limits
                _minis.append(min(_no_nan))
                _maxis.append(max(_no_nan))

        # set limits
        _mini, _maxi = min(_minis), max(_maxis)
        self.__axes.set_ylim(_mini, _maxi)

    def __update_2D(self, zs):
        """Method to udpate 2D plots.
        
        Parameters
        ----------
            zs : list
                Z-axis values.
        """
        
        # update pcolormesh plot
        rave = np.ravel(zs)

        # contourf plot
        if self.__plot_type == 'contourf':
            self.__axes.clear()
            self.__axes.contourf(zs)
        # pcolormesh plot
        if self.__plot_type == 'pcolormesh':
            self.__plot.set_array(rave)

        # handle NaN values
        _no_nan = [z if z == z else 0 for z in rave]

        # set limits
        _mini, _maxi = min(_no_nan), max(_no_nan)
        self.__plot.set_clim(vmin=_mini, vmax=_maxi)

        # color bar
        _ticks = np.linspace(_mini, _maxi, 11)
        self.__cbar.set_ticks(_ticks)
        self.__cbar.ax.set_autoscale_on(True)
        self.__cbar.draw_all()

    def show(self, hold=False):
        """Method to display plot.

        Parameters
        ----------
            hold : boolean, optional
                Option to hold the plot. Default is True.
        """

        # draw data
        plt.draw()

        # display plot
        if hold:
            plt.show()
        else:
            plt.pause(1e-9)
        