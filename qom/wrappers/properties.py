#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for properties."""

__name__    = 'qom.wrappers.properties'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-15'
__updated__ = '2020-06-24'

# dependencies
import logging
import os
from numpy import around, ceil, empty, imag, linspace, log10, NaN, real

# dev dependencies
from qom.ui import figure

# module logger
logger = logging.getLogger(__name__)

def property_1D(model, property_code, property_data, thres_mode='max_min', plot=True, plot_type='line'):
    """Function to calculate a property versus a continuous variable.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    property_code: str
        Short code for the property.

    property_data: str
        Data for the calculation of property.

    thres_mode: str
        Mode of calculation of the threshold values:
            max_min: Minimum value of variable for which property attains maximum value.
            max_max: Maximum value of variable for which property attains maximum value.

    plot: boolean
        Option to plot the property.

    plot_type: str
        Option for type of plot:
            line: Line plot.
            scatter: Scatter plot.

    Returns
    -------
    X : list
        Values of the first variable at which the proprety is calculated.

    P : list
        Properties calculated.

    Thres: dict
        Threshold values of the variables calculated.
    """

    # extract frequently used variables
    plot_params = property_data['figure']['1D']
    x_name = plot_params['X']['name']
    x_min = plot_params['X']['min']
    x_max = plot_params['X']['max']
    x_steps = plot_params['X']['steps']

    # display initialization
    logger.info('Initializing {property_name} calculation\n'.format(property_name=property_data['name']))

    # initialize variable
    num_decimals = int(ceil(log10((x_steps - 1) / (x_max - x_min))))
    X = around(linspace(x_min, x_max, x_steps), num_decimals)

    # initialize threshold values
    Thres = {}
    Thres[x_name] = x_min - 1

    # threshold values
    if thres_mode.index('max_') != -1:
        # max value of property
        p_max = 0

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_type, plot_params, X=X)

    # initialize lists
    X_p = []
    P = []
    # for each variable value, calculate the property
    for i in range(len(X)):
        # calculate progress
        progress = float(i) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # update model
        model.p[x_name] = X[i]

        # if stability state
        if property_code == 'bis':
            # obtain mean occupancy number
            N = model.get_num()

            # get bistability condition
            p = 1 if len(N) == 3 else 0
    
            # update lists
            X_p.append(X[i])
            P.append(p)

            # update thresholds if multistable
            if p == 1:
                if Thres[x_name] < x_min or abs(Thres[x_name]) > abs(X[i]):
                    Thres[x_name] = X[i]

        # if imaginary part of exponent
        if property_code == 'exp_im':
            # obtain complex exponents as list
            Exp = model.get_exp()
            # obtain imaginary part
            Exp_im = [imag(exp) for exp in Exp]

            # update lists
            X_p += [X[i] for e in Exp_im]
            P += Exp_im
            
            # get maximum value of imaginary part
            p = max(Exp_im)

            # update thresholds
            if thres_mode == 'max_min' and p != 0 and p > p_max:
                p_max = p
                Thres[x_name] = X[i]
            if thres_mode == 'max_max' and p != 0 and p >= p_max:
                p_max = p
                Thres[x_name] = X[i]

        # if real part of exponent
        if property_code == 'exp_re':
            # obtain real exponents as list
            Exp = model.get_exp()
            # obtain real part
            Exp_re = [real(exp) for exp in Exp]

            # update lists
            X_p += [X[i] for e in Exp_re]
            P += Exp_re

            # get maximum value of real part
            p = max(Exp_re)

            # update thresholds
            if thres_mode == 'max_min' and p != 0 and p > p_max:
                p_max = p
                Thres[x_name] = X[i]
            if thres_mode == 'max_max' and p != 0 and p >= p_max:
                p_max = p
                Thres[x_name] = X[i]

        # if mean occupancy number
        if property_code == 'num':
            # obtain mean occupancy number
            N = model.get_num()

            # update lists
            X_p += [X[i] for n in N]
            P += N

            # update thresholds
            if thres_mode == 'max_min' and max(N) != 0 and max(N) > p_max:
                p_max = max(N)
                Thres[x_name] = X[i]
            if thres_mode == 'max_max' and max(N) != 0 and max(N) >= p_max:
                p_max = max(N)
                Thres[x_name] = X[i]

        # if stability state
        if property_code == 'trans':
            # get property
            p = model.get_trans()

            # update thresholds
            if thres_mode == 'max_min' and p != 0 and p > p_max:
                p_max = p
                Thres[x_name] = X[i]
            if thres_mode == 'max_max' and p != 0 and p >= p_max:
                p_max = p
                Thres[x_name] = X[i]
    
            # update list
            X_p.append(X[i])
            P.append(p)

        # update plot
        if plot:
            plotter.update(X_p, P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(X_p, P, head=False, hold=True)

    # values of the property
    return X, P, Thres

def property_2D(model, property_code, property_data, thres_mode='max_min', plot=True, plot_type='pcolormesh'):
    """Function to calculate a property versus a continuous variable.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    property_code: str
        Short code for the property.

    property_data: str
        Data for the property.

    thres_mode: str
        Mode of calculation of the threshold values:
            max_min: Minimum value of variable for which property attains maximum value.
            max_max: Maximum value of variable for which property attains maximum value.

    plot: boolean
        Option to plot the property.

    plot_type: str
        Option for type of plot:
            pcolormesh: Pcolormesh plot.

    Returns
    -------
    X : list
        Values of the first variable at which the proprety is calculated.

    Y : list
        Values of the second variable at which the proprety is calculated.

    P : list
        Properties calculated.

    Thres: dict
        Threshold values of the variables calculated.
    """

    # extract frequently used variables
    plot_params = property_data['figure']['2D']
    x_name = plot_params['X']['name']
    x_min = plot_params['X']['min']
    x_max = plot_params['X']['max']
    x_steps = plot_params['X']['steps']
    y_name = plot_params['Y']['name']
    y_min = plot_params['Y']['min']
    y_max = plot_params['Y']['max']
    y_steps = plot_params['Y']['steps']

    # display initialization
    logger.info('Initializing {property_name} calculation\n'.format(property_name=property_data['name']))

    # initialize variables
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
        # max value of property
        p_max = 0

    # initialize list
    P = empty((len(Y), len(X)))
    P[:] = NaN

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_type, plot_params, X=X, Y=Y, Z=P)

    # for each variable value, calculate the property
    for j in range(len(Y)):
        # calculate progress
        progress = float(j) / float(len(Y)) * 100
        # display progress
        logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))
        
        for i in range(len(X)):
            # initialize measure
            p = 0

            # update model
            model.p[x_name] = X[i]
            model.p[y_name] = Y[j]

            # if stability state
            if property_code == 'bis':
                # obtain mean occupancy number
                N = model.get_num()

                # get bistability condition
                p = 1 if len(N) == 3 else 0

                # update thresholds if multistable
                if p == 1:
                    if Thres[x_name] < x_min or abs(Thres[x_name]) > abs(X[i]):
                        Thres[x_name] = X[i]
                    if Thres[y_name] < y_min or abs(Thres[y_name]) > abs(Y[j]):
                        Thres[y_name] = Y[j]

            # if imaginary part of exponent
            if property_code == 'exp_im':
                # obtain complex exponents as list
                Exp = model.get_exp()
                # obtain imaginary part
                Exp_im = [imag(exp) for exp in Exp]
                
                # get maximum value of imaginary part
                p = max(Exp_im)

                # update thresholds
                if thres_mode == 'max_min' and p != 0 and p > p_max:
                    p_max = p
                    Thres[x_name] = X[i]
                if thres_mode == 'max_max' and p != 0 and p >= p_max:
                    p_max = p
                    Thres[x_name] = X[i]

            # if real part of exponent
            if property_code == 'exp_re':
                # obtain real exponents as list
                Exp = model.get_exp()
                # obtain real part
                Exp_re = [real(exp) for exp in Exp]

                # get maximum value of real part
                p = max(Exp_re)

                # update thresholds
                if thres_mode == 'max_min' and p != 0 and p > p_max:
                    p_max = p
                    Thres[x_name] = X[i]
                if thres_mode == 'max_max' and p != 0 and p >= p_max:
                    p_max = p
                    Thres[x_name] = X[i]

            # if mean occupancy number
            if property_code == 'num':
                # obtain mean occupancy number
                N = model.get_num()

                # get maximum value of N
                p = max(N)

                # update thresholds
                if thres_mode == 'max_min' and p != 0 and p > p_max:
                    p_max = p
                    Thres[x_name] = X[i]
                if thres_mode == 'max_max' and p != 0 and p >= p_max:
                    p_max = p
                    Thres[x_name] = X[i]

            # if stability state
            if property_code == 'trans':
                # get property
                p = model.get_trans()

                # update thresholds
                if thres_mode == 'max_min' and p != 0 and p > p_max:
                    p_max = p
                    Thres[x_name] = X[i]
                    Thres[y_name] = Y[j]
                if thres_mode == 'max_max' and p != 0 and p >= p_max:
                    p_max = p
                    Thres[x_name] = X[i]
                    Thres[y_name] = Y[j]

            # update temp list
            P[j][i] = p

            # update plot
            if plot:
                plotter.update(Z=P)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\n'.format(Thres=Thres))

    # update plot
    if plot:
        plotter.update(Z=P, head=False, hold=True)

    # values of the property
    return X, Y, P, Thres