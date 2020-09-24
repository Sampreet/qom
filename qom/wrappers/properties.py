#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for properties."""

__name__    = 'qom.wrappers.properties'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-15'
__updated__ = '2020-09-23'

# dependencies
import copy
import logging
import numpy as np
import os

# dev dependencies
from qom.ui import figure
from qom.utils import axis

# module logger
logger = logging.getLogger(__name__)

# TODO: Move `get_grad` and index functions to to `qom/utils/array`.
# TODO: Handle scatter plots for gradient functions.
# TODO: Handle single parameter case for `get_grad`.
# TODO: Handle multi-value points for 2D functions.
# TODO: Implement 3D plots.
# TODO: Verify parametes.

def calculate(model, data):
    """Wrapper function to switch functions for calculation of properties.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        data : dict
            Data for the calculation.

    Returns
    -------
        data : list
            Data of the propreties calculated.
    """

    # get properties
    return globals()[data['prop_params']['func']](model, data['prop_params'], data['plot'], data['plot_params'])

def properties_1D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate properties versus a continuous variable.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        prop_params : dict
            Parameters for the property.

        plot : boolean, optional
            Option to plot the property.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        P : list
            Properties calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the properties as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    X           = axis.StaticAxis(prop_params['X'])

    # initialize variables
    X_p = axis.DynamicAxis([len(X.values)])
    P = axis.DynamicAxis([len(X.values)])

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X)

    # display initialization
    logger.info('Initializing {prop_name} calculation...\t\n'.format(prop_name=prop_name))

    # for variation in X
    for i in range(len(X.values)):
        # calculate progress
        progress = float(i) / float(len(X.values)) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model
        model.p[X.var] = X.values[i]

        # get property from model
        p = getattr(model, prop_code)()

        # update lists for scatter plot
        if type(p) == list:
            X_p.values += [X.values[i] for l in range(len(p))]
            P.values += p
        # update lists for line plot
        else:
            X_p.values.append(X.values[i])
            P.values.append(p)

        # update plot
        if plot and plot_prog:
            plotter.update(X_p, P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')

    # update plot
    if plot:
        plotter.update(X_p, P, head=False, hold=True)
    
    thres_idx = get_thres_indices(P.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(P.values)]
    X_p.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_p

    # return data
    return P.values, Thres, Axes

def properties_1D_multi(model, prop_params, plot=False, plot_params=None):
    """Function to calculate properties versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        prop_params : dict
            Parameters for the property.

        plot : boolean, optional
            Option to plot the property.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        P : list
            Properties calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the properties as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    X           = axis.StaticAxis(prop_params['X'])
    Z           = axis.StaticAxis(prop_params['Z'])

    # initialize variables
    X_p = axis.DynamicAxis([len(Z.values), len(X.values)])
    Z_p = axis.DynamicAxis([len(Z.values), len(X.values)])
    P = axis.DynamicAxis([len(Z.values), len(X.values)])

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X, Z=Z)

    # display initialization
    logger.info('Initializing {prop_name} calculation...\t\n'.format(prop_name=prop_name))

    # for variation in X
    for i in range(len(X.values)):
        # for variation in Z
        for j in range(len(Z.values)):
            # calculate progress
            progress = ((float(i) + float(j) / float(len(Z.values))) / float(len(X.values))) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.p[X.var] = X.values[i]
            model.p[Z.var] = Z.values[j]

            # get property from model
            p = getattr(model, prop_code)()

            # update lists for multi-scatter plot
            if type(p) == list:
                X_p.values[j] += [X.values[i] for l in range(len(p))]
                Z_p.values[j] += [Z.values[j] for l in range(len(p))]
                P.values[j] += p
            # update lists for multi-line plot
            else:
                X_p.values[j].append(X.values[i])
                Z_p.values[j].append(Z.values[j])
                P.values[j].append(p)

        # update plot
        if plot and plot_prog:
            plotter.update(X_p, P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')

    # update plot
    if plot:
        plotter.update(X_p, P, head=False, hold=True)
    
    thres_idx = get_thres_indices(P.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[1]]
    Thres[Z.var] = Z.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(P.values), len(P.values[0])]
    X_p.size = dim
    Z_p.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_p
    Axes['Z'] = Z_p

    # return data
    return P.values, Thres, Axes

def properties_2D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate properties versus two continuous variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        prop_params : dict
            Parameters for the property.

        plot : boolean, optional
            Option to plot the property.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        P : list
            Properties calculated.

        Thres: dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the properties as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    X           = axis.StaticAxis(prop_params['X'])
    Y           = axis.StaticAxis(prop_params['Y'])

    # initialize variables
    X_p = axis.DynamicAxis([len(Y.values), len(X.values)])
    Y_p = axis.DynamicAxis([len(Y.values), len(X.values)])
    P = axis.DynamicAxis([len(Y.values), len(X.values)])

    for j in range(len(Y.values)):
        P.values[j] = [np.NaN for i in range(len(X.values))]

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X, Y=Y, Z=P)

    # display initialization
    logger.info('Initializing {prop_name} calculation...\t\n'.format(prop_name=prop_name))

    # for variation in Y
    for j in range(len(Y.values)):
        # for variation in X
        for i in range(len(X.values)):
            # calculate progress
            progress = ((float(j) + float(i) / float(len(X.values))) / float(len(Y.values))) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.p[X.var] = X.values[i]
            model.p[Y.var] = Y.values[j]

            # get property from model
            p = getattr(model, prop_code)()

            if type(p) == list:
                if thres_mode.find('max_') != -1:
                    p = max(p)

            # update list
            X_p.values[j].append(X.values[i])
            Y_p.values[j].append(Y.values[j])
            P.values[j][i] = p

        # update plot
        if plot and plot_prog:
            plotter.update(Z=P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')

    # update plot
    if plot:
        plotter.update(Z=P, head=False, hold=True)
    
    thres_idx = get_thres_indices(P.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[1]]
    Thres[Y.var] = Y.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(P.values), len(P.values[0])]
    X_p.size = dim
    Y_p.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_p
    Axes['Y'] = Y_p

    # return data
    return P.values, Thres, Axes

def properties_grad_1D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate a gradient of properties versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        prop_params : dict
            Parameters for the property.

        plot : boolean, optional
            Option to plot the property.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        G : list
            Gradients calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the gradients as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    grad_axis   = prop_params['grad_axis']
    thres_mode  = prop_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    prop_model  = copy.deepcopy(model)

    # switch variables for property function
    if grad_axis == 'X':
        # get properties
        P_values, Thres, Axes = properties_1D(prop_model, prop_params)
        # calculate gradients
        Grads = np.gradient(P_values, Axes['X'].values)
        X = axis.StaticAxis(prop_params['X'])
    elif grad_axis == 'Y':
        # get properties
        P_values, Thres, Axes = properties_2D(prop_model, prop_params)
        X = axis.StaticAxis(prop_params['Y'])

    # initialize variables
    X_g = axis.DynamicAxis([len(X.values)])
    G = axis.DynamicAxis([len(X.values)])

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X)

    # display initialization
    logger.info('Initializing {prop_name} gradient calculation...\t\n'.format(prop_name=prop_name))
    
    # for variation in X
    for i in range(len(X.values)):
        # calculate progress
        progress = float(i) / float(len(X.values)) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model for gradient calculation
        model.p[X.var] = X.values[i]

        # get parameters from model
        grad_params = model.get_grad_params()

        if grad_axis == 'X':
            # obtain calculated gradients
            grad = Grads[i] / grad_params['divisor']
        elif grad_axis == 'Y':
            # get gradient at particular value
            grad = get_grad(P_values[i], Axes['X'].values[i], grad_params)

        # update lists for line plot
        X_g.values.append(X.values[i])
        G.values.append(grad)
        
        # update plot
        if plot and plot_prog:
            plotter.update(X_g, G)
    
    # display completion
    logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {G}\n'.format(G=G))

    # update plot
    if plot:
        plotter.update(X_g, G, head=False, hold=True)
    
    thres_idx = get_thres_indices(G.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(G.values)]
    X_g.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_g

    # return data
    return G.values, Thres, Axes

def properties_grad_1D_multi(model, prop_params, plot=False, plot_params=None):
    """Function to calculate a gradient of properties versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        prop_params : dict
            Parameters for the property.

        plot : boolean, optional
            Option to plot the property.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        G : list
            Gradients calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the gradients as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    grad_axis   = prop_params['grad_axis']
    thres_mode  = prop_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    X           = axis.StaticAxis(prop_params[grad_axis])
    Z           = axis.StaticAxis(prop_params['Z'])

    # initialize variables
    X_g = axis.DynamicAxis([len(Z.values), len(X.values)])
    Z_g = axis.DynamicAxis([len(Z.values), len(X.values)])
    G = axis.DynamicAxis([len(Z.values), len(X.values)])

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X, Z=Z)

    # for variation in Z
    for j in range(len(Z.values)):
        # display initialization
        logger.info('Initializing {prop_name} gradient calculation for {legend}\t\n'.format(prop_name=prop_name, legend=Z.legends[j]))

        # update model for property calculation
        prop_model = copy.deepcopy(model)
        prop_model.p[Z.var] = Z.values[j]

        # switch variables for property function
        if grad_axis == 'X':
            P_values, Thres, Axes = properties_1D(prop_model, prop_params)
            # calculate gradients
            Grads = np.gradient(P_values, Axes['X'].values)
        elif grad_axis == 'Y':
            # get properties
            P_values, Thres, Axes = properties_2D(prop_model, prop_params)

        # for variation in X 
        for i in range(len(X.values)):
            # calculate progress
            progress = (float(i) / float(len(X.values))) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model for gradient calculation
            model.p[X.var] = X.values[i]
            model.p[Z.var] = Z.values[j]

            # get parameters from model
            grad_params = model.get_grad_params()

            if grad_axis == 'X':
                # obtain calculated gradients
                grad = Grads[i] / grad_params['divisor']
            elif grad_axis == 'Y':
                # get gradient at particular value
                grad = get_grad(P_values[i], Axes['X'].values[i], grad_params)

            # update lists for line plot
            X_g.values[j].append(X.values[i])
            Z_g.values[j].append(Z.values[j])
            G.values[j].append(grad)
            
            # update plot
            if plot and plot_prog:
                plotter.update(X_g, G)
    
        # display completion
        logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {G}\n'.format(G=G))

    # update plot
    if plot:
        plotter.update(X_g, G, head=False, hold=True)
    
    thres_idx = get_thres_indices(G.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[1]]
    Thres[Z.var] = Z.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(G.values), len(G.values[0])]
    X_g.size = dim
    Z_g.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_g
    Axes['Z'] = Z_g

    # return data
    return G.values, Thres, Axes

def properties_grad_2D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate a gradient of properties versus two continuous variables.
    
    Parameters
    ----------
        model : :class:`Model`
            Model of the system.

        prop_params : dict
            Parameters for the property.

        plot : boolean, optional
            Option to plot the property.

        plot_params : dict, optional
            Parameters for the plot.

    Returns
    -------
        G : list
            Gradients calculated.

        Thres : dict
            Threshold values of the variables used.

        Axes : dict
            Axes points used to calculate the gradients as :class:`qom.utils.axis.DynamicAxis`.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    plot_prog   = plot_params['progress'] if plot_params != None else False 
    prop_model  = copy.deepcopy(model)

    # get properties
    P_values, Thres, Axes = properties_2D(prop_model, prop_params)
    X = axis.StaticAxis(prop_params['X'])
    Y = axis.StaticAxis(prop_params['Y'])

    # initialize variables
    X_g = axis.DynamicAxis([len(Y.values), len(X.values)])
    Y_g = axis.DynamicAxis([len(Y.values), len(X.values)])
    G = axis.DynamicAxis([len(Y.values), len(X.values)])

    for j in range(len(Y.values)):
        G.values[j] = [np.NaN for i in range(len(X.values))]

    # initialize plot
    if plot:
        plotter = figure.Plotter(plot_params, X=X, Y=Y, Z=G)

    # display initialization
    logger.info('Initializing {prop_name} gradient calculation...\t\n'.format(prop_name=prop_name))
        
    # for variation in Y
    for j in range(len(Y.values)):
        # calculate progress
        progress = float(j) / float(len(Y.values)) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model for gradient calculation
        model.p[Y.var] = Y.values[j]

        # get parameters from model
        grad_params = model.get_grad_params()

        # calculate gradients
        Grads = np.gradient(P_values[j], X.values) / grad_params['divisor']

        # update lists
        X_g.values.append(X.values)
        Y_g.values.append([Y.values[j] for _ in range(len(X.values))])
        G.values[j] = Grads.tolist()
            
        # update plot
        if plot and plot_prog:
            plotter.update(Z=G)
    
    # display completion
    logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {Grads}\t\n'.format(Grads=Grads))

    # update plot
    if plot:
        plotter.update(Z=G, head=False, hold=True)
    
    thres_idx = get_thres_indices(G.values, thres_mode)

    Thres = {}
    Thres[X.var] = X.values[thres_idx[1]]
    Thres[Y.var] = Y.values[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update sizes
    dim = [len(G.values), len(G.values[0])]
    X_g.size = dim
    Y_g.size = dim

    # axes dictionary
    Axes = {}
    Axes['X'] = X_g
    Axes['Y'] = Y_g

    # return data
    return G.values, Thres, Axes

def get_grad(Y, X, grad_params):
    """Function to calculate the gradient of a dataset at a particular position.
    
    Parameters
    ----------
        Y : list
            Values of the dataset.

        X : list
            Positions of the dataset.

        grad_params : dict
            Options for the position.

    Returns
    -------
        grad : float
            Value of the gradient at the position.
    """

    # calculate gradients
    temp = np.gradient(Y, X)

    # if position is specified
    if grad_params['mode'] == 'at_position':
        index = abs(np.asarray(X) - grad_params['position']).argmin()

    # if vicinity is specified
    if grad_params['mode'] == 'near_position':
        # list of indices for mean of monotonic behaviour
        list_idx = get_index_monotonic_mean(temp)

        # index of gradient position
        temp_index = abs(np.asarray(X) - grad_params['position']).argmin()

        # get minimum index
        index = list_idx[abs(np.asarray(list_idx) - temp_index).argmin()]

    # if monotonocity mid position is specified
    if grad_params['mode'] == 'at_mono_mid':
        # list of indices for mean of monotonic behaviour
        list_idx = get_index_monotonic_mean(temp)

        # get minimum index
        index = list_idx[grad_params['mono_id'] - 1]

    # if monotonocity local maxima/minima value is specified
    if grad_params['mode'] == 'at_mono_max_min':
        # list of indices for mean of monotonic behaviour
        list_idx = get_index_monotonic_mean(temp)

        # get minimum index
        index = list_idx[grad_params['mono_id'] - 1]
    
    grad = temp[index]
    if 'divisor' in grad_params:
        grad /= grad_params['divisor']

    return grad

def get_index_monotonic_mean(Y):
    """Function to calculate the position of the mid points of monotonicity for given function data.
    
    Parameters
    ----------
        Y : list
            Values of the data.

    Returns
    -------
        idx : list
            Indices of the mid points.
    """
    
    # list of signum values
    sgn = [1 if ele >= 0 else -1 for ele in Y]
    # list of mid points of same sign
    idx = []
    # sign of element
    sign = sgn[0]
    # start index
    i = 0
    for j in range(1, len(sgn)):
        # if sign changes
        if sgn[j] != sign:
            # mark mid value of previous cluster
            idx.append((int) ((i + j - 1) / 2))
            sign = sgn[j]
            i = j
    idx.append((int) ((i + len(sgn) - 1) / 2))

    return idx

def get_index_monotonic_max_min(Y):
    """Function to calculate the position of the local maximas/minimas of monotonicity for given function data.
    
    Parameters
    ----------
        Y : list
            Values of the data.

    Returns
    -------
        idx : list
            Indices of the local maximas points.
    """
    
    # list of signum values
    sgn = [1 if ele >= 0 else -1 for ele in Y]
    # list of local maxima/minima points of same sign
    idx = []
    # sign of element
    sign = sgn[0]
    # start index
    i = 0
    for j in range(1, len(sgn)):
        # if sign changes
        if sgn[j] != sign:
            # mark max value of previous cluster
            idx.append(np.abs(np.asarray(Y[i:j - 1])).argmax() + i)
            sign = sgn[j]
            i = j
    idx.append(np.abs(np.asarray(Y[i:j - 1])).argmax() + i)

    return idx

def get_thres_indices(values, thres_mode='max_min'):
    """Function to obtain the indices of threshold for a given mode.

    Parameters
    ----------
        values : list
            Values of the variable.

        thres_mode : str
            Mode of threshold index calculation:
                min_min : Minimum index where minimum is observed.
                min_max : Maximum index where minimum is observed.
                max_min : Minimum index where minimum is observed.
                max_max : Maximum index where minimum is observed.

    Returns
    -------
        res : list
            Indices of the threshold.
    """

    # indices of minimas and maximas
    idx_min = np.argwhere(np.array(values) == np.amin(values)).flatten().tolist()
    idx_max = np.argwhere(np.array(values) == np.amax(values)).flatten().tolist()

    # handle 1D array
    idx_min = [idx_min[2 * i : 2 * i + len(np.shape(values))] for i in range(int(len(idx_min) / len(np.shape(values))))]
    idx_max = [idx_max[2 * i : 2 * i + len(np.shape(values))] for i in range(int(len(idx_max) / len(np.shape(values))))]

    # required threshold
    res = {
        'min_min': idx_min[0],
        'min_max': idx_min[-1],
        'max_min': idx_max[0],
        'max_max': idx_max[-1]
    }

    return res[thres_mode]


