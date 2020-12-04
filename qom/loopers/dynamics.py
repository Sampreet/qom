#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module containing looper functions for dynamics."""

__name__    = 'qom.loopers.dynamics'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-21'
__updated__ = '2020-12-04'

# dependencies
import logging
import numpy as np
import os

# dev dependencies
from qom.measures import correlations, differences
from qom.numerics import solvers
from qom.ui import Figure
from qom.ui.axes import MultiAxis, StaticAxis

# modules logger
logger = logging.getLogger(__name__)

# TODO: Add single-system legacy module.
# TODO: Optimize the workflow for `dynamics_measure`.
# TODO: Verify parametes.

def calculate(system, data):
    """Wrapper function to switch functions for calculation of dynamcis.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        System for the calculation.
    data : dict
        System data for the calculation.

    Returns
    -------
    data : list 
        Data of the dynamics calculated.
    """

    # get dynamics
    return globals()[data['dyna_params']['func']](system, data['dyna_params'], data['meas_params'], data.get('plot', False), data.get('plot_params', None))

def dynamics_measure(system, dyna_params, meas_params, plot=False, plot_params=None):
    """Function to calculate the dynamics of a measure for multiple systems.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        System for the calculation.
    dyna_params : dict
        Parameters for the calculation of dynamics.
    meas_params : dict
        Parameters for the calculation of measures.
    plot : boolean, optional
        Option to plot the dynamics.
    plot_params : dict, optional
        Parameters for the plot.

    Returns
    -------
    D_all : list
        Dynamics of the measures for all systems.
    V_all : list
        Dynamics of the variables for all systems.
    Axes : dict
        Axes points used to calculate the dynamics as lists.
    """

    # extract frequently used variables
    if 'cache' in dyna_params and dyna_params['cache'] == True:
        _cache = True
    else:
        _cache = False
    if 'dir' not in dyna_params or dyna_params['dir'] == '':
        _dir = 'data'
    else:
        _dir = dyna_params['dir']
    _file_v_prefix = 'V'
    _file_d_prefix = meas_params['type'] + '_' + meas_params['code']
    if 'arg_str' in meas_params:
        _file_d_prefix += '_' + meas_params['arg_str']

    # time axis
    T = StaticAxis(dyna_params['T'])

    # directory and file names for storing data
    _dir += '\\' + system.code + '\\dynamics\\' + str(T.val[0]) + '_' + str(T.val[-1]) + '_' + str(T.dim) + '\\'

    # variables parameter
    X = None
    if 'X' in meas_params:
        X = MultiAxis(meas_params['X'])
        var_params = {
            X.var: X.val
        }
        _v, _c = system.get_ivc_multi(var_params)
    else:
        _v, _c = system.get_ivc_multi()

    # constants
    _n_s = _c['n_s']
    _n_v = int(len(_v) / _n_s)

    if _cache: 
        # update log
        logger.debug('Checking for saved measure dynamics...\n')

        # create directories
        try:
            os.makedirs(_dir)
        except FileExistsError:
            # update log
            logger.debug('Directory {dir_name} already exists\n'.format(dir_name=_dir))

        # populate filenames
        _file_vs = list()
        _file_ds = list()
        for i in range(_c['n_s']):
            _file_v = _file_v_prefix
            _file_d = _file_d_prefix
            for val in _c['params'][i]:
                _file_v += '_' + str(val)
                _file_d += '_' + str(val)
            _file_vs.append(_file_v)
            _file_ds.append(_file_d)

        # variables to calculate dynamics
        _count = 0
        _v_todo = list()
        _c_todo = dict()
        for key in _c:
            if type(_c[key]) == list:
                _c_todo[key] = list()
                
        # filter calculated systems
        for i in range(_c['n_s']):
            # flag 
            todo = False
            # if system dynamics not calculated
            if not os.path.isfile(_dir + _file_vs[i] + '.npy'):
                # update log
                logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=_file_vs[i], dir_name=_dir))

                todo = True
                
            # if measure dynamics not calculated
            elif not os.path.isfile(_dir + _file_ds[i] + '.npy'):
                # update log
                logger.debug('File {file_name} does not exist inside directory {dir_name}\n'.format(file_name=_file_ds[i], dir_name=_dir))

                todo = True

            if todo:
                # update lists
                _v_todo += _v[_n_v * i : _n_v * i + _n_v]
                for key in _c_todo:
                    _c_todo[key].append(_c[key][i])
                # update count
                _count += 1

        _v = _v_todo

        _c['n_s'] = _count
        for key in _c_todo:
            if type(_c[key]) == list:
                _c[key] = _c_todo[key]

    # initialize axis
    _T_d = T.val 

    # all variables
    V_all = list()
    # all measures
    D_all = list()

    # display initialization
    logger.info('Calculating dynamics for {system_name}...\n\tMeasure Parameters:\n\t\t{meas_params}\n\tDynamics Parameters:\n\t\t{dyna_params}\n'.format(system_name=system.name, meas_params=meas_params, dyna_params=dyna_params))
    
    if _c['n_s'] != 0:
        # solver function
        solver_type = dyna_params['solver_type']
        func = getattr(system, 'f_multi_' + solver_type)

        # calculate dynamics
        _, V = solvers.solve_ode_scipy(func, solver_type, T.val, _v, _c)

        # display completion
        logger.info('----------------System Dynamics Obtained----------------\n')
            
        # convert to numpy array
        V = np.array(V)
        
        # for each system
        for i in range(_c['n_s']):
            # extract dynamics of individual system
            # update lists
            _V_s = V[:, _n_v * i : _n_v * i + _n_v]
            _D_s = np.zeros([T.dim])
            # calculate measures for individual system
            if meas_params['type'] == 'corr':
                _D_s = correlations.calculate(_V_s, meas_params)
            elif meas_params['type'] == 'diff':
                _D_s = differences.calculate(_V_s, meas_params)

            # if caching is enabled
            if _cache:
                _file_v = _file_v_prefix
                _file_d = _file_d_prefix
                for val in _c['params'][i]:
                    _file_v += '_' + str(val)
                    _file_d += '_' + str(val)

                # save system dynamics data to file
                np.save(_dir + _file_v, np.array(_V_s))
                # save measure dynamics data to file
                np.save(_dir + _file_d, np.array(_D_s))

            else:
                # update lists
                V_all.append(_V_s)
                D_all.append(_D_s.val)  

                # display plot
                if plot:
                    logger.info('Plotting the dynamics from {filename}...\n'.format(filename=_file_d))
                    figure = Figure(plot_params, X=T)
                    figure.update(_T_d, _D_s)
            
        # display completion
        logger.info('----------------Measure Dynamics Obtained---------------\n') 

    # display completion
    logger.debug('----------------Dynamics Obtained---------------\n')
    
    if _cache:
        for i in range(_n_s):
            _V_s = np.load(_dir + _file_vs[i] + '.npy').tolist()
            _D_s = np.load(_dir + _file_ds[i] + '.npy').tolist()
            V_all.append(_V_s)
            D_all.append(_D_s)

            # display plot
            if plot:
                if X != None:
                    plot_params['legend'] = X.legends[i]
                logger.info('Plotting the dynamics from {filename}...\n'.format(filename=_file_ds[i]))
                figure = Figure(plot_params, X=T)
                figure.update(_T_d, _D_s)

    # axes dictionary
    Axes = {}
    Axes['T'] = _T_d
    if X != None:
        Axes['X'] = X.val

    return D_all, V_all, Axes    