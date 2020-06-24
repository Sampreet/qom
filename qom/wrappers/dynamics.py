#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Wrapper modules for dynamics."""

__name__    = 'qom.wrappers.dynamics'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-05-01'
__updated__ = '2020-06-24'

# dependencies
import logging
import os
from numpy import array, linspace, load, real, save
from scipy.integrate import ode

# dev dependencies
from qom.measures import corr
from qom.ui import figure

# module logger
logger = logging.getLogger(__name__)

def measure(model, measure_code, measure_data, solver_type='complex', cache=True, dir_name='data', plot=False):
    """Function to obtain the dynamics of a quantum correlation measure.

    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    measure_code : str
        Short code for the measure.
    
    measure_data : dict
        Data for the calculation of measure.

    solver_type : str
        Type of solver ('real' or 'complex').

    cache : boolean
        Option to cache data.

    dir_name: str
        Directory name to cache data.

    plot: boolean
        Option to plot the measure dynamics.

    Returns
    -------
    M : float
        Values of the measure.
    """

    # extract frequently used variables
    measure_params = measure_data['params']
    plot_params = measure_data['figure']['dynamics']
    num_modes = measure_params['num_modes']

    # display initialization
    logger.info('Initializing {measure_name} calculation for {model_name} model:\n\tModel Parameters:\n\t\t{model_params}\n\tMeasure Parameters:\n\t\t{measure_params}\n\tPlot Parameters:\n\t\t{plot_params}\n'.format(measure_name=measure_data['name'], model_name=model.NAME, model_params=model.p, measure_params=measure_params, plot_params=plot_params))

    # obtain all variables
    T, V = get_variables(model, measure_params['t_max'], measure_params['t_steps'], solver_type, cache, dir_name)

    # initialize plot
    if plot:
        plotter = figure.Plotter2D('line', plot_params)

    # initialize list
    M = []

    # for each time step, calculate the measure
    for i in range(len(V)):
        # calculate progress
        progress = float(i) / float(len(V)) * 100
        # display progress
        logger.info('Calculating the measure dynamics: Progress = {progress:3.2f}'.format(progress=progress))

        mat_Corr = real(V[i][num_modes:]).reshape([2*num_modes, 2*num_modes])

        # initialize measure
        m = 0
        # position of ith mode in the correlation matrix
        pos_i = 2*measure_params['mode_i']
        # position of jth mode in the correlation matrix 
        pos_j = 2*measure_params['mode_j']

        # quantum discord measure between ith and jth cavity
        if measure_code == 'corr_disc':
            m = corr.disc(mat_Corr, pos_i, pos_j)
        # entanglement measure between ith and jth cavity
        if measure_code == 'corr_entan_bi_log_neg':
            m = corr.entan_bi_log_neg(mat_Corr, pos_i, pos_j)
        # complete synchronization measure between ith and jth quadratures
        if measure_code == 'corr_sync_comp':
            m = corr.sync_comp(mat_Corr, pos_i, pos_j)
        # phase synchronization measure between ith and jth cavity
        if measure_code == 'corr_sync_phase':
            mode_i = V[i][measure_params['mode_i']]
            mode_j = V[i][measure_params['mode_j']]
            m = corr.sync_phase(mat_Corr, pos_i, pos_j, mode_i, mode_j)
        if measure_code == 'corr_sync_phase_rot':
            mode_i = V[i][measure_params['mode_i']]
            mode_j = V[i][measure_params['mode_j']]
            m = corr.sync_phase_rot(mat_Corr, pos_i, pos_j, mode_i, mode_j)
        
        # update list
        M.append(m)

        # update plot
        if plot:
            plotter.update(T[0:i + 1], M)

    
    # display completion
    logger.info('----------------Measure Dynamics Obtained---------------\n')

    # update plot
    if plot:
        plotter.update(T, M, head=False, hold=True)

    # values of the measure
    return T, M

def get_variables(model, t_max, t_steps, solver_type='complex', cache=True, dir_name='data'):
    """Function to obtain the dynamics of variables for a given model.

    Parameters
    ----------
    model : :class:`Model`
        Model of the system.

    t_max : float
        Maximum value of time.

    t_steps : *int*
        Number of steps to maximum value.

    solver_type : str
        Type of solver ('real' or 'complex').

    cache : boolean
        Option to cache data.

    dir_name: str
        Directory name to cache data.

    Returns
    -------
    T : list
        Times at which dynamics are obtained.

    V : list
        Dynamics of the variables.
    """

    # directory and file names for storing data
    dir_name += '\\' + model.CODE + '\\dynamics\\' + str(t_max) + '_' + str(t_steps) + '\\'
    file_name = 'V'
    for key in model.p:
        file_name += '_' + str(model.p[key])

    # if caching is enabled
    if (cache):
        # create directories
        try:
            os.makedirs(dir_name)
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=dir_name))
        
        # try loading data
        try:
            T = linspace(0, t_max, t_steps + 1)
            V = load(dir_name + file_name + '.npy')
        except IOError:
            # update log
            logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=file_name, dir_name=dir_name))
        else:
            # update log
            logger.info('----------------System Dynamics Obtained----------------\n')

            # return lists
            return T.tolist(), V.tolist()

    # get initial values and constants for the model
    v, c = model.get_initial_values_and_constants()

    # update log
    logger.debug('Obtaining the System Dynamics with initial values {model_variables} and constants {model_constants} and time parameters {time_params}\n'.format(model_variables=v, model_constants=c, time_params=[t_max, t_steps]))

    # initialize integrator
    integrator = None
    # initial time
    t = 0
    # time step
    dt = t_max / t_steps
    
    if solver_type == 'complex':
        # complex ode solver formalism
        integrator = ode(model.model_complex)
        integrator.set_integrator('zvode')
    else:
        # real-valued ode solver formalism
        integrator = ode(model.modelReal)
        
    # set initial values and constants
    integrator.set_initial_value(v, t)
    integrator.set_f_params(c)

    # initialize lists
    T = [t]
    V = [v]

    # for each time step, calculate the integration values
    for i in range(1, t_steps + 1):
        # update progress
        progress = float(i)/float(t_steps) * 100
        # display progress
        logger.info('Obtaining the system dynamics: Progress = {progress:3.2f}'.format(progress=progress))

        # integrate
        t = t + dt
        v = integrator.integrate(t)

        # update log
        logger.debug('t = {}\tv = {}'.format(t, v))

        # update lists
        T.append(t)
        V.append(v)

    # display completion
    logger.info('----------------System Dynamics Obtained----------------\n')

    # if caching is enabled
    if (cache):
        # save data to file
        save(dir_name + file_name, array(V))

    # times and dynamics
    return T, V