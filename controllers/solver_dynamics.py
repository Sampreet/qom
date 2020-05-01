#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Modules to calculate dynamics."""

__authors__ = ['Sampreet Kalita']
__created__ = '2020-05-01'
__updated__ = '2020-05-01'

# dependencies
import numpy as np
import os
import scipy.integrate as si

from helpers import logger_console
from modules.measures import quantum_correlations

def get_quantum_correlation_measure_dynamics(V, measure_code, measure_data, debug=False):
    """Function to obtain the dynamics of a quantum correlation measure.

    Parameters
    ----------
    V : list
        Modes and Correlation matrices.

    measure_code : str
        Short code for the measure.
    
    measure_data : dict
        Data for the measure.

    debug : boolean
        Option to enable DEBUG log level.

    Returns
    -------
    M : float
        Values of the measure.
    """

    # initialize logger
    clh = logger_console.get_logger(__name__, 'short', debug)

    # extract frequently used variables
    measure_params = measure_data['params']
    num_modes = measure_params['num_modes']

    # display initialization
    clh.info('Initializing {measure_name} calculation with parameters {measure_params}\n'.format(measure_name=measure_data['name'], measure_params=measure_params))

    # initialize list
    M = []
    # for each time step, calculate the complete synchronization values
    for i in range(len(V)):
        # calculate progress
        progress = float(i)/float(len(V)) * 100
        # display progress
        clh.info('Calculating the measure dynamics: Progress={progress:3.2f}'.format(progress=progress))

        mat_Corr = np.real(V[i][num_modes:]).reshape([2*num_modes, 2*num_modes])

        # calculate property
        prop = 0
        # position of ith mode in the correlation matrix
        pos_i = 2*measure_params['mode_i']
        # position of jth mode in the correlation matrix 
        pos_j = 2*measure_params['mode_j']

        # complete synchronization measure between ith and jth quadratures
        if measure_code == 'quant_sync_comp':
            prop = quantum_correlations.QuantumSynchronization().calculate_comp_sync(mat_Corr, pos_i, pos_j)
        # phase synchronization measure between ith and jth cavity
        if measure_code == 'quant_sync_phase':
            arg_i = np.angle(V[i][measure_params['mode_i']])
            arg_j = np.angle(V[i][measure_params['mode_j']])
            prop = quantum_correlations.QuantumSynchronization().calculate_phase_sync(mat_Corr, pos_i, pos_j, arg_i, arg_j)
        # quantum discord measure between ith and jth cavity
        if measure_code == 'quant_disc':
            prop = quantum_correlations.QuantumDiscord().calculate(mat_Corr, pos_i, pos_j)
        # entanglement measure between ith and jth cavity
        if measure_code == 'quant_entan':
            prop = quantum_correlations.QuantumEntanglement().calculate_log_neg(mat_Corr, pos_i, pos_j)
        
        # append to list
        M.append(prop)
    
    # display completion
    clh.info('----------------Measure Dynamics Obtained---------------\n')

    # return list
    return M

def get_system_dynamics(model, t_max, t_steps, solver_type='complex', debug=False):
    """Function to obtain the dynamics of variables for a given model.

    Parameters
    ----------
    model : :class:`Model`

    time_params : dict
        Time parameters for integration.

    solver_type : str
        Type of solver ('real' or 'complex').

    debug : boolean
        Option to enable DEBUG log level.

    Returns
    -------
    T : list
        Times at which dynamics are obtained.

    V : list
        Dynamics of the variables.
    """

    # initialize logger
    clh = logger_console.get_logger(__name__, 'short', debug)

    # display initialization
    clh.info('Intializing {model_name} model with parameters {model_params}\n'.format(model_name=model.NAME, model_params=model.p))

    # directory and file names for storing data
    dir_name = 'data\\' + model.CODE + '\\' + str(t_max) + '_' + str(t_steps) + '\\'
    file_name = 'dynamics'
    for key in model.p:
        file_name += '_' + str(model.p[key])

    # create directories
    try:
        os.makedirs(dir_name)
    except FileExistsError:
        # update log
        clh.debug('Directory {dir_name} already exists\n'.format(dir_name=dir_name))
    
    # try loading data
    try:
        T = np.linspace(0, t_max, t_steps + 1)
        V = np.load(dir_name + file_name + '.npy')
    except IOError:
        # update log
        clh.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=file_name, dir_name=dir_name))
    else:
        # update log
        clh.info('----------------System Dynamics Obtained----------------\n')

        # return lists
        return T.tolist(), V.tolist()

    # update log
    clh.debug('Obtaining the System Dynamics with initial values {model_variables} and constants {model_constants} and time parameters {time_params}\n'.format(model_variables=model.v, model_constants=model.c, time_params=[t_max, t_steps]))

    # initialize integrator
    integrator = None
    # initial time
    t = 0
    # time step
    dt = t_max / t_steps
    
    if solver_type == 'complex':
        # complex ode solver formalism
        integrator = si.ode(model.modelComplex)
        integrator.set_integrator('zvode')
    else:
        # real-valued ode solver formalism
        integrator = si.ode(model.modelReal)
        
    # set initial values and constants
    integrator.set_initial_value(model.v, t)
    integrator.set_f_params(model.c)

    # initialize lists
    T = [t]
    V = [model.v]

    # for each time step, calculate the integration values
    for i in range(1, t_steps + 1):
        # update progress
        progress = float(i)/float(t_steps) * 100
        # display progress
        clh.info('Obtaining the system dynamics: Progress = {progress:3.2f}'.format(progress=progress))

        # integrate
        t = t + dt
        v = integrator.integrate(t)

        # update log
        clh.debug('t = {}\tv = {}'.format(t, v))

        # update lists
        T.append(t)
        V.append(v)

    # display completion
    clh.info('----------------System Dynamics Obtained----------------\n')

    # save data to file
    np.save(dir_name + file_name, np.array(V))

    # return list
    return T, V