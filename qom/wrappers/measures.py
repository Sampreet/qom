#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for measures."""

__name__    = 'qom.wrappers.measures'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-19'
__updated__ = '2020-06-24'

# dependencies
import logging
import os
from numpy import around, ceil, empty, linspace, log10, NaN

# dev dependencies
from qom.ui import figure
from qom.wrappers import dynamics

# module logger
logger = logging.getLogger(__name__)

def measure_1D(model, measure_code, measure_data, thres_mode='max_min', solver_type='complex', cache=True, dir_name='data', plot=True, plot_type='line'):
    """Function to calculate a measure versus a continuous variable.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    measure_code : str
        Short code for the measure.
    
    measure_data : dict
        Data for the calculation of measure.

    thres_mode: str
        Mode of calculation of the threshold values:
            max_min: Minimum value of variable for which measure attains maximum value.
            max_max: Maximum value of variable for which measure attains maximum value.

    solver_type : str
        Type of solver ('real' or 'complex').

    cache : boolean
        Option to cache data.

    dir_name: str
        Directory name to cache data.

    plot: boolean
        Option to plot the measure dynamics.

    plot_type: str
        Option for type of plot:
            line: Line plot.
            scatter: Scatter plot.

    Returns
    -------
    X : list
        Values of the first variable at which the measure is calculated.

    M : list
        Measures calculated.

    Thres: dict
        Threshold values of the variables calculated.
    """

    # extract frequently used variables
    plot_params = measure_data['figure']['1D']
    x_name = plot_params['X']['name']
    x_min = plot_params['X']['min']
    x_max = plot_params['X']['max']
    x_steps = plot_params['X']['steps']

    # display initialization
    logger.info('Initializing average {measure_name} calculation\n'.format(measure_name=measure_data['name']))

    # initialize variable
    num_decimals = int(ceil(log10((x_steps - 1) / (x_max - x_min))))
    X = around(linspace(x_min, x_max, x_steps), num_decimals)

    # initialize threshold values
    Thres = {}
    Thres[x_name] = x_min - 1

    # threshold measures
    if thres_mode.index('max_') != -1:
        # maximum value of measure
        m_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_type, plot_params, X=X)

    # initialize list
    M = []
    # for each variable value, calculate the measure
    for i in range(len(X)):
        # calculate progress
        progress = float(i) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model
        model.p[x_name] = X[i]

        # get measure dynamics
        _, temp = dynamics.measure(model, measure_code, measure_data)
        # calculate average value
        m = sum(temp[-100:-1])/100

        # update threshold
        if thres_mode == 'max_min':
            if m > m_max:
                m_max = m
                Thres[x_name] = X[i]
    
        # update list
        M.append(m)

        # update plot
        if plot:
            plotter.update(X[0:i + 1], M)
        
    # display completion
    logger.info('-----------------Average Values Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(X, M, head=False, hold=True)

    # values of the measure
    return X, M, Thres

def measure_2D(model, measure_code, measure_data, solver_type='complex', cache=True, dir_name='data', thres_mode='max_min', plot=True, plot_type='pcolormesh'):
    """Function to calculate a measure versus a continuous variable.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    measure_code : str
        Short code for the measure.
    
    measure_data : dict
        Data for the calculation of measure.

    thres_mode: str
        Mode of calculation of the threshold values:
            max_min: Minimum value of variable for which measure attains maximum value.
            max_max: Maximum value of variable for which measure attains maximum value.

    solver_type : str
        Type of solver ('real' or 'complex').

    cache : boolean
        Option to cache data.

    dir_name: str
        Directory name to cache data.

    plot: boolean
        Option to plot the measure dynamics.

    plot_type: str
        Option for type of plot:
            pcolormesh: Pcolormesh plot.

    Returns
    -------
    X : list
        Values of the first variable at which the measure is calculated.

    Y : list
        Values of the second variable at which the proprety is calculated.

    M : list
        Measures calculated.

    Thres: dict
        Threshold values of the variables calculated.
    """

    # extract frequently used variables
    plot_params = measure_data['figure']['2D']
    x_name = plot_params['X']['name']
    x_min = plot_params['X']['min']
    x_max = plot_params['X']['max']
    x_steps = plot_params['X']['steps']
    y_name = plot_params['Y']['name']
    y_min = plot_params['Y']['min']
    y_max = plot_params['Y']['max']
    y_steps = plot_params['Y']['steps']

    # display initialization
    logger.info('Initializing average {measure_name} calculation\n'.format(measure_name=measure_data['name']))

    # initialize variable
    num_decimals = int(ceil(log10((x_steps - 1) / (x_max - x_min))))
    X = around(linspace(x_min, x_max, x_steps), num_decimals)
    num_decimals = int(ceil(log10((y_steps - 1) / (y_max - y_min))))
    Y = around(linspace(y_min, y_max, y_steps), num_decimals)

    # initialize threshold values
    Thres = {}
    Thres[x_name] = x_min - 1
    Thres[y_name] = y_min - 1

    # threshold values
    if thres_mode.index('max_') != -1:
        # max value of measure
        m_max = 0

    # initialize list
    M = empty((len(Y), len(X)))
    M[:] = NaN

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_type, plot_params, X=X, Y=Y, Z=M)

    # for each variable value, calculate the measure
    for j in range(len(Y)):
        # calculate progress
        progress = float(j) / float(len(Y)) * 100
        # display progress
        logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

        for i in range(len(X)):

            # update model
            model.p[x_name] = X[i]
            model.p[y_name] = Y[j]

            # get measure dynamics
            _, temp = dynamics.measure(model, measure_code, measure_data)
            # calculate average value
            m = sum(temp[-100:-1])/100

            # update threshold
            if thres_mode == 'max_min':
                if m > m_max:
                    m_max = m
                    Thres[x_name] = X[i]
                    Thres[y_name] = Y[j]
        
            # update list
            M[j][i] = m

            # update plot
            if plot:
                plotter.update(Z=M)
        
    # display completion
    logger.info('-----------------Average Values Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(Z=M, head=False, hold=True)

    # values of the measure
    return X, M, Thres