#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Wrapper modules for dynamics."""

__name__    = 'qom.wrappers.dynamics'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-05-01'
__updated__ = '2020-09-04'

# dependencies
import logging
import numpy as np
import os
import scipy.integrate as si

# dev dependencies
from qom.measures import corr, diff
from qom.legacy.ui import figure

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
    return globals()[data['dyna_params']['func']](model, data['dyna_params'], data['meas_params'], data['plot'], data['plot_params'])

def dynamics_measure(model, dyna_params, meas_params, plot=False, plot_params=None):
    """Function to calculate the dynamics of a measure.

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
    if 'dir' not in dyna_params or dyna_params['dir'] == '':
        dir_name = 'data'
    else:
        dir_name = dyna_params['dir']
    t_min   = dyna_params['T']['min']
    t_max   = dyna_params['T']['max']
    t_steps = dyna_params['T']['steps']

    # directory and file names for storing data
    dir_name += '\\' + model.CODE + '\\dynamics\\' + str(t_min) + '_' + str(t_max) + '_' + str(t_steps) + '\\'
    file_name_v = 'V'
    for key in model.p:
        file_name_v += '_' + str(model.p[key])
    file_name_d = meas_params['type'] + '_' + meas_params['code']
    if 'arg_str' in meas_params:
        file_name_d += '_' + meas_params['arg_str']
    for key in model.p:
        file_name_d += '_' + str(model.p[key])

    # initialize variables
    found_saved_v = False
    found_saved_d = False

    # if caching is enabled
    if cache:
        # update log
        logger.debug('Checking for saved measure dynamics...\n')

        # create directories
        try:
            os.makedirs(dir_name)
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=dir_name))
        
        # try loading system dynamics data
        try:
            V = np.load(dir_name + file_name_v + '.npy').tolist()
        except IOError:
            # update log
            logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=file_name_v, dir_name=dir_name))
        else:
            # generate time array
            num_decimals = int(np.ceil(np.log10((t_steps - 1) / (t_max - t_min))))
            T = np.around(np.linspace(t_min, t_max, t_steps), num_decimals).tolist()
            # update flag
            found_saved_v = True

        # try loading measure dynamics data
        try:
            D = np.load(dir_name + file_name_d + '.npy').tolist()
        except IOError:
            # update log
            logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=file_name_d, dir_name=dir_name))
        else:
            # update flag
            found_saved_d = True

    if not (found_saved_v and found_saved_d):
        # display initialization
        logger.info('Calculating dynamics for {model_name}...\n\tModel Parameters:\n\t\t{model_params}\n\tMeasure Parameters:\n\t\t{meas_params}\n\tDynamics Parameters:\n\t\t{dyna_params}\n'.format(model_name=model.NAME, model_params=model.p, meas_params=meas_params, dyna_params=dyna_params))

    if not found_saved_v:
        # get dynamics of all variables
        T, V = get_dynamics(model, dyna_params)

        # display completion
        logger.debug('----------------System Dynamics Obtained----------------\n')

        # if caching is enabled
        if cache:
            # save system dynamics data to file
            np.save(dir_name + file_name_v, np.array(V))

    if not found_saved_d:
        # calculate measures
        if meas_params['type'] == 'corr':
            D = corr.calculate(V, meas_params)
        elif meas_params['type'] == 'diff':
            D = diff.calculate(V, meas_params)
            
        # display completion
        logger.debug('----------------Measure Dynamics Obtained---------------\n')

        # if caching is enabled
        if cache:
            # save measure dynamics data to file
            np.save(dir_name + file_name_d, np.array(D))
            
    if not (found_saved_v and found_saved_d):
        # display completion
        logger.info('----------------Dynamics Calculated---------------\n')

    # display plot
    if plot:
        plotter = figure.Plotter2D(plot_params, X=T)
        plotter.update(T, D, head=False, hold=True)

    # axes dictionary
    Axes = {}
    Axes['X'] = T
    Axes['Y'] = []
    Axes['Z'] = []

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
    t_min   = dyna_params['T']['min']
    t_max   = dyna_params['T']['max']
    t_steps = dyna_params['T']['steps']

    # initialize variables
    num_decimals = int(np.ceil(np.log10((t_steps - 1) / (t_max - t_min))))
    T = np.around(np.linspace(t_min, t_max, t_steps), num_decimals).tolist()

    # get initial values and constants for the model
    v, c = model.get_initial_values_and_constants()

    # initialize integrator
    integrator = si.ode(getattr(model, 'model_' + solver_type))
    # for complex ode solver
    if solver_type.find('complex') != -1:
        integrator.set_integrator('zvode')
        
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

    return T, V