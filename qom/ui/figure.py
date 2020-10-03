#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to display figures."""

__name__    = 'qom.ui.figure'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-16'
__updated__ = '2020-10-03'

# dependencies
import logging

# dev dependencies
from qom.ui.plotters import PlotterMPL

# module logger
logger = logging.getLogger(__name__)

# TODO: Add platform-based features.

class Plotter():
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

    def __init__(self, plot_params, X, Y=None, Z=None):
        """Class constructor for Plotter.
        
        Parameters
        ----------
            plot_params : dict
                Parameters of the plot.

            X : :class:`qom.utils.axis.StaticAxis`
                X-axis data.

            Y : :class:`qom.utils.axis.StaticAxis`, optional
                Y-axis data.

            Z : :class:`qom.utils.axis.StaticAxis`, optional
                Z-axis data.
        """
        
        # initialize plot
        Axes = {
            'X': X,
            'Y': Y,
            'Z': Z
        }
        
        # matplotlib plotter
        self.plotter = PlotterMPL(plot_params, Axes) 

        # display initialization
        logger.info('----------------------------Figure Initialized-------------------\t\n')

    def update(self, X=None, Y=None, Z=None, head=False, hold=True):
        """Function to update plot.
        
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

            hold : boolean, optional
                Option to hold the plot. Default is True.
        """

        # update plot
        self.__plotter.update(X, Y, Z, head)
            
        # update log
        logger.info('------------------------------Figure Updated---------------------\t\n')

        # show plot
        self.__plotter.show(hold)