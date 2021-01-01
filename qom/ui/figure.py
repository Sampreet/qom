#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to plot figures."""

__name__    = 'qom.ui.Figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2021-01-01'

# dependencies
from typing import Union
import logging

# dev dependencies
from qom.ui.axes import *
from qom.ui.plotters import *

# module logger
logger = logging.getLogger(__name__)

# data types
t_axis = Union[list, DynamicAxis, StaticAxis, MultiAxis]

class Figure():
    """Class to plot figures.
        
    Parameters
    ----------
    plot_params : dict
        Parameters of the plot.
    X : list or :class:`qom.ui.axes.*`
        X-axis data.
    Y : list or :class:`qom.ui.axes.*`, optional
        Y-axis data.
    Z : :class:`qom.ui.axes.*`, optional
        Z-axis data.
    """

    @property
    def plotter(self):
        """:class:`qom.ui.plotters.*`: Plotter class."""

        return self.__plotter
    
    @plotter.setter
    def plotter(self, plotter):
        self.__plotter = plotter

    def __init__(self, plot_params, X: t_axis, Y: t_axis=list(), Z: t_axis=list(), plotter_type='mpl'):
        """Class constructor for Figure."""
        
        # initialize plot
        Axes = {
            'X': X,
            'Y': Y,
            'Z': Z
        }
        
        # matplotlib plotter
        if plotter_type == 'mpl':
            self.plotter = MPLPlotter(plot_params, Axes) 

        # display initialization
        logger.info('----------------------------Figure Initialized-------------------\t\n')

    def update(self, xs=None, ys=None, zs=None, head=False, hold=True):
        """Function to update plot.
        
        Parameters
        ----------
        xs : list or numpy.ndarray, optional
            X-axis data.
        ys : list or numpy.ndarray, optional
            Y-axis data.
        zs : list or numpy.ndarray, optional
            Z-axis data.
        head : boolean, optional
            Option to display the head for line-type plots. Default is False.
        hold : boolean, optional
            Option to hold the plot. Default is True.
        """

        # update plot
        self.__plotter.update(xs, ys, zs, head)
            
        # update log
        logger.info('------------------------------Figure Updated---------------------\t\n')

        # show plot
        self.__plotter.show(hold)