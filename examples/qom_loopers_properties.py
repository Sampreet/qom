#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Example script to plot properties."""

__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-27'
__updated__ = '2020-09-27'

# dependencies
import os 
import sys

# add path to local library
sys.path.append(os.path.abspath(os.path.join('..', 'qom')))

# dev dependencies
from qom.loopers import properties

# demo class
class Model:
    """Class containing the model.

    Attributes
    ----------
        name : str
            Name of the model
        
        code : str
            Short code for the model

        params : dict
            Base parameters for the model.
    """
    
    # demo attributes
    name = 'My Model Class'
    code = 'mmc'
    params = {
        'x': 2.0
    }

    # demo property function
    def square(self):
        """Function to obtain square value.
            
        Returns
        -------
            y : float
                Square of the parameter.
        """

        return self.params['x']**2

# data for modules
script_data = {
    # property parameters
    'prop_params': {
        # function in the library
        'func': 'properties_1D',
        # function in the model
        'code': 'square',
        # name of the function
        'name': 'Square',
        # variable in the x-axis
        'X': {
            'var': 'x',
            'min': -5,
            'max': 5,
            'steps': 1001
        }
    },
    # option to show plot
    'plot': True,
    # plot parameters
    'plot_params': {
        # option to show progress on plot
        'progress': True, 
        # plot title
        'title': 'Square Function',
        # axis labels
        'x_label': '$x$',
        'y_label': '$x^{2}$',
        # line plot
        'type': 'line'
    }
}

# calculate properties
properties.calculate(Model(), script_data)