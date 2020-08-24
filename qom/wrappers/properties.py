#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for properties."""

__name__    = 'qom.wrappers.properties'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-15'
__updated__ = '2020-08-18'

# dependencies
import logging
import numpy as np
import os

# dev dependencies
from qom.ui import figure

# module logger
logger = logging.getLogger(__name__)

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

    plot : boolean
        Option to plot the property.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    P : list
        Properties calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: verify presence of parametes

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    x_name      = prop_params['X']['name']
    x_min       = prop_params['X']['min']
    x_max       = prop_params['X']['max']
    x_steps     = prop_params['X']['steps']

    # initialize variables
    num_decimals = int(np.ceil(np.log10((x_steps - 1) / (x_max - x_min))))
    X = np.around(np.linspace(x_min, x_max, x_steps), num_decimals).tolist()
    X_p = []
    P = []
    Thres = {}
    Thres[x_name] = x_min - 1

    # threshold values
    if thres_mode.find('max_') != -1:
        # max value of property
        p_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X)

    # display initialization
    logger.info('Initializing {prop_name} calculation...\t\n'.format(prop_name=prop_name))

    # for variation in X
    for i in range(len(X)):
        # calculate progress
        progress = float(i) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model
        model.p[x_name] = X[i]

        # get property from model
        p = getattr(model, prop_code)()

        # update lists for scatter plot
        if type(p) == list:
            X_p += [X[i] for l in range(len(p))]
            P += p
            if thres_mode.find('max_') != -1:
                p = max(p)
        # update lists for line plot
        else:
            X_p.append(X[i])
            P.append(p)

        # update thresholds
        if thres_mode == 'max_min' and p != 0 and p > p_max:
            p_max = p
            Thres['value'] = p_max
            Thres[x_name] = X[i]
        if thres_mode == 'max_max' and p != 0 and p >= p_max:
            p_max = p
            Thres['value'] = p_max
            Thres[x_name] = X[i]

        # update plot
        if plot:
            plotter.update(X_p, P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(X_p, P, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = []
    Axes['z'] = []

    # return data
    return P, Thres, Axes

def properties_1D_multi(model, prop_params, plot=False, plot_params=None):
    """Function to calculate properties versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    prop_params : dict
        Parameters for the property.

    plot : boolean
        Option to plot the property.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    P : list
        Properties calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: assert property and plot parametes

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    x_name      = prop_params['X']['name']
    x_min       = prop_params['X']['min']
    x_max       = prop_params['X']['max']
    x_steps     = prop_params['X']['steps']
    z_name      = prop_params['Z']['name']
    z_unit      = prop_params['Z']['unit']
    Z           = prop_params['Z']['values']
    if plot:
        plot_params['legend'] = ['{name} = {value} {unit}'.format(name=z_name, value=z, unit=z_unit) for z in Z]

    # initialize variables
    num_decimals = int(np.ceil(np.log10((x_steps - 1) / (x_max - x_min))))
    X = np.around(np.linspace(x_min, x_max, x_steps), num_decimals).tolist()
    X_p = []
    P = []
    Thres = {}
    Thres[x_name] = x_min - 1

    # threshold values
    if thres_mode.find('max_') != -1:
        # max value of property
        p_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X, Z=Z)

    # display initialization
    logger.info('Initializing {prop_name} calculation...\t\n'.format(prop_name=prop_name))
    
    # for variation in Z
    for j in range(len(Z)):       
        # for variation in X
        for i in range(len(X)):
            # calculate progress
            progress = ((float(j) + float(i) / float(len(X))) / float(len(Z))) * 100
            # display progress
            logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.p[x_name] = X[i]
            model.p[z_name] = Z[j]

            # get property from model
            p = getattr(model, prop_code)()

            # update lists for multi-scatter plot
            if type(p) == list:
                X_p += [X[i] for l in range(len(p))]
                P += p
                if thres_mode.find('max_') != -1:
                    p = max(p)
            # update lists for multi-line plot
            else:
                X_p.append(X[i])
                P.append(p)

            # update thresholds
            if thres_mode == 'max_min' and p != 0 and p > p_max:
                p_max = p
                Thres['value'] = p_max
                Thres[x_name] = X[i]
            if thres_mode == 'max_max' and p != 0 and p >= p_max:
                p_max = p
                Thres['value'] = p_max
                Thres[x_name] = X[i]

            # update plot
            if plot:
                plotter.update(X_p, P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(X_p, P, head=False, hold=True)

    # reshape list
    P = np.reshape(P, (len(Z), len(X))).tolist()

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = []
    Axes['z'] = Z

    # return data
    return P, Thres, Axes

def properties_2D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate properties versus two continuous variables.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    prop_params : dict
        Parameters for the property.

    plot : boolean
        Option to plot the property.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    P : list
        Properties calculated.

    Thres: dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: assert property and plot parametes

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params['thres_mode']
    x_name      = prop_params['X']['name']
    x_min       = prop_params['X']['min']
    x_max       = prop_params['X']['max']
    x_steps     = prop_params['X']['steps']
    y_name      = prop_params['Y']['name']
    y_min       = prop_params['Y']['min']
    y_max       = prop_params['Y']['max']
    y_steps     = prop_params['Y']['steps']

    # initialize variables
    num_decimals = int(np.ceil(np.log10((x_steps - 1) / (x_max - x_min))))
    X = np.around(np.linspace(x_min, x_max, x_steps), num_decimals).tolist()
    num_decimals = int(np.ceil(np.log10((y_steps - 1) / (y_max - y_min))))
    Y = np.around(np.linspace(y_min, y_max, y_steps), num_decimals).tolist()
    P = np.empty((len(Y), len(X)))
    P[:] = np.NaN
    Thres = {}
    Thres[x_name] = x_min - 1
    Thres[y_name] = y_min - 1

    # threshold values
    if thres_mode.find('max_') != -1:
        # max value of property
        p_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X, Y=Y, Z=P)

    # display initialization
    logger.info('Initializing {prop_name} calculation...\t\n'.format(prop_name=prop_name))

    # for variation in Y
    for j in range(len(Y)):
        # for variation in X
        for i in range(len(X)):
            # calculate progress
            progress = ((float(j) + float(i) / float(len(X))) / float(len(Y))) * 100
            # display progress
            logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.p[x_name] = X[i]
            model.p[y_name] = Y[j]

            # get property from model
            p = getattr(model, prop_code)()

            # handle multi-value points
            if type(p) == list:
                if thres_mode.find('max_') != -1:
                    p = max(p)

            # update list
            P[j][i] = p

            # update thresholds
            if thres_mode == 'max_min' and p != 0 and p > p_max:
                p_max = p
                Thres['value'] = p_max
                Thres[x_name] = X[i]
                Thres[y_name] = Y[j]
            if thres_mode == 'max_max' and p != 0 and p >= p_max:
                p_max = p
                Thres['value'] = p_max
                Thres[x_name] = X[i]
                Thres[y_name] = Y[j]

            # update plot
            if plot:
                plotter.update(Z=P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(Z=P, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = Y
    Axes['z'] = []

    # return data
    return P, Thres, Axes

def properties_grad_1D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate a gradient of properties versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    prop_params : dict
        Parameters for the property.

    plot  : boolean
        Option to plot the property.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    P : list
        Properties calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: assert property and plot parametes

    # extract frequently used variables
    prop_name   = prop_params['name']
    grad_func   = prop_params['grad_func']
    prop_model  = model

    # initialize variables
    X_g = []
    G = []

    # get properties
    P, Thres, Axes = globals()['properties_' + grad_func](prop_model, prop_params)

    # switch variables for property function
    if grad_func == '1D':
        x_name = prop_params['X']['name']
        X = Axes['x']
        # calculate gradients
        Grads = np.gradient(P, X)
    elif grad_func == '1D_multi':
        x_name = prop_params['Z']['name']
        X = Axes['z']
    elif grad_func == '2D':
        x_name = prop_params['Y']['name']
        X = Axes['y']

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X)

    # display initialization
    logger.info('Initializing {prop_name} gradient calculation...\t\n'.format(prop_name=prop_name))
    
    # for variation in X
    for i in range(len(X)):
        # calculate progress
        progress = float(i) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model for gradient calculation
        model.p[x_name] = X[i]

        # get parameters from model
        grad_params = model.get_grad_params()

        if grad_func == '1D':
            # obtain calculated gradients
            grad = Grads[i] / grad_params['divisor']
        else:
            # get gradient at particular value
            grad = get_grad(P[i], Axes['x'], grad_params)

        # update lists for line plot
        X_g.append(X[i])
        G.append(grad)

        # TODO: handle scatter plot
        
        # update plot
        if plot:
            plotter.update(X_g, G)
    
    # display completion
    logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {G}\t\n'.format(G=G))

    # update plot
    if plot:
        plotter.update(X_g, G, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = []
    Axes['z'] = []

    # return data
    return G, Thres, Axes

def properties_grad_1D_multi(model, prop_params, plot=False, plot_params=None):
    """Function to calculate a gradient of properties versus a continuous variable for multiple discrete variables.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    prop_params : dict
        Parameters for the property.

    plot : boolean
        Option to plot the property.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    P : list
        Properties calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    grad_func   = prop_params['grad_func']
    prop_model  = model
    z_name      = prop_params['Z']['name']
    z_unit      = prop_params['Z']['unit']
    Z           = prop_params['Z']['values']
    if plot:
        plot_params['legend'] = ['{name} = {value} {unit}'.format(name=z_name, value=z, unit=z_unit) for z in Z]

    # initialize variables
    X_g = []
    G = []

    # switch variables for property function
    if grad_func == '1D_multi':
        # get properties
        P, Thres, Axes = properties_1D_multi(prop_model, prop_params)
        x_name = prop_params['X']['name']
        X = Axes['x']
    elif grad_func == '2D':
        x_name = prop_params['Y']['name']
        y_min = prop_params['Y']['min']
        y_max = prop_params['Y']['max']
        y_steps = prop_params['Y']['steps']
        num_decimals = int(np.ceil(np.log10((y_steps - 1) / (y_max - y_min))))
        X = np.around(np.linspace(y_min, y_max, y_steps), num_decimals).tolist()

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X, Z=Z)

    # for variation in Z
    for j in range(len(Z)):
        # display initialization
        logger.info('Initializing {prop_name} gradient calculation for {z_name} = {z} {z_unit}\t\n'.format(prop_name=prop_name, z_name=z_name, z=Z[j], z_unit=z_unit))

        # switch variables for property function
        if grad_func == '1D_multi':
            # calculate gradients
            Grads = np.gradient(P[j], Axes['x'])
        elif grad_func == '2D':
            # update model for property calculation
            prop_model.p[z_name] = Z[j]
            # get properties
            P, Thres, Axes = properties_2D(prop_model, prop_params)

        # for variation in X 
        for i in range(len(X)):
            # calculate progress
            progress = (float(i) / float(len(X))) * 100
            # display progress
            logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model for gradient calculation
            model.p[x_name] = X[i]
            model.p[z_name] = Z[j]

            # get parameters from model
            grad_params = model.get_grad_params()

            if grad_func == '1D_multi':
                # obtain calculated gradients
                grad = Grads[i] / grad_params['divisor']
            else:
                # get gradient at particular value
                grad = get_grad(P[i], Axes['x'], grad_params)

            # update lists for line plot
            X_g.append(X[i])
            G.append(grad)
            
            # update plot
            if plot:
                plotter.update(X_g, G)
    
        # display completion
        logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {G}\n'.format(G=G))

    # update plot
    if plot:
        plotter.update(X_g, G, head=False, hold=True)

    # reshape list
    G = np.reshape(G, (len(Z), len(X))).tolist()

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = []
    Axes['z'] = Z

    # return data
    return G, Thres, Axes

def properties_grad_2D(model, prop_params, plot=False, plot_params=None):
    """Function to calculate a gradient of properties versus two continuous variables.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    prop_params : dict
        Parameters for the property.

    plot : boolean
        Option to plot the property.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    P : list
        Properties calculated.

    Thres : dict
        Threshold values of the variables used.

    Axes : dict
        Axes points used to calculate the properties.
    """

    # TODO: assert property and plot parameters

    # extract frequently used variables
    prop_name   = prop_params['name']
    prop_model  = model
    y_name      = prop_params['Y']['name']

    # TODO: handle 3D plots

    # get properties
    P, Thres, Axes = properties_2D(prop_model, prop_params)

    # initialize variables
    X = Axes['x']
    Y = Axes['y']
    G = np.empty((len(Y), len(X)))
    G[:] = np.NaN

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=X, Y=Y, Z=G)

    # display initialization
    logger.info('Initializing {prop_name} gradient calculation...\t\n'.format(prop_name=prop_name))
        
    # for variation in Y
    for j in range(len(Y)):
        # calculate progress
        progress = float(j) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model for gradient calculation
        model.p[y_name] = Y[j]

        # get parameters from model
        grad_params = model.get_grad_params()

        # calculate gradients
        Grads = np.gradient(P[j], X) / grad_params['divisor']

        # update lists
        G[j] = Grads.tolist()
            
        # update plot
        if plot:
            plotter.update(Z=G)
    
    # display completion
    logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {Grads}\t\n'.format(Grads=Grads))

    # update plot
    if plot:
        plotter.update(Z=G, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = X
    Axes['y'] = Y
    Axes['z'] = []

    # return data
    return G, Thres, Axes


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

    # TODO: handle single parameter case

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
