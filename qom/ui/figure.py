#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to plot figures."""

__name__    = 'qom.ui.Figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2020-12-02'

# dependencies
import logging

# dev dependencies
from qom.ui.plotters import *

# module logger
logger = logging.getLogger(__name__)

class Figure():
    """Class to plot figures.
    
    Properties
    ----------
        plotter : :class:`qom.ui.plotters.*`
            Plotter class. 
    """

    @property
    def plotter(self):
        """Property plotter.

        Returns
        -------
            plotter : :class:`qom.ui.plotters.*`
                Plotter class.
        """

        return self.__plotter
    
    @plotter.setter
    def plotter(self, plotter):
        """Setter for plotter.

        Parameters
        ----------
            plotter : :class:`qom.ui.plotters.*`
                Plotter class.
        """

        self.__plotter = plotter

    def __init__(self, plot_params, X, Y={}, Z={}):
        """Class constructor for Figure.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            X : :class:`qom.ui.axes.*`
                X-axis data.

            Y : :class:`qom.ui.axes.*`, optional
                Y-axis data.

            Z : :class:`qom.ui.axes.*`, optional
                Z-axis data.
        """
        
        # initialize plot
        Axes = {
            'X': X,
            'Y': Y,
            'Z': Z
        }
        
        # matplotlib plotter
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