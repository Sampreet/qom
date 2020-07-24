#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules to display matplotlib plots."""

__name__    = 'qom.ui.figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2020-07-24'

# dependencies
from matplotlib.lines import Line2D
import logging
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# module logger
logger = logging.getLogger(__name__)

class Plotter2D():
    """Class containing various 2D plot scenarios.

    Attibutes
    ---------
    axes : :class:`matplotlib.axes.Axes`
        Axes for the figure.

    cbar : :class:`matplotlib.colorbar.Colorbar`
        Colorbar for 2D color figures.

    head : :class:`matplotlib.lines.Line2D`
        Line to indicate the point of processing.

    plot : :class:`matplotlib.*`
        Variable plot classes depending on the type of figure.

    x_steps : int
        Number of steps in x-axis.

    y_steps : int
        Number of steps in y-axis.

    z_steps : int
        Number of steps in z-axis.

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

    # class attributes
    axes = None
    cbar = None
    head = None
    plot = None
    x_steps = 0
    y_steps = 0
    z_steps = 0
    plot_type = 'line'

    def __init__(self, plot_params, X=[], Y=[], Z=[]):
        """Class constructor for Plotter.
        
        Parameters
        ----------
        plot_params : list
            Parameters of the plot.
            
        X : list
            X-axis data.
            
        Y : list
            Y-axis data.
            
        Z : list
            Z-axis data.
        """
        
        # initialize plot
        plt.show()
        self.axes = plt.gca()
        self.axes.set_xlim(min(X), max(X))

        self.x_steps = len(X)

        # plot type
        self.plot_type = plot_params['type']

        # if line plot
        if self.plot_type == 'line':
            self.plot = Line2D([], [], color=plot_params['color'], linestyle=plot_params['linestyle'])
            self.head = Line2D([], [], color=plot_params['color'], linestyle=plot_params['linestyle'], marker='o')
            self.axes.add_line(self.plot)
            self.axes.add_line(self.head)

        # if multi-line plot
        if self.plot_type == 'lines':
            self.plot = [Line2D([], [], color=plot_params['colors'][i], linestyle=plot_params['linestyles'][i]) for i in range(len(Z))]
            self.head = [Line2D([], [], color=plot_params['colors'][i], linestyle=plot_params['linestyles'][i], marker='o') for i in range(len(Z))]
            [self.axes.add_line(self.plot[i]) for i in range(len(Z))]
            [self.axes.add_line(self.head[i]) for i in range(len(Z))]

        # if scatter plot
        if self.plot_type == 'scatter':
            self.plot = self.axes.scatter([], [], s=plot_params['size'], c=plot_params['color'])

        # TODO: handle multi-scatter
            
        # if pcolormesh plot
        if self.plot_type == 'pcolormesh':
            self.axes.set_ylim(min(Y), max(Y))

            X, Y = np.meshgrid(X, Y)
            # blue red
            cmap = sns.diverging_palette(250, 15, s=75, l=40, n=9, center='light', as_cmap=True)
            # # red blue
            # cmap = sns.diverging_palette(15, 250, s=75, l=40, n=9, center='light', as_cmap=True)
            # green red
            cmap = sns.diverging_palette(150, 15, s=75, l=40, n=9, center='light', as_cmap=True)
            self.plot = self.axes.pcolormesh(X, Y, Z, shading='gouraud', cmap=cmap)
            self.cbar = plt.colorbar(self.plot)

        # TODO: handle contour plots

        # values
        self.X = X
        self.Y = Y
        self.Z = Z

        # setup plot
        self.set_params(plot_params)

    def set_params(self, plot_params):
        """Function to set plot parameters.
        
        Parameters
        ----------
        plot_params : list
            Parameters of the plot.
        """

        # font sizes
        plt.rcParams.update({'font.size': 12})
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        # legends
        if 'legend' in plot_params:
            if type(plot_params['legend']) == list:
                plot_params['legend'] = [r'$' + ele + '$' for ele in plot_params['legend']]
            else:
                plot_params['legend'] = [r'$' + plot_params['legend'] + '$']
            plt.legend(plot_params['legend'], loc='best')

        # title
        if 'title' in plot_params:
            plt.title(plot_params['title'])

        # labels
        if 'x_label' in plot_params:
            plt.xlabel(r'$' + plot_params['x_label'] + '$', fontsize=16)
        if 'y_label' in plot_params:
            plt.ylabel(r'$' + plot_params['y_label'] + '$', fontsize=16)

        # limits
        if 'x_lim' in plot_params:
            plt.xlim(plot_params['x_lim'][0], plot_params['x_lim'][1])
        if 'y_lim' in plot_params:
            plt.ylim(plot_params['y_lim'][0], plot_params['y_lim'][1])

        # ticks
        plt.ticklabel_format(axis='both', style='plain')

    def update(self, X=[], Y=[], Z=[], head=True, hold=False):
        """Function to update plot.
        
        Parameters
        ----------
        X : list
            X-axis data.
            
        Y : list
            Y-axis data.
            
        Z : list
            Z-axis data.

        head : boolean
            Option to display the head for line-type plots.

        hold : boolean
            Option to hold the plot.
        """

        if self.plot_type == 'line':
            # update data 
            self.plot.set_xdata(X)
            self.plot.set_ydata(Y)
            if head:
                self.head.set_xdata(X[-1:])
                self.head.set_ydata(Y[-1:])
            else:
                self.head.set_xdata([])
                self.head.set_ydata([])

            # scale down nan or inf values for limits
            Y = [y if y == y else 0 for y in Y]
            self.axes.set_ylim(min(Y), max(Y))

        if self.plot_type == 'lines':
            # scale down nan or inf values for limits
            temp = [y if y == y else 0 for y in Y]
            self.axes.set_ylim(min(temp), max(temp))

            i = 0
            while len(X) >= self.x_steps:
                # update data 
                self.plot[i].set_xdata(X[0:self.x_steps])
                self.plot[i].set_ydata(Y[0:self.x_steps])

                # reduce data 
                X = X[self.x_steps:]
                Y = Y[self.x_steps:]

                # update plot numer
                i+= 1
            
            if len(X) != 0:
                # update data 
                self.plot[i].set_xdata(X)
                self.plot[i].set_ydata(Y)

                if head:
                    self.head[i].set_xdata(X[-1:])
                    self.head[i].set_ydata(Y[-1:])
                else:
                    self.head[i].set_xdata([])
                    self.head[i].set_ydata([])

            elif i > 0:
                self.head[i-1].set_xdata([])
                self.head[i-1].set_ydata([])

        if self.plot_type == 'scatter':
            # update data
            XY = np.c_[X, Y]
            self.plot.set_offsets(XY)

            # scale down nan or inf values for limits
            Y = [y if y == y else 0 for y in Y]
            self.axes.set_ylim(min(Y), max(Y))
        
        if self.plot_type == 'pcolormesh':
            Z = Z.ravel()
            self.plot.set_array(Z)
            
            # scale down nan or inf values for limits
            Z = [z if z == z else 0 for z in Z]
            self.plot.set_clim(vmin=min(Z), vmax=max(Z))
            self.cbar.set_ticks(np.linspace(min(Z), max(Z), 11))
            self.cbar.ax.set_autoscale_on(True)
            self.cbar.draw_all()

        # draw data
        plt.draw()

        # display plot
        if hold:
            plt.show()
        else:
            plt.pause(1e-9)
