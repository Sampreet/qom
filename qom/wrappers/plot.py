#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules to display matplotlib plots."""

__name__    = 'qom.wrappers.plot'
__authors__ = ['Sampreet Kalita']
__created__ = '2019-11-22'
__updated__ = '2020-06-15'

# dependencies
import logging
import matplotlib.pyplot as mp
from matplotlib.colors import LinearSegmentedColormap
from numpy import array, meshgrid

# module logger
logger = logging.getLogger(__name__)

def contourf(X, Y, Z, plot_params):
    """Function for contourf plot.
    
    Parameters
    ----------
    X : list
        Lists of points in x-axis.
    Y : list
        Lists of points in y-axis.
    Z : list
        Lists of points in z-axis.
    plot_params : list
        Parameters of the plot.
    """

    # create mesh
    X, Y = meshgrid(X, Y)

    cmap = 'RdBu_r'
    # check colormap
    if 'cmap' in plot_params:
        cmap_params = plot_params['cmap']
        n_bins = 101
        if 'n_bins' in cmap_params:
            n_bins = int(cmap_params['n_bins'])
        colors = [(1, 1, 1), (0, 0, 0)]
        if 'colors' in cmap_params:
            colors = int(cmap_params['colors'])
        cmap = LinearSegmentedColormap.from_list('custom', colors, n_bins)

    # plot 
    mp.contourf(X, Y, Z, cmap=cmap, alpha=0.75)

    # display color bar
    mp.colorbar()

    # set parameters
    set_params(plot_params)

    # display plot
    mp.show()

def set_params(plot_params):
    """Function to update plot parameters.
    
    Parameters
    ----------
    plot_params : list
        Parameters of the plot.
    """

    # default font sizes
    mp.rcParams.update({'font.size': 12})
    mp.xticks(fontsize=12)
    mp.yticks(fontsize=12)

    # legends
    if 'legend' in plot_params:
        if type(plot_params['legend']) == list:
            plot_params['legend'] = [r'$' + ele + '$' for ele in plot_params['legend']]
        else:
            plot_params['legend'] = [r'$' + plot_params['legend'] + '$']
        mp.legend(plot_params['legend'], loc='best')

    # title
    if 'title' in plot_params:
        mp.title(plot_params['title'])

    # labels
    if 'x_label' in plot_params:
        mp.xlabel(r'$' + plot_params['x_label'] + '$', fontsize=16)
    if 'y_label' in plot_params:
        mp.ylabel(r'$' + plot_params['y_label'] + '$', fontsize=16)

    # limits
    if 'x_lim' in plot_params:
        mp.xlim(plot_params['x_lim'][0], plot_params['x_lim'][1])
    if 'y_lim' in plot_params:
        mp.ylim(plot_params['y_lim'][0], plot_params['y_lim'][1])

    # ticks
    mp.ticklabel_format(axis='both', style='plain')

def line(X, Y, plot_params):
    """Function for single line plot.
    
    Parameters
    ----------
    X : list
        List of points in x-axis.
    Y : list
        List of points in y-axis.
    plot_params : list
        Parameters of the plot.
    """

    # plot line
    line = mp.plot(X, Y)

    # set color
    if 'color' in plot_params:
        mp.setp(line, color=plot_params['color'])

    # set linestyle
    if 'linestyle' in plot_params:
        mp.setp(line, linestyle=plot_params['linestyle'])

    # set parameters
    set_params(plot_params)

    # display plot
    mp.show()

def lines(X, Y, plot_params):
    """Function for multiple line plots.
    
    Parameters
    ----------
    X : list
        Lists of points in x-axis.
    Y : list
        Lists of points in y-axis.
    plot_params : list
        Parameters of the plot.
    """

    # plot each line
    for i in range(len(Y)):
        # plot line
        line = mp.plot(X[i], Y[i])

        # set color
        if 'color' in plot_params:
            mp.setp(line, color=plot_params['color'][i])

        # set linestyle
        if 'linestyle' in plot_params:
            mp.setp(line, linestyle=plot_params['linestyle'][i])

    # set parameters
    set_params(plot_params)

    # display plot
    mp.show()

def pcolormesh(X, Y, Z, plot_params):
    """Function for pcolormesh plot.
    
    Parameters
    ----------
    X : list
        Lists of points in x-axis.
    Y : list
        Lists of points in y-axis.
    Z : list
        Lists of points in z-axis.
    plot_params : list
        Parameters of the plot.
    """

    # create mesh
    X, Y = meshgrid(X, Y)

    cmap = 'RdBu_r'
    # check colormap
    if 'cmap' in plot_params:
        cmap = plot_params['cmap']

    # plot color
    mp.pcolormesh(X, Y, Z, cmap=cmap, alpha=0.75)

    # display color bar
    mp.colorbar()

    # set parameters
    set_params(plot_params)

    # display plot
    mp.show()

def scatter(X, Y, plot_params):
    """Function for scatter plot.
    
    Parameters
    ----------
    X : list
        Lists of points in x-axis.
    Y : list
        Lists of points in y-axis.
    plot_params : list
        Parameters of the plot.
    """

    # plot line
    scatter = mp.scatter(X, Y)

    # set color
    if 'color' in plot_params:
        mp.setp(scatter, color=plot_params['color'])

    # set linestyle
    if 'linestyle' in plot_params:
        mp.setp(scatter, linestyle=plot_params['linestyle'])

    # set parameters
    set_params(plot_params)

    # display plot
    mp.show()
    
