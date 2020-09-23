#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules to display matplotlib plots."""

__name__    = 'qom.ui.figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2020-09-23'

# dependencies
from matplotlib.lines import Line2D
import logging
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# module logger
logger = logging.getLogger(__name__)

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
    """

    # TODO: handle contour, contourf plots.
    # TODO: validate multi-scatter plots.

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
        
        # initialize
        plt.show()
        self.axes = plt.gca()
        self.plot_type = plot_params['type']
            
        # single-line plot
        if self.__plot_type == 'line':
            self.__init_1D(X.values, 1, [plot_params['color']], linestyles=[plot_params['linestyle']], legends=[plot_params['legend']])
        # multi-line plot
        elif self.__plot_type == 'lines':
            self.__init_1D(X.values, len(Z.legends), Z.colors, linestyles=Z.linestyles, legends=Z.legends)
        # scatter plot
        elif self.__plot_type == 'scatter':
            self.__init_1D(X.values, 1, [plot_params['color']], sizes=[plot_params['size']], legends=[plot_params['legend']])
        # multi-scatter plot
        elif self.__plot_type == 'scatters':
            self.__init_1D(X.values, len(Z.legends), Z.colors, sizes=Z.sizes, legends=Z.legends)

        # pcolormesh plot
        elif self.plot_type == 'pcolormesh':
            self.__init_2D(X.values, Y.values)

        # setup plot
        self.__init_params(plot_params)

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

    def __init_1D(self, xs, num, colors, linestyles=None, sizes=None, legends=None):
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
        if legends and legends[0] != '':
            plt.legend(legends, loc='best')

    def __init_2D(self, xs, ys, color_grad='br_light', shading='gouraud', cbar=True):
        """Function to initialize 2D plots.
        
        Parameters
        ----------
            xs : list
                X-axis values.
                
            ys : list
                Y-axis values.

            color_grad : str, optional
                Colors for the plot.

            shading : str, optional
                Shading of the plot.

            cbar : bool, optional
                Option to plot colorbar.
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

        # color bar
        if cbar:
            self.cbar = plt.colorbar(self.__plot)

    def __init_params(self, plot_params):
        """Function to initialize plot with given parameters.
        
        Parameters
        ----------
            plot_params : dict
                Parameters for the plot.
        """

        # font sizes
        plt.rcParams.update({'font.size': 12})
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        # title
        if 'title' in plot_params:
            plt.title(plot_params['title'])

        # labels
        if 'x_label' in plot_params:
            plt.xlabel(r'' + plot_params['x_label'], fontsize=16)
        if 'y_label' in plot_params:
            plt.ylabel(r'' + plot_params['y_label'], fontsize=16)

        # limits
        if 'x_lim' in plot_params:
            plt.xlim(plot_params['x_lim'][0], plot_params['x_lim'][1])
        if 'y_lim' in plot_params:
            plt.ylim(plot_params['y_lim'][0], plot_params['y_lim'][1])

        # ticks
        plt.ticklabel_format(axis='both', style='plain')

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
        elif self.__plot_type == 'pcolormesh':
            self.__update_2D(Z)

        # draw data
        plt.draw()

        # display plot
        if hold:
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
        minis = []
        maxis = []
        for j in range(len(ys)):
            # calculate minimum and maximum values
            if len(ys[j]) != 0:
                # handle NaN values
                _no_nan = [y if y == y else 0 for y in ys[j]]
                minis.append(min(_no_nan))
                maxis.append(max(_no_nan))
        self.__axes.set_ylim(min(minis), max(maxis))

    def __update_2D(self, Z):
        """Function to udpate 2D plots.
        
        Parameters
        ----------
            Z : :class:`qom.utils.axis.StaticAxis` or :class:`qom.utils.axis.DynamicAxis`
                Z-axis data.
        """
        
        # update pcolormesh plot
        rave = np.ravel(Z.values)
        self.__plot.set_array(rave)

        # handle NaN values
        _no_nan = [z if z == z else 0 for z in rave]
        self.__plot.set_clim(vmin=min(_no_nan), vmax=max(_no_nan))

        # color bar
        self.__cbar.set_ticks(np.linspace(min(_no_nan), max(_no_nan), 11))
        self.__cbar.ax.set_autoscale_on(True)
        self.__cbar.draw_all()