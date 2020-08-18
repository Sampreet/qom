#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for dynamics."""

__name__    = 'qom.wrappers.dynamics'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-05-01'
__updated__ = '2020-08-18'

# dependencies
import logging
import numpy as np
import os
import scipy.integrate as si

# dev dependencies
from qom.measures import corr
from qom.ui import figure

# module logger
logger = logging.getLogger(__name__)

def calculate(model, data):
    """Wrapper function to switch functions for calculation of dynamics.
    
    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    data : dict
        Data for the calculation.

    Returns
    -------
    data : list
        Data of the dynamics calculated.
    """

    # get dynamics
    return globals()[data['func']](model, data['dyna_params'], data['meas_params'], data['plot'], data['plot_params'])

def dynamics_measure(model, dyna_params, meas_params, plot=False, plot_params=None):
    """Function to calculate the dynamics of a quantum correlation measure.

    Parameters
    ----------
    model : :class:`Model`
        Model of the system.
    
    dyna_params : dict
        Parameters for the calculation of dynamics.
    
    meas_params : dict
        Parameters for the calculation of measures.

    plot : boolean
        Option to plot the dynamics.

    plot_params : dict
        Parameters for the plot.

    Returns
    -------
    D : list
        Dynamics of the measure.

    V : list
        Dynamics of the variables.

    Axes : dict
        Axes points used to calculate the dynamics.
    """

    # extract frequently used variables
    if 'cache' in dyna_params and dyna_params['cache'] == True:
        cache = True
    else:
        cache = False
    if 'dir_name' not in dyna_params or dyna_params['dir_name'] == '':
        dir_name = 'data'
    else:
        dir_name = dyna_params['dir_name']
    t_min   = dyna_params['T']['min']
    t_max   = dyna_params['T']['max']
    t_steps = dyna_params['T']['steps']

    # initialize variables
    X_d = []
    D   = []

    # directory and file names for storing data
    dir_name += '\\' + model.CODE + '\\dynamics\\' + str(t_min) + '_' + str(t_max) + '_' + str(t_steps) + '\\'
    file_name = meas_params['type'] + '_' + meas_params['code']
    for key in model.p:
        file_name += '_' + str(model.p[key])

    # get dynamics of all variables
    T, V = get_dynamics(model, dyna_params)

    # initialize plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=T)

    # if caching is enabled
    if cache:
        # create directories
        try:
            os.makedirs(dir_name)
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=dir_name))
        
        # try loading data
        try:
            D = np.load(dir_name + file_name + '.npy').tolist()
        except IOError:
            # update log
            logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=file_name, dir_name=dir_name))
        else:
            # update log
            logger.info('----------------Measure Dynamics Obtained----------------\n')

            # update plot
            if plot:
                plotter.update(T, D, head=False, hold=True)

            # axes dictionary
            Axes = {}
            Axes['x'] = T
            Axes['y'] = []
            Axes['z'] = []

            # return data
            return D, V, Axes

    # display initialization
    logger.info('Initializing dynamics calculation of {meas_name} for {model_name} model:\n\tModel Parameters:\n\t\t{model_params}\n\tMeasure Parameters:\n\t\t{meas_params}\n\tDynamics Parameters:\n\t\t{dyna_params}\n'.format(meas_name=meas_params['name'], model_name=model.NAME, model_params=model.p, meas_params=meas_params, dyna_params=dyna_params))

    # for each time step, calculate the measure
    for i in range(len(V)):
        # calculate progress
        progress = float(i) / float(len(V)) * 100
        # display progress
        logger.info('Calculating the measure dynamics: Progress = {progress:3.2f}'.format(progress=progress))

        # initialize value
        d = 0

        # calculate measure
        if meas_params['type'] == 'corr':
            d = corr.calculate(V[i], meas_params)
        
        # update lists
        X_d.append(T[i])
        D.append(d)

        # update plot
        if plot:
            plotter.update(X_d, D)
    
    # display completion
    logger.info('----------------Measure Dynamics Obtained---------------\n')

    # if caching is enabled
    if (cache):
        # save data to file
        np.save(dir_name + file_name, np.array(D))

    # update plot
    if plot:
        plotter.update(X_d, D, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['x'] = T
    Axes['y'] = []
    Axes['z'] = []

    # return data
    return D, V, Axes

def get_dynamics(model, dyna_params):
    """Function to calculate the dynamics of variables for a given model using scipy.integrate.

    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    dyna_params : dict
        Parameters for the calculation.

    Returns
    -------
    T : list
        Times at which dynamics are calculated.

    V : list
        Dynamics of the variables.
    """

    # extract frequently used variables
    solver_type = dyna_params['solver_type']
    if 'cache' in dyna_params and dyna_params['cache'] == True:
        cache = True
    else:
        cache = False
    if 'dir_name' not in dyna_params or dyna_params['dir_name'] == '':
        dir_name = 'data'
    else:
        dir_name = dyna_params['dir_name']
    t_min   = dyna_params['T']['min']
    t_max   = dyna_params['T']['max']
    t_steps = dyna_params['T']['steps']

    # initialize variables
    num_decimals = int(np.ceil(np.log10((t_steps - 1) / (t_max - t_min))))
    T = np.around(np.linspace(t_min, t_max, t_steps), num_decimals).tolist()

    # directory and file names for storing data
    dir_name += '\\' + model.CODE + '\\dynamics\\' + str(t_min) + '_' + str(t_max) + '_' + str(t_steps) + '\\'
    file_name = 'V'
    for key in model.p:
        file_name += '_' + str(model.p[key])

    # if caching is enabled
    if cache:
        # create directories
        try:
            os.makedirs(dir_name)
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=dir_name))
        
        # try loading data
        try:
            V = np.load(dir_name + file_name + '.npy').tolist()
        except IOError:
            # update log
            logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=file_name, dir_name=dir_name))
        else:
            # update log
            logger.info('----------------System Dynamics Obtained----------------\n')

            # return lists
            return T, V

    # get initial values and constants for the model
    v, c = model.get_initial_values_and_constants()

    # update log
    logger.debug('Obtaining the System Dynamics with initial values {model_variables} and constants {model_constants} and time parameters {time_params}\n'.format(model_variables=v, model_constants=c, time_params=[t_max, t_steps]))

    # initialize integrator
    integrator = None    
    if solver_type == 'complex':
        # complex ode solver formalism
        integrator = si.ode(model.model_complex)
        integrator.set_integrator('zvode')
    else:
        # real-valued ode solver formalism
        integrator = si.ode(model.modelReal)
        
    # set initial values and constants
    integrator.set_initial_value(v, t_min)
    integrator.set_f_params(c)

    # initialize lists
    V = [v]

    # for each time step, calculate the integration values
    for i in range(1, t_steps):
        # update progress
        progress = float(i)/float(t_steps) * 100
        # display progress
        logger.info('Obtaining the system dynamics: Progress = {progress:3.2f}'.format(progress=progress))

        # integrate
        t = T[i]
        v = integrator.integrate(t)

        # update log
        logger.debug('t = {}\tv = {}'.format(t, v))

        # update lists
        V.append(v)

    # display completion
    logger.info('----------------System Dynamics Obtained----------------\n')

    # if caching is enabled
    if (cache):
        # save data to file
        np.save(dir_name + file_name, np.array(V))

    return T, V