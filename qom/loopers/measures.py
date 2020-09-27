#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Looper functions for measures."""

__name__    = 'qom.loopers.measures'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-23'
__updated__ = '2020-09-27'

# dependencies
import logging
import numpy as np

# dev dependencies
from qom.loopers import dynamics
from qom.ui import figure
from qom.utils import axis, misc

# module logger
logger = logging.getLogger(__name__)

# TODO: Verify parametes.

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
            Model of the systems.
        
        dyna_params : dict
            Parameters for the dynamics.
        
        meas_params : dict
            Parameters for the measures.

        plot : boolean, optional
            Option to plot the measures.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        M : list
            Measures calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the properties as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    avg_mode    = meas_params['avg_mode']
    avg_type    = meas_params['avg_type']
    thres_mode  = meas_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 

    # get dynamics
    D_all, _, Axes = dynamics.dynamics_measure(model, dyna_params, meas_params)
    X = Axes['X']

    # initialize variables
    X_m = axis.DynamicAxis([len(X.values)])
    M = axis.DynamicAxis([len(X.values)])

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in X
    for i in range(len(X.values)):
        # calculate progress
        progress = float(i) / float(len(X.values)) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the average values: Progress = {progress:3.2f}'.format(progress=progress))

        # initialize value
        m = 0

        # calculate average value
        if avg_mode == 'all':
            m = np.mean(D_all[i])
        elif avg_mode == 'end' and avg_type == 'min_max':
            arr = D_all[i][-meas_params['span']:]
            m = (max(arr) + min(arr)) / 2
        elif avg_mode == 'range' and avg_type == 'min_max':
            arr = D_all[i][meas_params['start']:meas_params['stop']]
            m = (max(arr) + min(arr)) / 2
        elif avg_mode == 'end' and avg_type == 'mean':
            arr = D_all[i][-meas_params['span']:]
            m = np.mean(arr)
        elif avg_mode == 'range' and avg_type == 'mean':
            arr = D_all[i][meas_params['start']:meas_params['stop']]
            m = np.mean(arr)
    
        # update list
        X_m.values.append(X.values[i])
        M.values.append(m)

        # update plot
        if plot and plot_prog:
            plotter.update(X_m, M)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')

    # update plot
    if plot:
        plotter.update(X_m, M, head=False, hold=True)
    
    thres_idx = misc.get_index_threshold(M.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(M.values)]
    X_m.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X

    # return data
    return M.values, Thres, Axes

def measures_1D_multi(model, dyna_params, meas_params, plot=False, plot_params=None):
    """Function to calculate measures versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the systems.
        
        dyna_params : dict
            Parameters for the dynamics.
        
        meas_params : dict
            Parameters for the measures.

        plot : boolean, optional
            Option to plot the measures.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        M : list
            Measures calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the properties as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    avg_mode    = meas_params['avg_mode']
    avg_type    = meas_params['avg_type']
    thres_mode  = meas_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    X           = axis.StaticAxis(meas_params['X'])
    Z           = axis.StaticAxis(meas_params['Z'])

    # initialize variables
    X_m = axis.DynamicAxis([len(Z.values), len(X.values)])
    Z_m = axis.DynamicAxis([len(Z.values), len(X.values)])
    M = axis.DynamicAxis([len(Z.values), len(X.values)])

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X, Z=Z)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in Z
    for j in range(len(Z.values)):
        # update model
        model.params[Z.var] = Z.values[j]

        # get dynamics
        D_all, _, Axes = dynamics.dynamics_measure(model, dyna_params, meas_params)

        # for variation in X
        for i in range(len(X.values)):
            # calculate progress
            progress = ((float(i) + float(j) / float(len(Z.values))) / float(len(X.values))) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the average values: Progress = {progress:3.2f}'.format(progress=progress))

            # initialize value
            m = 0

            # calculate average value
            if avg_mode == 'all':
                m = np.mean(D_all[i])
            elif avg_mode == 'end' and avg_type == 'min_max':
                arr = D_all[i][-meas_params['span']:]
                m = (max(arr) + min(arr)) / 2
            elif avg_mode == 'range' and avg_type == 'min_max':
                arr = D_all[i][meas_params['start']:meas_params['stop']]
                m = (max(arr) + min(arr)) / 2
            elif avg_mode == 'end' and avg_type == 'mean':
                arr = D_all[i][-meas_params['span']:]
                m = np.mean(arr)
            elif avg_mode == 'range' and avg_type == 'mean':
                arr = D_all[i][meas_params['start']:meas_params['stop']]
                m = np.mean(arr)
        
            # update list
            X_m.values[j].append(X.values[i])
            Z_m.values[j].append(Z.values[j])
            M.values[j].append(m)

        # update plot
        if plot and plot_prog:
            plotter.update(X_m, M)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')

    # update plot
    if plot:
        plotter.update(X_m, M, head=False, hold=True)
    
    thres_idx = misc.get_index_threshold(M.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[1]]
    Thres[Z.var] = Z.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(M.values), len(M.values[0])]
    X_m.size = dim
    Z_m.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_m
    Axes['Z'] = Z_m

    # return data
    return M.values, Thres, Axes

def measures_2D(model, dyna_params, meas_params, plot, plot_params):
    """Function to calculate measures versus two continuous variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the systems.
        
        dyna_params : dict
            Parameters for the dynamics.
        
        meas_params : dict
            Parameters for the measures.

        plot : boolean, optional
            Option to plot the measures.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        M : list
            Measures calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the measures as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    avg_mode    = meas_params['avg_mode']
    avg_type    = meas_params['avg_type']
    thres_mode  = meas_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    X           = axis.StaticAxis(meas_params['X'])
    Y           = axis.StaticAxis(meas_params['Y'])

    # initialize variables
    X_m = axis.DynamicAxis([len(Y.values), len(X.values)])
    Y_m = axis.DynamicAxis([len(Y.values), len(X.values)])
    M = axis.DynamicAxis([len(Y.values), len(X.values)])

    for j in range(len(Y.values)):
        M.values[j] = [np.NaN for i in range(len(X.values))]

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X, Y=Y, Z=M)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in Y
    for j in range(len(Y.values)):
        # update model
        model.params[Y.var] = Y.values[j]

        # get dynamics
        D_all, _, Axes = dynamics.dynamics_measure(model, dyna_params, meas_params)

        # for variation in X
        for i in range(len(X.values)):
            # calculate progress
            progress = ((float(j) + float(i) / float(len(X.values))) / float(len(Y.values))) * 100
            # display progress
            logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

            # initialize value
            m = 0

            # calculate average value
            if avg_mode == 'all':
                m = np.mean(D_all[i])
            elif avg_mode == 'end' and avg_type == 'min_max':
                arr = D_all[i][-meas_params['span']:]
                m = (max(arr) + min(arr)) / 2
            elif avg_mode == 'range' and avg_type == 'min_max':
                arr = D_all[i][meas_params['start']:meas_params['stop']]
                m = (max(arr) + min(arr)) / 2
            elif avg_mode == 'end' and avg_type == 'mean':
                arr = D_all[i][-meas_params['span']:]
                m = np.mean(arr)
            elif avg_mode == 'range' and avg_type == 'mean':
                arr = D_all[i][meas_params['start']:meas_params['stop']]
                m = np.mean(arr)
        
            # update list
            X_m.values[j].append(X.values[i])
            Y_m.values[j].append(Y.values[j])
            M.values[j][i] = m

            # update plot
            if plot and plot_prog:
                plotter.update(Z=M)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')

    # update plot
    if plot:
        plotter.update(Z=M, head=False, hold=True)
    
    thres_idx = misc.get_index_threshold(M.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[1]]
    Thres[Y.var] = Y.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(M.values), len(M.values[0])]
    X_m.size = dim
    Y_m.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_m
    Axes['Y'] = Y_m

    # return data
    return M.values, Thres, Axes