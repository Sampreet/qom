#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module containing utility functions for solvers."""

__name__ = 'qom.utils.solvers'
__authors__ = ["Sampreet Kalita"]
__created__ = "2023-06-21"
__updated__ = "2023-07-10"

# qom modules
from ..solvers.deterministic import HLESolver, SSHLESolver
from ..solvers.measure import QCMSolver, get_Lyapunov_exponents, get_stability_zone, get_system_measures
from ..solvers.stability import RHCSolver, get_counts_from_eigenvalues

def get_func_Lyapunov_exponents(SystemClass, params:dict={}, steady_state:bool=True, cb_update=None):
    """Function to get the function to obtain the Lyapunov exponents.

    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Uninitialized system class. Requires predefined system methods for certain solver methods.
    params : dict, optional
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver`, :class:`qom.solvers.deterministic.SSHLESolver` and `qom.solvers.measure.get_Lyapunov_exponents` for available parameters.
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.
        
    Returns
    -------
    get_le : callable
        Function to obtain the Lyapunov exponents.
    """

    # function
    def get_le(system_params):
        # initialize system
        system = SystemClass(
            params=system_params,
            cb_update=cb_update
        )

        # initialize solver
        SolverClass = SSHLESolver if steady_state else HLESolver
        solver = SolverClass(
            system=system,
            params=params,
            cb_update=cb_update
        )
        # get final times and modes
        T = [0.0] if steady_state else solver.get_times()
        Modes = solver.get_modes()

        # return Lyapunov exponents
        return get_Lyapunov_exponents(
            system=system,
            modes=Modes[-1],
            t=T[-1],
            params=params,
            cb_update=cb_update
        )

    return get_le

def get_func_quantum_correlation_measures(SystemClass, params:dict={}, steady_state:bool=True, cb_update=None):
    """Function to get the function to obtain quantum correlation measures.

    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Uninitialized system class. Requires predefined system methods for certain solver methods.
    params : dict, optional
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver`, :class:`qom.solvers.deterministic.SSHLESolver` and :class:`qom.solvers.measure.QCMSolver` for available parameters.
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.
        
    Returns
    -------
    get_qcm : callable
        Function to obtain quantum correlation measures.
    """

    # function
    def get_qcm(system_params):
        # initialize system
        system = SystemClass(
            params=system_params,
            cb_update=cb_update
        )

        # initialize solver
        SolverClass = SSHLESolver if steady_state else HLESolver
        solver = SolverClass(
            system=system,
            params=params,
            cb_update=cb_update
        )

        # get modes, correlations and times
        Modes, Corrs = solver.get_modes_corrs()

        # get quantum correlation measures
        return QCMSolver(
            Modes=Modes,
            Corrs=Corrs,
            params=params,
            cb_update=cb_update
        ).get_measures()
    
    return get_qcm

def get_func_stability_zone(SystemClass, params:dict={}, steady_state:bool=True, use_rhc:bool=False, cb_update=None):
    """Function to get the function to obtain the stability zone.

    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Uninitialized system class. Requires predefined system methods for certain solver methods.
    params : dict, optional
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver`, :class:`qom.solvers.deterministic.SSHLESolver` and :class:`qom.solvers.stability.RHCSolver` for available parameters. If the value of key `"system_measure_name"` is `"coeffs_A"`, the stability is calculated using the coefficients, else the drift matrices are used (fallback).
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    use_rhc : bool, default=False
        Option to use the Routh-Hurwitz criteria to calculate the counts for the unstable eigenvalues.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.
        
    Returns
    -------
    get_sz : callable
        Function to obtain the stability zone.
    """

    # function
    def get_sz(system_params):
        # initialize system
        system = SystemClass(
            params=system_params,
            cb_update=cb_update
        )

        # initialize solver
        SolverClass = SSHLESolver if steady_state else HLESolver
        solver = SolverClass(
            system=system,
            params=params,
            cb_update=cb_update
        )

        # get coefficients
        if 'coeffs_A' in params.get('system_measure_name', 'A'):
            As = None
            Coeffs = get_system_measures(
                system=system,
                Modes=solver.get_modes(),
                T=solver.get_times() if not steady_state else None,
                params=params,
                cb_update=cb_update
            )
        # get drift matrices
        else:
            As = solver.get_As() if steady_state else get_system_measures(
                system=system,
                Modes=solver.get_modes(),
                T=solver.get_times() if not steady_state else None,
                params=params,
                cb_update=cb_update
            )
            Coeffs = None

        # get stability zone using Routh-Hurwitz criteria
        if use_rhc:
            counts = RHCSolver(
                As=As,
                Coeffs=Coeffs,
                params=params,
                cb_update=cb_update
            ).get_counts()
        # get stability zone using eigenvalues
        else:
            counts=get_counts_from_eigenvalues(
                As=As,
                Coeffs=Coeffs,
                params=params,
                cb_update=cb_update
            )

        if steady_state:
            return [get_stability_zone(
                counts=counts
            )]
        else:
            return [get_stability_zone(
                counts=[count]
            ) for count in counts]

    return get_sz

def get_func_system_measures(SystemClass, params:dict={}, steady_state:bool=True, cb_update=None):
    """Function to get the function to obtain system measure.

    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Uninitialized system class. Requires predefined system methods for certain solver methods.
    params : dict, optional
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver` and :class:`qom.solvers.deterministic.SSHLESolver` and `qom.solvers.measure.get_system_measures` for available parameters.
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.
        
    Returns
    -------
    get_sm : callable
        Function to obtain system measure.
    """

    # function
    def get_sm(system_params):
        # initialize system
        system = SystemClass(
            params=system_params,
            cb_update=cb_update
        )

        # initialize solver
        SolverClass = SSHLESolver if steady_state else HLESolver
        solver = SolverClass(
            system=system,
            params=params,
            cb_update=cb_update
        )

        # get system measures
        return get_system_measures(
            system=system,
            Modes=solver.get_modes(),
            T=solver.get_times() if not steady_state else None,
            params=params,
            cb_update=cb_update
        )
    
    return get_sm