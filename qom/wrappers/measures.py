#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for measures."""

__name__    = 'qom.wrappers.measures'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-19'
__updated__ = '2020-08-24'

# dependencies
import logging
import numpy as np
import os

# dev dependencies
from qom.ui import figure
from qom.wrappers import dynamics

# module logger
logger = logging.getLogger(__name__)

def calculate(model, data):
    """Wrapper function to switch functions for calculation of measures.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    data : dict
        Data for the calculation.

    Returns
    -------
    data : list
        Data of the measures calculated.
    """

    # get properties
    return globals()[data['meas_params']['func']](model, data['dyna_params'], data['meas_params'], data['plot'], data['plot_params'])

def measures_1D(model, dyna_params, meas_params, plot=False, plot_params=None):
    """Function to calculate measures versus a continuous variable.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.
    
    dyna_params : dict
        Parameters for the dynamics.
    
    meas_params : dict
        Parameters for the measures.

    plot : boolean
        Option to plot the measures.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    M : list
        Measures calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: verify presence of parametes

    # extract frequently used variables
    avg_mode    = meas_params['avg_mode']
    avg_type    = meas_params['avg_type']
    thres_mode  = meas_params['thres_mode']
    x_name      = meas_params['X']['name']
    x_min       = meas_params['X']['min']
    x_max       = meas_params['X']['max']
    x_steps     = meas_params['X']['steps']

    # initialize variables
    num_decimals = int(np.ceil(np.log10((x_steps - 1) / (x_max - x_min))))
    X = np.around(np.linspace(x_min, x_max, x_steps), num_decimals).tolist()
    X_m = []
    M = []
    m_max = 0
    Thres = {}
    Thres[x_name] = x_min - 1

    # threshold values
    if thres_mode.find('max_') != -1:
        # max value of measure
        m_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in X
    for i in range(len(X)):
        # calculate progress
        progress = float(i) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model
        model.p[x_name] = X[i]

        # get measure dynamics
        D, _, _ = dynamics.dynamics_measure(model, dyna_params, meas_params)

        # initialize value
        m = 0

        # calculate average value
        if avg_mode == 'all':
            m = np.mean(D)
        elif avg_mode == 'end' and avg_type == 'min_max':
            arr = D[-meas_params['span']:]
            m = (max(arr) + min(arr)) / 2
        elif avg_mode == 'range' and avg_type == 'min_max':
            arr = D[meas_params['start']:meas_params['stop']]
            m = (max(arr) + min(arr)) / 2
        elif avg_mode == 'end' and avg_type == 'mean':
            arr = D[-meas_params['span']:]
            m = np.mean(arr)
        elif avg_mode == 'range' and avg_type == 'mean':
            arr = D[meas_params['start']:meas_params['stop']]
            m = np.mean(arr)

        # update threshold
        if thres_mode == 'max_min' and m != 0 and m > m_max:
            m_max           = m
            Thres['value']  = m_max
            Thres[x_name]   = X[i]
        if thres_mode == 'max_max' and m != 0 and m >= m_max:
            m_max           = m
            Thres['value']  = m_max
            Thres[x_name]   = X[i]
    
        # update list
        X_m.append(X[i])
        M.append(m)

        # update plot
        if plot:
            plotter.update(X_m, M)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(X_m, M, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = []
    Axes['z'] = []

    # return data
    return M, Thres, Axes

def measures_2D(model, dyna_params, meas_params, plot, plot_params):
    """Function to calculate measures versus two continuous variables.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.
    
    dyna_params : dict
        Parameters for the dynamics.
    
    meas_params : dict
        Parameters for the measures.

    plot : boolean
        Option to plot the measures.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    M : list
        Measures calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: verify presence of parametes

    # extract frequently used variables
    avg_mode    = meas_params['avg_mode']
    avg_type    = meas_params['avg_type']
    thres_mode  = meas_params['thres_mode']
    x_name      = meas_params['X']['name']
    x_min       = meas_params['X']['min']
    x_max       = meas_params['X']['max']
    x_steps     = meas_params['X']['steps']
    y_name      = meas_params['Y']['name']
    y_min       = meas_params['Y']['min']
    y_max       = meas_params['Y']['max']
    y_steps     = meas_params['Y']['steps']

    # initialize variables
    num_decimals = int(np.ceil(np.log10((x_steps - 1) / (x_max - x_min))))
    X = np.around(np.linspace(x_min, x_max, x_steps), num_decimals).tolist()
    num_decimals = int(np.ceil(np.log10((y_steps - 1) / (y_max - y_min))))
    Y = np.around(np.linspace(y_min, y_max, y_steps), num_decimals).tolist()
    M = np.empty((len(Y), len(X)))
    M[:] = np.NaN
    m_max = 0
    Thres = {}
    Thres[x_name] = x_min - 1
    Thres[y_name] = y_min - 1

    # threshold values
    if thres_mode.find('max_') != -1:
        # max value of measure
        m_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X, Y=Y, Z=M)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in Y
    for j in range(len(Y)):
        # for variation in X
        for i in range(len(X)):
            # calculate progress
            progress = ((float(j) + float(i) / float(len(X))) / float(len(Y))) * 100
            # display progress
            logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.p[x_name] = X[i]
            model.p[y_name] = Y[j]

            # get measure dynamics
            D, _, _ = dynamics.dynamics_measure(model, dyna_params, meas_params)

            # initialize value
            m = 0

            # calculate average value
            if avg_mode == 'all':
                m = sum(D) / len(D)
            elif avg_mode == 'end' and avg_type == 'min_max':
                arr = D[-meas_params['span']:-1]
                m = (max(arr) + min(arr)) / 2
            elif avg_mode == 'range' and avg_type == 'min_max':
                arr = D[meas_params['start']:meas_params['stop']]
                m = (max(arr) + min(arr)) / 2
            elif avg_mode == 'end' and avg_type == 'mean':
                arr = D[-meas_params['span']:-1]
                m = sum(arr) / len(arr)
            elif avg_mode == 'range' and avg_type == 'mean':
                arr = D[meas_params['start']:meas_params['stop']]
                m = sum(arr) / len(arr)


            # update threshold
            if thres_mode == 'max_min' and m != 0 and m > m_max:
                m_max           = m
                Thres['value']  = m_max
                Thres[x_name]   = X[i]
                Thres[y_name]   = Y[j]
            if thres_mode == 'max_max' and m != 0 and m >= m_max:
                m_max           = m
                Thres['value']  = m_max
                Thres[x_name]   = X[i]
                Thres[y_name]   = Y[j]
        
            # update list
            M[j][i] = m

            # update plot
            if plot:
                plotter.update(Z=M)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(Z=M, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = Y
    Axes['z'] = []

    # return data
    return M, Thres, Axes