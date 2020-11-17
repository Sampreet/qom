#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Looper functions for measures."""

__name__    = 'qom.loopers.measures'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-23'
__updated__ = '2020-11-17'

# dependencies
import logging
import numpy as np

# dev dependencies
from qom.loopers import dynamics
from qom.ui import Figure
from qom.ui.axes import MultiAxis, StaticAxis
from qom.utils.misc import get_index_threshold

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
    return globals()[data['meas_params']['func']](model, data['dyna_params'], data['meas_params'], data.get('plot', False), data.get('plot_params', None))

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
            Axes points used to calculate the properties as lists.
    """

    # extract frequently used variables
    span_mode    = meas_params['span_mode']
    calc_mode    = meas_params['calc_mode']
    thres_mode  = meas_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False

    # get dynamics
    D_all, _, Axes = dynamics.dynamics_measure(model, dyna_params, meas_params, plot_prog, plot_params)
    X = StaticAxis({'val': Axes['X']})

    # initialize variables
    X_m = np.zeros((X.dim))
    M = np.zeros((X.dim))
    M[:] = np.NaN

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'line'
        figure = Figure(plot_params, X=X)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in X
    for i in range(X.dim):
        # calculate progress
        progress = float(i) / float(X.dim) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the average values: Progress = {progress:3.2f}'.format(progress=progress))

        # initialize value
        m = 0

        # calculate span
        if span_mode == 'all':
            arr = D_all[i]
        elif span_mode == 'end':
            arr = D_all[i][-meas_params['span']:]
        elif span_mode == 'range':
            arr = D_all[i][meas_params['start']:meas_params['stop']]

        # calculate measures
        if calc_mode == 'mean':
            m = np.mean(arr)
        elif calc_mode == 'max':
            m = np.max(arr)
        elif calc_mode == 'min':
            m = np.min(arr)
        elif calc_mode == 'min_max':
            m = (np.max(arr) + np.min(arr)) / 2
    
        # update list
        X_m[i] = X.val[i]
        M[i] = m

        # update plot
        if plot and plot_prog:
            figure.update(X_m, M, head=True, hold=False)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')
    
    thres_idx = get_index_threshold(M, thres_mode)

    Thres = {}
    Thres[X.var] = X.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(X_m, M)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_m.tolist()

    # return data
    return M.tolist(), Thres, Axes

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
            Axes points used to calculate the properties as lists.
    """

    # extract frequently used variables
    span_mode    = meas_params['span_mode']
    calc_mode    = meas_params['calc_mode']
    thres_mode  = meas_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    X           = StaticAxis(meas_params['X'])
    Z           = MultiAxis(meas_params['Z'])

    # initialize variables
    X_m = np.zeros([Z.dim, X.dim])
    Z_m = np.zeros([Z.dim, X.dim])
    M = np.zeros([Z.dim, X.dim])
    M[:] = np.NaN

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'lines'
        figure = Figure(plot_params, X=X, Z=Z)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in Z
    for j in range(Z.dim):
        # update model
        model.params[Z.var] = Z.val[j]

        # get dynamics
        D_all, _, Axes = dynamics.dynamics_measure(model, dyna_params, meas_params, plot_prog, plot_params)

        # for variation in X
        for i in range(X.dim):
            # calculate progress
            progress = ((float(i) + float(j) / float(Z.dim)) / float(X.dim)) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the average values: Progress = {progress:3.2f}'.format(progress=progress))

            # initialize value
            m = 0

            # calculate span
            if span_mode == 'all':
                arr = D_all[i]
            elif span_mode == 'end':
                arr = D_all[i][-meas_params['span']:]
            elif span_mode == 'range':
                arr = D_all[i][meas_params['start']:meas_params['stop']]

            # calculate measures
            if calc_mode == 'mean':
                m = np.mean(arr)
            elif calc_mode == 'max':
                m = np.max(arr)
            elif calc_mode == 'min':
                m = np.min(arr)
            elif calc_mode == 'min_max':
                m = (np.max(arr) + np.min(arr)) / 2
        
            # update list
            X_m[j][i] = X.val[i]
            Z_m[j][i] = Z.val[j]
            M[j][i] = m

        # update plot
        if plot and plot_prog:
            figure.update(X_m, M, head=True, hold=False)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')
    
    thres_idx = get_index_threshold(M, thres_mode)

    Thres = {}
    Thres[X.var] = X.val[thres_idx[1]]
    Thres[Z.var] = Z.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(X_m, M)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_m.tolist()
    Axes['Z'] = Z_m.tolist()

    # return data
    return M.tolist(), Thres, Axes

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
            Axes points used to calculate the measures as lists.
    """

    # extract frequently used variables
    span_mode    = meas_params['span_mode']
    calc_mode    = meas_params['calc_mode']
    thres_mode  = meas_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    X           = StaticAxis(meas_params['X'])
    Y           = StaticAxis(meas_params['Y'])

    # initialize variables
    X_m = np.zeros([Y.dim, X.dim])
    Y_m = np.zeros([Y.dim, X.dim])
    M = np.zeros([Y.dim, X.dim])
    M[:] = np.NaN

    for j in range(Y.dim):
        M[j] = [np.NaN for i in range(X.dim)]

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'pcolormesh'
        figure = Figure(plot_params, X=X, Y=Y)

    # display initialization
    logger.info('Initializing average {meas_name} calculation...\t\n'.format(meas_name=meas_params['name']))

    # for variation in Y
    for j in range(Y.dim):
        # update model
        model.params[Y.var] = Y.val[j]

        # get dynamics
        D_all, _, Axes = dynamics.dynamics_measure(model, dyna_params, meas_params, plot_prog, plot_params)

        # for variation in X
        for i in range(X.dim):
            # calculate progress
            progress = ((float(j) + float(i) / float(X.dim)) / float(Y.dim)) * 100
            # display progress
            logger.info('Calculating the measure values: Progress = {progress:3.2f}'.format(progress=progress))

            # initialize value
            m = 0

            # calculate span
            if span_mode == 'all':
                arr = D_all[i]
            elif span_mode == 'end':
                arr = D_all[i][-meas_params['span']:]
            elif span_mode == 'range':
                arr = D_all[i][meas_params['start']:meas_params['stop']]

            # calculate measures
            if calc_mode == 'mean':
                m = np.mean(arr)
            elif calc_mode == 'max':
                m = np.max(arr)
            elif calc_mode == 'min':
                m = np.min(arr)
            elif calc_mode == 'min_max':
                m = (np.max(arr) + np.min(arr)) / 2
        
            # update list
            X_m[j][i] = X.val[i]
            Y_m[j][i] = Y.val[j]
            M[j][i] = m

            # update plot
            if plot and plot_prog:
                figure.update(zs=M, hold=False)
        
    # display completion
    logger.info('----------------Average Measures Obtained----------------\n')
    
    thres_idx = get_index_threshold(M, thres_mode)

    Thres = {}
    Thres[X.var] = X.val[thres_idx[1]]
    Thres[Y.var] = Y.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(zs=M)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_m.tolist()
    Axes['Y'] = Y_m.tolist()

    # return data
    return M.tolist(), Thres, Axes