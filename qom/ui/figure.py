#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""UI module to display matplotlib plots."""

__name__    = 'qom.ui.figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2020-09-27'

# dependencies
from matplotlib.lines import Line2D
import logging
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# module logger
logger = logging.getLogger(__name__)

# TODO: handle contour, contourf plots.

class Plotter():
    """Class containing various 2D plot scenarios.

    Properties
    ----------
        axes : :class:`matplotlib.axes.Axes`
            Axes for the figure.

        plot : :class:`matplotlib.*`
            Variable plot classes depending on the type of figure.

        head : :class:`matplotlib.lines.Line2D`
            Line to indicate the point of processing.

        cbar : :class:`matplotlib.colorbar.Colorbar`
            Colorbar for 2D color figures.

        plot_type : str
            Type of plot:
                contour: Contour plot.
                contourf: Filled contour plot.
                line: Line plot.
                lines: Multi-line plot.
                pcolormesh: Color plot.
                scatter: Scatter plot.
                scatters: Multi-scatter plot.
        
        fonts : dict
            Dictionaries of font settings for text and mathematical symbols.
            
        labels : dict
            Dictionaries of axes labels.
    """

    def __init__(self, plot_params, X, Y=None, Z=None):
        """Class constructor for Plotter2D.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            X : :class:`qom.utils.axis.StaticAxis` or :class:`qom.utils.axis.DynamicAxis`
                X-axis data.

            Y : :class:`qom.utils.axis.StaticAxis` or :class:`qom.utils.axis.DynamicAxis`, optional
                Y-axis data.

            Z : :class:`qom.utils.axis.StaticAxis` or :class:`qom.utils.axis.DynamicAxis`, optional
                Z-axis data.
        """
        
        # initialize plot
        self.__init_plot(plot_params)
            
        # single-line plot
        if self.__plot_type == 'line':
            colors = [plot_params['color'] if 'color' in plot_params else 'r']
            linestyles = [plot_params['linestyle'] if 'linestyle' in plot_params else '-']
            legends = [plot_params['legend'] if 'legend' in plot_params else '']
            self.__init_1D(X.values, 1, colors, linestyles=linestyles, legends=legends, xticks=X.ticks)
        # multi-line plot
        elif self.__plot_type == 'lines':
            self.__init_1D(X.values, len(Z.legends), Z.colors, linestyles=Z.linestyles, legends=Z.legends, xticks=X.ticks)
        # scatter plot
        elif self.__plot_type == 'scatter':
            colors = [plot_params['color'] if 'color' in plot_params else 'r']
            sizes = [plot_params['size'] if 'size' in plot_params else 2]
            legends = [plot_params['legend'] if 'legend' in plot_params else '']
            self.__init_1D(X.values, 1, colors, sizes=sizes, legends=legends, xticks=X.ticks)
        # multi-scatter plot
        elif self.__plot_type == 'scatters':
            self.__init_1D(X.values, len(Z.legends), Z.colors, sizes=Z.sizes, legends=Z.legends, xticks=X.ticks)

        # contourf plot
        elif self.plot_type == 'contourf':
            self.__init_2D(X.values, Y.values, plot_params, xticks=X.ticks, yticks=Y.ticks)
        # pcolormesh plot
        elif self.plot_type == 'pcolormesh':
            self.__init_2D(X.values, Y.values, plot_params, xticks=X.ticks, yticks=Y.ticks)

        # display initialization
        logger.info('----------------------------Figure Initialized-------------------\t\n')

    @property
    def axes(self):
        """Property axes.

        Returns
        -------
            axes : :class:`matplotlib.axes.Axes`
                Axes for the figure.
        """

        return self.__axes
    
    @axes.setter
    def axes(self, axes):
        """Setter for axes.

        Parameters
        ----------
            axes : :class:`matplotlib.axes.Axes`
                Axes for the figure.
        """

        self.__axes = axes

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

    @property
    def plot_type(self):
        """Property plot_type.

        Returns
        -------
            plot_type : str
                Type of plot:
                    contour: Contour plot.
                    contourf: Filled contour plot.
                    line: Line plot.
                    lines: Multi-line plot.
                    pcolormesh: Color plot.
                    scatter: Scatter plot.
                    scatters: Multi-scatter plot.
        """

        return self.__plot_type
    
    @plot_type.setter
    def plot_type(self, plot_type):
        """Setter for plot_type.

        Parameters
        ----------
            plot_type : str
                Type of plot:
                    contour: Contour plot.
                    contourf: Filled contour plot.
                    line: Line plot.
                    lines: Multi-line plot.
                    pcolormesh: Color plot.
                    scatter: Scatter plot.
                    scatters: Multi-scatter plot.
        """

        self.__plot_type = plot_type

    @property
    def fonts(self):
        """Property fonts.

        Returns
        -------
            fonts : dict
                Dictionaries of font settings for text and mathematical symbols.
        """

        return self.__fonts
    
    @fonts.setter
    def fonts(self, fonts):
        """Setter for fonts.

        Returns
        -------
            fonts : dict
                Dictionaries of font settings for text and mathematical symbols.
        """

        self.__fonts = fonts

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

    def __init_plot(self, plot_params):
        """Function to initialize plot with given parameters.
        
        Parameters
        ----------
            plot_params : dict
                Parameters for the plot.
        """

        # get axes
        self.axes = plt.gca()
        self.plot_type = plot_params['type']
            
        # font for texts
        if 'font_text' in plot_params:
            _font_text = plot_params['font_text']
        else:
            _font_text = {
                'family': 'Times New Roman',
                'style': 'normal',
                'variant': 'normal',
                'weight': 500,
                'size': 16.0
            }

        # font for mathematical symbols
        if 'font_math' in plot_params:
            _font_math = plot_params['font_math']
        else:
            _font_math = 'cm'
        plt.rcParams['mathtext.fontset'] = _font_math

        # set fonts property
        self.fonts = {
            'text': _font_text,
            'math': _font_math
        }

        # title
        if 'title' in plot_params:
            plt.title(plot_params['title'], fontdict=_font_text)

        # ticks
        plt.xticks(fontfamily=_font_text['family'], fontstyle=_font_text['style'], fontvariant=_font_text['variant'], fontweight=_font_text['weight'], fontsize=12.0)
        plt.yticks(fontfamily=_font_text['family'], fontstyle=_font_text['style'], fontvariant=_font_text['variant'], fontweight=_font_text['weight'], fontsize=12.0)
        plt.ticklabel_format(axis='both', style='plain')

        # labels
        x_label = plot_params['x_label'] if 'x_label' in plot_params else ''
        plt.xlabel(r'' + x_label, fontdict=_font_text)
        y_label = plot_params['y_label'] if 'y_label' in plot_params else ''
        plt.ylabel(r'' + y_label, fontdict=_font_text)
        z_label = plot_params['z_label'] if 'z_label' in plot_params else ''
        self.labels = {
            'x_label': x_label,
            'y_label': y_label,
            'z_label': z_label
        }

        # limits
        if 'x_lim' in plot_params:
            plt.xlim(plot_params['x_lim'][0], plot_params['x_lim'][1])
        if 'y_lim' in plot_params:
            plt.ylim(plot_params['y_lim'][0], plot_params['y_lim'][1])

    def __init_1D(self, xs, num, colors, linestyles=None, sizes=None, legends=None, xticks=None):
        """Function to initialize 1D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.

            num : int
                Number of 1D plots.

            colors : list
                Colors for the plots.

            linestyles : list, optional
                Linestyles for line plots.

            sizes : list, optional
                Marker sizes for scatter plots.

            legends : list, optional
                Legends for the plots.

            xticks : list, optional
                Ticks for the X-axis.
        """

        # update axis
        self.__axes.set_xlim(xs[0], xs[-1])

        # line plots
        if self.__plot_type == 'line' or self.__plot_type == 'lines':
            # plots
            self.plot = [Line2D([], [], color=colors[i], linestyle=linestyles[i]) for i in range(num)]
            self.head = [Line2D([], [], color=colors[i], linestyle=linestyles[i], marker='o') for i in range(num)]

            # axes
            [self.__axes.add_line(self.__plot[i]) for i in range(num)]
            [self.__axes.add_line(self.__head[i]) for i in range(num)]

        # scatter plots
        elif self.__plot_type == 'scatter' or self.__plot_type == 'scatters':
            # plots
            self.plot = [self.__axes.scatter([], [], c=colors[i], s=sizes[i]) for i in range(num)]  

        # legends
        if legends is not None and legends[0] != '':
            l = plt.legend(legends, loc='best')                
            plt.setp(l.texts, 
                fontfamily=self.__fonts['text']['family'], 
                fontstyle=self.__fonts['text']['style'], 
                fontvariant=self.__fonts['text']['variant'], 
                fontweight=self.__fonts['text']['weight'], 
                fontsize=12.0
            )
        
        # ticks
        if xticks is not None:
            plt.xticks(ticks=xticks)

    def __init_2D(self, xs, ys, plot_params, color_grad='br_light', shading='gouraud', cbar=True, xticks=None, yticks=None):
        """Function to initialize 2D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.
                
            ys : list
                Y-axis values.
                
            plot_params : dict
                Parameters for the plot.

            color_grad : str, optional
                Colors for the plot.

            shading : str, optional
                Shading of the plot.

            cbar : bool, optional
                Option to plot colorbar.

            xticks : list, optional
                Ticks for the X-axis.

            yticks : list, optional
                Ticks for the Y-axis.
        """

        # update axes
        self.__axes.set_xlim(xs[0], xs[-1])
        self.__axes.set_ylim(ys[0], ys[-1])

        # color map
        if color_grad == 'br_light':
            cmap = sns.diverging_palette(250, 15, s=75, l=40, n=9, center='light', as_cmap=True)
        if color_grad == 'rb_light':
            cmap = sns.diverging_palette(15, 250, s=75, l=40, n=9, center='light', as_cmap=True)
        if color_grad == 'gr_light':
            cmap = sns.diverging_palette(150, 15, s=75, l=40, n=9, center='light', as_cmap=True)

        # plot axes
        _X, _Y = np.meshgrid(xs, ys)
        _nans = np.zeros((len(ys), len(xs)))
        _nans[:] = np.NaN

        # pcolormesh plot
        if self.__plot_type == 'pcolormesh':
            self.plot = self.__axes.pcolormesh(_X, _Y, _nans, shading=shading, cmap=cmap)

        # pcolormesh plot
        if self.__plot_type == 'contourf':
            self.plot = self.__axes.contourf(_X, _Y, _nans, cmap=cmap)

        # color bar
        if cbar:
            self.cbar = plt.colorbar(self.__plot)
            self.__cbar.set_label(
                label=self.__labels['z_label'], 
                fontfamily=self.__fonts['text']['family'], 
                fontstyle=self.__fonts['text']['style'], 
                fontvariant=self.__fonts['text']['variant'], 
                fontweight=self.__fonts['text']['weight'], 
                fontsize=self.__fonts['text']['size']
            )
            plt.setp(
                self.__cbar.ax.get_yticklabels(), 
                fontfamily=self.__fonts['text']['family'], 
                fontstyle=self.__fonts['text']['style'], 
                fontvariant=self.__fonts['text']['variant'], 
                fontweight=self.__fonts['text']['weight'], 
                fontsize=12.0
            )
        
        # axis ticks
        if xticks is not None:
            plt.xticks(ticks=xticks)
        if yticks is not None:
            plt.yticks(ticks=yticks)

    def update(self, X=None, Y=None, Z=None, head=True, hold=False):
        """Function to update plot.
        
        Parameters
        ----------
            X : list, optional
                X-axis data.
                
            Y : list, optional
                Y-axis data.
                
            Z : list, optional
                Z-axis data.

            head : boolean, optional
                Option to display the head for line-type plots.

            hold : boolean, optional
                Option to hold the plot.
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

        # draw data
        plt.draw()

        # display plot
        if hold:
            logger.info('------------------------------Figure Updated---------------------\t\n')
            plt.show()
        else:
            plt.pause(1e-9)

    def __update_1D(self, xs, ys, dim=None, head=False):
        """Function to udpate 1D plots.
        
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
        """Function to udpate 2D plots.
        
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