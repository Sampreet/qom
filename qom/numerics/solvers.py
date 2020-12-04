#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module containing sovler functions."""

__name__    = 'qom.numerics.solvers'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-09-27'
__updated__ = '2020-12-04'

# dependencies
import logging
import scipy.integrate as si

# modules logger
logger = logging.getLogger(__name__)

def solve_ode_scipy(func, solver_type, ts, iv, c):
    """Function to calculate the dynamics of variables for a given system using :class:`scipy.integrate.ode`.

    Parameters
    ----------
    func : callable
        Function for the system.
    solver_type : dict
        Parameters for the calculation of dynamics.
    ts : list
        Times at which dynamics are required.
    iv : list
        Initial values of variables.
    c : list
        Constants for the system.

    Returns
    -------
    ts : list
        Times at which dynamics are calculated.
    vs : list
        Dynamics of the variables.
    """

    # initialize integrator
    integrator = si.ode(func)
    # for complex ode solver
    if solver_type.find('complex') != -1:
        integrator.set_integrator('zvode')
        
    # set initial values and constants
    integrator.set_initial_value(iv, ts[0])
    integrator.set_f_params(c)

    # initialize lists
    vs = [iv]

    # for each time step, calculate the integration values
    for i in range(1, len(ts)):
        # update progress
        progress = float(i - 1)/float(len(ts) - 1) * 100
        # display progress
        if int(progress * 1000) % 10 == 0:
            logger.info('Obtaining the system dynamics: Progress = {progress:3.2f}'.format(progress=progress))

        # integrate
        t = ts[i]
        v = integrator.integrate(t)

        # update log
        logger.debug('t = {}\tv = {}'.format(t, v))

        # update lists
        vs.append(v)

    return ts, vs