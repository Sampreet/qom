#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Looper functions for properties."""

__name__    = 'qom.loopers.properties'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-15'
__updated__ = '2020-10-22'

# dependencies
import copy
import logging
import numpy as np

# dev dependencies
from qom.numerics.calculators import get_grad
from qom.ui import Figure
from qom.ui.axes import MultiAxis, StaticAxis
from qom.utils.misc import get_index_threshold

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle scatter plots for gradient functions.
# TODO: Handle multi-value points for 1D and 2D functions.
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
    return globals()[data['prop_params']['func']](model, data['prop_params'], data.get('plot', False), data.get('plot_params', None))

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
            Axes points used to calculate the properties as lists.
    """

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    X           = StaticAxis(prop_params['X'])

    # initialize variables
    X_p = np.zeros([X.dim])
    P = np.zeros([X.dim])
    P[:] = np.NaN

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'line'
        figure = Figure(plot_params, X=X)

    # display initialization
    logger.info('Initializing {prop_name} property calculation...\t\n'.format(prop_name=prop_name))

    # for variation in X
    for i in range(X.dim):
        # calculate progress
        progress = float(i) / float(X.dim) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model
        model.params[X.var] = X.val[i]

        # get property from model
        p = getattr(model, prop_code)()

        # update lists for scatter plot
        if type(p) == list:
            X_p[i] = X.val[i]
            P[i] = p[0]
            if len(p) > 1:
                X_p = np.concatenate((X_p, [X.val[i] for l in range(len(p) - 1)]))
                P = np.concatenate((P, p[1:]))
        # update lists for line plot
        else:
            X_p[i] = X.val[i]
            P[i] = p

        # update plot
        if plot and plot_prog:
            figure.update(X_p, P, head=True, hold=False)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')
    
    thres_idx = get_index_threshold(P, thres_mode)

    Thres = {}
    Thres['value'] = P[thres_idx[0]]
    Thres[X.var] = X_p[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(X_p, P)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_p.tolist()

    # return data
    return P.tolist(), Thres, Axes

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
            Axes points used to calculate the properties as lists.
    """

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    X           = StaticAxis(prop_params['X'])
    Z           = MultiAxis(prop_params['Z'])

    # initialize variables
    X_p = np.zeros([Z.dim, X.dim])
    Z_p = np.zeros([Z.dim, X.dim])
    P = np.zeros([Z.dim, X.dim])
    P[:] = np.NaN

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'lines'
        figure = Figure(plot_params, X=X, Z=Z)

    # display initialization
    logger.info('Initializing {prop_name} property calculation...\t\n'.format(prop_name=prop_name))

    # for variation in X
    for i in range(X.dim):
        # for variation in Z
        for j in range(Z.dim):
            # calculate progress
            progress = ((float(i) + float(j) / float(Z.dim)) / float(X.dim)) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.params[X.var] = X.val[i]
            model.params[Z.var] = Z.val[j]

            # get property from model
            p = getattr(model, prop_code)()

            # update lists for multi-scatter plot
            if type(p) == list:
                X_p[j] += [X.val[i] for l in range(len(p))]
                Z_p[j] += [Z.val[j] for l in range(len(p))]
                P[j] += p
            # update lists for multi-line plot
            else:
                X_p[j][i] = X.val[i]
                Z_p[j][i] = Z.val[j]
                P[j][i] = p

        # update plot
        if plot and plot_prog:
            figure.update(X_p, P, head=True, hold=False)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')
    
    thres_idx = get_index_threshold(P, thres_mode)

    Thres = {}
    Thres['value'] = P[thres_idx[0]][thres_idx[1]]
    Thres[X.var] = X.val[thres_idx[1]]
    Thres[Z.var] = Z.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(X_p, P)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_p.tolist()
    Axes['Z'] = Z_p.tolist()

    # return data
    return P.tolist(), Thres, Axes

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
            Axes points used to calculate the properties as lists.
    """

    # extract frequently used variables
    prop_code   = prop_params['code']
    prop_name   = prop_params['name']
    thres_mode  = prop_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    X           = StaticAxis(prop_params['X'])
    Y           = StaticAxis(prop_params['Y'])

    # initialize variables
    X_p = np.zeros([Y.dim, X.dim])
    Y_p = np.zeros([Y.dim, X.dim])
    P = np.zeros([Y.dim, X.dim])
    P[:] = np.NaN

    for j in range(Y.dim):
        P[j] = [np.NaN for i in range(X.dim)]

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'pcolormesh'
        figure = Figure(plot_params, X=X, Y=Y)

    # display initialization
    logger.info('Initializing {prop_name} property calculation...\t\n'.format(prop_name=prop_name))

    # for variation in Y
    for j in range(Y.dim):
        # for variation in X
        for i in range(X.dim):
            # calculate progress
            progress = ((float(j) + float(i) / float(X.dim)) / float(Y.dim)) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model
            model.params[X.var] = X.val[i]
            model.params[Y.var] = Y.val[j]

            # get property from model
            p = getattr(model, prop_code)()

            if type(p) == list:
                if thres_mode.find('max_') != -1:
                    p = max(p)

            # update list
            X_p[j][i] = X.val[i]
            Y_p[j][i] = Y.val[j]
            P[j][i] = p

        # update plot
        if plot and plot_prog:
            figure.update(zs=P, hold=False)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\t\n')
    
    thres_idx = get_index_threshold(P, thres_mode)

    Thres = {}
    Thres['value'] = P[thres_idx[0]][thres_idx[1]]
    Thres[X.var] = X.val[thres_idx[1]]
    Thres[Y.var] = Y.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(zs=P)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_p.tolist()
    Axes['Y'] = Y_p.tolist()

    # return data
    return P.tolist(), Thres, Axes

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
            Axes points used to calculate the gradients as lists.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    grad_axis   = prop_params.get('grad_axis', 'X')
    thres_mode  = prop_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    prop_model  = copy.deepcopy(model)

    # switch variables for property function
    if grad_axis == 'X':
        # get properties
        P_values, Thres, Axes = properties_1D(prop_model, prop_params)
        # calculate gradients
        Grads = np.gradient(P_values, Axes['X'])
        X = StaticAxis(prop_params['X'])
    elif grad_axis == 'Y':
        # get properties
        P_values, Thres, Axes = properties_2D(prop_model, prop_params)
        X = StaticAxis(prop_params['Y'])

    # initialize variables
    X_g = np.zeros([X.dim])
    G = np.zeros([X.dim])
    G[:] = np.NaN

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'line'
        figure = Figure(plot_params, X=X)

    # display initialization
    logger.info('Initializing {prop_name} gradient calculation...\t\n'.format(prop_name=prop_name))
    
    # for variation in X
    for i in range(X.dim):
        # calculate progress
        progress = float(i) / float(X.dim) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model for gradient calculation
        model.params[X.var] = X.val[i]

        # get parameters from model
        _f_grad_params = getattr(model, 'get_grad_params', None)
        if _f_grad_params is not None:
            grad_params = _f_grad_params()
        else:
            grad_params = {
                'divisor': 1,
                'mode': 'at_position',
                'position': 0
            }

        if grad_axis == 'X':
            # obtain calculated gradients
            grad = Grads[i] / grad_params['divisor']
        elif grad_axis == 'Y':
            # get gradient at particular value
            grad = get_grad(P_values[i], Axes['X'][i], grad_params)

        # update lists for line plot
        X_g[i] = X.val[i]
        G[i] = grad
        
        # update plot
        if plot and plot_prog:
            figure.update(X_g, G, head=True, hold=False)
    
    # display completion
    logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {G}\n'.format(G=G))
    
    thres_idx = get_index_threshold(G, thres_mode)

    Thres = {}
    Thres['value'] = G[thres_idx[0]]
    Thres[X.var] = X.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(X_g, G)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_g.tolist()

    # return data
    return G.tolist(), Thres, Axes

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
            Axes points used to calculate the gradients as lists.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    grad_axis   = prop_params.get('grad_axis', 'X')
    thres_mode  = prop_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    X           = StaticAxis(prop_params[grad_axis])
    Z           = MultiAxis(prop_params['Z'])

    # initialize variables
    X_g = np.zeros([Z.dim, X.dim])
    Z_g = np.zeros([Z.dim, X.dim])
    G = np.zeros([Z.dim, X.dim])
    G[:] = np.NaN

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'lines'
        figure = Figure(plot_params, X=X, Z=Z)

    # for variation in Z
    for j in range(Z.dim):
        # display initialization
        logger.info('Initializing {prop_name} gradient calculation for {legend}\t\n'.format(prop_name=prop_name, legend=Z.legends[j]))

        # update model for property calculation
        prop_model = copy.deepcopy(model)
        prop_model.params[Z.var] = Z.val[j]

        # switch variables for property function
        if grad_axis == 'X':
            P_values, Thres, Axes = properties_1D(prop_model, prop_params)
            # calculate gradients
            Grads = np.gradient(P_values, Axes['X'])
        elif grad_axis == 'Y':
            # get properties
            P_values, Thres, Axes = properties_2D(prop_model, prop_params)

        # for variation in X 
        for i in range(X.dim):
            # calculate progress
            progress = (float(i) / float(X.dim)) * 100
            # display progress
            if int(progress * 1000) % 10 == 0:
                logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

            # update model for gradient calculation
            model.params[X.var] = X.val[i]
            model.params[Z.var] = Z.val[j]

            # get parameters from model
            _f_grad_params = getattr(model, 'get_grad_params', None)
            if _f_grad_params is not None:
                grad_params = _f_grad_params()
            else:
                grad_params = {
                    'divisor': 1,
                    'mode': 'at_position',
                    'position': 0
                }

            if grad_axis == 'X':
                # obtain calculated gradients
                grad = Grads[i] / grad_params['divisor']
            elif grad_axis == 'Y':
                # get gradient at particular value
                grad = get_grad(P_values[i], Axes['X'][i], grad_params)

            # update lists for line plot
            X_g[j][i] = X.val[i]
            Z_g[j][i] = Z.val[j]
            G[j][i] = grad
            
            # update plot
            if plot and plot_prog:
                figure.update(X_g, G, head=True, hold=False)
    
        # display completion
        logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {G}\n'.format(G=G))
    
    thres_idx = get_index_threshold(G, thres_mode)

    Thres = {}
    Thres['value'] = G[thres_idx[0]][thres_idx[1]]
    Thres[X.var] = X.val[thres_idx[1]]
    Thres[Z.var] = Z.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(X_g, G)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_g.tolist()
    Axes['Z'] = Z_g.tolist()

    # return data
    return G.tolist(), Thres, Axes

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
            Axes points used to calculate the gradients as lists.
    """

    # extract frequently used variables
    prop_name   = prop_params['name']
    thres_mode  = prop_params.get('thres_mode', 'max_min')
    plot_prog   = plot_params.get('progress', False) if plot_params != None else False
    prop_model  = copy.deepcopy(model)

    # get properties
    P_values, Thres, Axes = properties_2D(prop_model, prop_params)
    X = StaticAxis(prop_params['X'])
    Y = StaticAxis(prop_params['Y'])

    # initialize variables
    X_g = np.zeros([Y.dim, X.dim])
    Y_g = np.zeros([Y.dim, X.dim])
    G = np.zeros([Y.dim, X.dim])
    G[:] = np.NaN

    for j in range(Y.dim):
        G[j] = [np.NaN for i in range(X.dim)]

    # initialize plot
    if plot:
        if plot_params.get('type', None) is None:
            plot_params['type'] = 'pcolormesh'
        figure = Figure(plot_params, X=X, Y=Y)

    # display initialization
    logger.info('Initializing {prop_name} gradient calculation...\t\n'.format(prop_name=prop_name))
        
    # for variation in Y
    for j in range(Y.dim):
        # calculate progress
        progress = float(j) / float(Y.dim) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Calculating the gradient values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model for gradient calculation
        model.params[Y.var] = Y.val[j]

        # get parameters from model
        _f_grad_params = getattr(model, 'get_grad_params', None)
        if _f_grad_params is not None:
            grad_params = _f_grad_params()
        else:
            grad_params = {
                'divisor': 1,
                'mode': 'at_position',
                'position': 0
            }

        # calculate gradients
        Grads = np.gradient(P_values[j], X.val) / grad_params['divisor']

        # update lists
        X_g[j] = X.val
        Y_g[j] = [Y.val[j] for _ in range(X.dim)]
        G[j] = Grads.tolist()
            
        # update plot
        if plot and plot_prog:
            figure.update(zs=G, hold=False)
    
    # display completion
    logger.info('----------------Gradient Values Obtained----------------\t\n')

    # # display gradient values
    # logger.info('Gradient values: {Grads}\t\n'.format(Grads=Grads))
    
    thres_idx = get_index_threshold(G, thres_mode)

    Thres = {}
    Thres['value'] = G[thres_idx[0]][thres_idx[1]]
    Thres[X.var] = X.val[thres_idx[1]]
    Thres[Y.var] = Y.val[thres_idx[0]]

    # display threshold values
    logger.info('Threshold values: {Thres}\t\n'.format(Thres=Thres))

    # update plot
    if plot:
        figure.update(zs=G)

    # axes dictionary
    Axes = {}
    Axes['X'] = X_g.tolist()
    Axes['Y'] = Y_g.tolist()

    # return data
    return G.tolist(), Thres, Axes