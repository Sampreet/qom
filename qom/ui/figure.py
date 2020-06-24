#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules to display matplotlib plots."""

__name__    = 'qom.ui.figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2020-06-24'

# dependencies
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from numpy import array, c_, empty, linspace, meshgrid, NaN, sin

# module logger
logger = logging.getLogger(__name__)

class Plotter2D():

    axes = None
    plot = None
    head = None
    cbar = None
    plot_type = 'line'

    def __init__(self, plot_type, plot_params, X=[], Y=[], Z=[]):
        """Class constructor for Plotter"""
        
        # initialize plot
        plt.show()
        self.axes = plt.gca()
        self.axes.set_xlim(plot_params['X']['min'], plot_params['X']['max'])

        # plot type
        self.plot_type = plot_type
        # if line plot
        if plot_type == 'line':
            self.plot = Line2D([], [], color=plot_params['color'], linestyle=plot_params['linestyle'])
            self.head = Line2D([], [], color=plot_params['color'], linestyle=plot_params['linestyle'], marker='o')
            self.axes.add_line(self.plot)
            self.axes.add_line(self.head)

        # if scatter plot
        if plot_type == 'scatter':
            self.plot = self.axes.scatter([], [], s=plot_params['size'], c=plot_params['color'])
            
        # if line plot
        if plot_type == 'pcolormesh':
            self.axes.set_ylim(plot_params['Y']['min'], plot_params['Y']['max'])

            X, Y = meshgrid(X, Y)
            # blue red
            cmap = sns.diverging_palette(250, 15, s=75, l=40, n=9, center='dark', as_cmap=True)
            # red blue
            cmap = sns.diverging_palette(15, 250, s=75, l=40, n=9, center='dark', as_cmap=True)
            # # green red
            # cmap = sns.diverging_palette(150, 15, s=75, l=40, n=9, center='dark', as_cmap=True)
            self.plot = self.axes.pcolormesh(X, Y, Z, shading='gouraud', cmap=cmap)
            self.cbar = plt.colorbar(self.plot)

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

        if self.plot_type == 'scatter':
            # update data
            XY = c_[X, Y]
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
            self.cbar.set_ticks(linspace(min(Z), max(Z), 11))
            self.cbar.ax.set_autoscale_on(True)
            self.cbar.draw_all()

        # draw data
        plt.draw()

        # display plot
        if hold:
            plt.show()
        else:
            plt.pause(1e-6)
