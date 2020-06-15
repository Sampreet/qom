#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for continuous variations."""

__name__    = 'qom.wrappers.cvar'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-06-15'
__updated__ = '2020-06-15'

# dependencies
import logging
import os
from numpy import around, imag, linspace, log10, real, roots

# module logger
logger = logging.getLogger(__name__)

def property_1D(model, property_code, property_data, thres_mode='max_min'):
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
    property_params = property_data['params']['1D']
    x_name = property_params['X']['var_name']
    x_min = property_params['X']['var_min']
    x_max = property_params['X']['var_max']
    x_steps = property_params['X']['var_steps']

    # display initialization
    logger.info('Initializing {property_name} calculation with parameters {property_params}\n'.format(property_name=property_data['name'], property_params=property_params))

    # initialize variable
    num_decimals = int(around(log10((x_steps - 1) / (x_max - x_min))))
    X = around(linspace(x_min, x_max, x_steps), num_decimals)

    # initialize threshold values
    Thres = {}
    Thres[x_name] = x_min - 1

    if thres_mode.index('max_') != -1:
        # max value of property
        p_max = 0

    # initialize list
    P = []
    # for each variable value, calculate the property
    for i in range(len(X)):
        # calculate progress
        progress = float(i) / float(len(X)) * 100
        # display progress
        logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # initialize measure
        p = 0

        # update model
        model.p[x_name] = X[i]

        # if stability state
        if property_code == 'bis':
            # obtain coeffs
            coeffs = model.get_coeffs()
            # find root 
            N = roots(coeffs)
            # get state
            p = 1 if sum([1 if imag(n) == 0.0 else 0 for n in N]) == 3 else 0

            # update thresholds if multistable
            if p == 1:
                if Thres[x_name] < x_min or abs(Thres[x_name]) > abs(X[i]):
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
        P.append(p)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\n'.format(Thres=Thres))

    # values of the property
    return X, P, Thres

def property_2D(model, property_code, property_data, thres_mode='max_min'):
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
    property_params = property_data['params']['2D']
    x_name = property_params['X']['var_name']
    x_min = property_params['X']['var_min']
    x_max = property_params['X']['var_max']
    x_steps = property_params['X']['var_steps']
    y_name = property_params['Y']['var_name']
    y_min = property_params['Y']['var_min']
    y_max = property_params['Y']['var_max']
    y_steps = property_params['Y']['var_steps']

    # display initialization
    logger.info('Initializing {property_name} calculation with parameters {property_params}\n'.format(property_name=property_data['name'], property_params=property_params))

    # initialize variables
    num_decimals = int(around(log10((x_steps - 1) / (x_max - x_min))))
    X = around(linspace(x_min, x_max, x_steps), num_decimals)
    num_decimals = int(around(log10((y_steps - 1) / (y_max - y_min))))
    Y = around(linspace(y_min, y_max, y_steps), num_decimals)

    # initialize threshold values
    Thres = {}
    Thres[x_name] = x_min - 1
    Thres[y_name] = y_min - 1

    if thres_mode.index('max_') != -1:
        # max value of property
        p_max = 0

    # initialize list
    P = []
    # for each variable value, calculate the property
    for j in range(len(Y)):
        # calculate progress
        progress = float(j) / float(len(Y)) * 100
        # display progress
        logger.info('Calculating the property values: Progress = {progress:3.2f}'.format(progress=progress))

        # temp list to store properties
        temp = []
        
        for i in range(len(X)):
            # initialize measure
            p = 0

            # update model
            model.p[x_name] = X[i]
            model.p[y_name] = Y[j]

            # if stability state
            if property_code == 'bis':
                # obtain coeffs
                coeffs = model.get_coeffs()
                # find root 
                N = roots(coeffs)
                # get state
                p = 1 if sum([1 if imag(n) == 0.0 else 0 for n in N]) == 3 else 0

                # update thresholds if multistable
                if p == 1:
                    if Thres[x_name] < x_min or abs(Thres[x_name]) > abs(X[i]):
                        Thres[x_name] = X[i]
                    if Thres[y_name] < y_min or abs(Thres[y_name]) > abs(Y[j]):
                        Thres[y_name] = Y[j]

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
            temp.append(p)
    
        # update list
        P.append(temp)
    
    # display completion
    logger.info('----------------Property Values Obtained----------------\n')

    # display threshold values
    logger.info('Threshold values: {Thres}\n'.format(Thres=Thres))

    # values of the property
    return X, Y, P, Thres