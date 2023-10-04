#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module containing utility functions for solvers."""

__name__ = 'qom.utils.solvers'
__authors__ = ["Sampreet Kalita"]
__created__ = "2023-06-21"
__updated__ = "2023-09-14"

# dependencies
import concurrent.futures as cf
import logging
import multiprocessing as mp
import numpy as np
import os
import time

# qom modules
from ..solvers.deterministic import HLESolver, SSHLESolver
from ..solvers.measure import QCMSolver, get_Lyapunov_exponents, get_stability_zone, get_system_measures
from ..solvers.stability import RHCSolver, get_counts_from_eigenvalues
from ..solvers.stochastic import MCQTSolver
from ..ui import init_log
from ..ui.plotters import MPLPlotter

# module_logger
logger = logging.getLogger(__name__)

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
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
        
    Returns
    -------
    get_le : callable
        Function to obtain the Lyapunov exponents. Returns a ``numpy.ndarray`` with shape ``(2 * num_modes, )``.
    """

    # function to obtain the Lyapunov exponents
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
    """Function to get the function to obtain the quantum correlation measures.

    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Uninitialized system class. Requires predefined system methods for certain solver methods.
    params : dict, optional
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver`, :class:`qom.solvers.deterministic.SSHLESolver` and :class:`qom.solvers.measure.QCMSolver` for available parameters.
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
        
    Returns
    -------
    get_qcm : callable
        Function to obtain the quantum correlation measures. Returns a ``numpy.ndarray`` with shape ``(dim, num_measure_codes)``.
    """

    # function to obtain the quantum correlation measures
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
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver`, :class:`qom.solvers.deterministic.SSHLESolver` and :class:`qom.solvers.stability.RHCSolver` for available parameters. If the value of key ``"system_measure_name"`` is ``"coeffs_A"``, the stability is calculated using the coefficients, else the drift matrices are used (fallback).
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    use_rhc : bool, default=False
        Option to use the Routh-Hurwitz criteria to calculate the counts for the unstable eigenvalues.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
        
    Returns
    -------
    get_sz : callable
        Function to obtain the stability zone. Returns a ``numpy.ndarray`` with shape ``(dim, )``. If ``steady_state`` is set to ``True``, the array contains a single element denoting the multi-stability indicator. Refer to ``qom.solvers.measure.get_stability_zone`` function for the meaning of indicators.
    """

    # function to obtain the stability zone
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
            return np.array([get_stability_zone(
                counts=counts
            )], dtype=np.int_)
        else:
            return np.array([get_stability_zone(
                counts=[count]
            ) for count in counts], dtype=np.int_)

    return get_sz

def get_func_system_measures(SystemClass, params:dict={}, steady_state:bool=True, cb_update=None):
    """Function to get the function to obtain the system measures.

    Parameters
    ----------
    SystemClass : :class:`qom.systems.*`
        Uninitialized system class. Requires predefined system methods for certain solver methods.
    params : dict, optional
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.HLESolver` and :class:`qom.solvers.deterministic.SSHLESolver` and `qom.solvers.measure.get_system_measures` for available parameters.
    steady_state : bool, default=True.
        Whether the calculated modes and correlations are steady state values or time series.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
        
    Returns
    -------
    get_sm : callable
        Function to obtain the system measures. Returns a ``numpy.ndarray`` with shape ``(dim, )`` plus the shape of each measure.
    """

    # function to obtain the system measures
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

def run_mcqt_solvers_in_parallel(system, params:dict, num_trajs:int=1000, plot:bool=False, subplots:bool=False, params_plotter:dict={}, max_processes:int=None, cb_update=None):
    r"""Function to run multiple MCQTSolver in parallel processes.
    
    Parameters
    ----------
    system : :class:`qom.systems.base`
        Instance of the system. Requires predefined system methods ``get_ops_collapse``, ``get_ops_expect``, ``get_H_0`` and ``get_ivc``. For time-dependent Hamiltonians, the method ``get_H_t`` should also be defined. Refer to **Notes** of :class:`qom.solvers.stochastic.MCQTSolver` for their implementations.
    params : dict
        Parameters of the solver. Refer to **Notes** of :class:`qom.solvers.stochastic.MCQTSolver` for all available options.
    num_trajs : int, default=1000
        Number of trajectories.
    plot : bool, default=False
        Option to plot the results of the main process.
    subplots : bool, default=False
        Option to plot the results of each subprocesses.
    params_plotter : dict, optional
        Parameters of the plotter.
    max_processes : int, optional
        Maximum number of solvers to run in parallel. The number of slices is decided by the dimensionality of the Hilbert space and the number of trajectories. For smaller number of trajectories, a single process is run without parallelization. Default value of dimension is :math:`5 \times 10^{4} / N`, where :math:`N` is the dimension of the combined Hilbert space.
    cb_update : callable
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Returns
    -------
    solver : :class:`qom.solvers.stochastic.MCQTSolver`
        Instance of the solver.
    """

    # validate system
    assert getattr(system, 'get_ivc', None) is not None, "Missing required system method ``get_ivc``"

    # frequently used variables
    p_start = time.time()
    _s = "Time Elapsed\t"

    # maximum dimension for slicing
    max_dim = int(1e5 / system.get_ivc()[0].shape[0])
    # single solver for smaller dimensions
    if num_trajs * 5 <= max_dim:
        return wrap_mcqt_solver(
            system=system,
            params=params,
            num_trajs=num_trajs,
            plot=plot,
            params_plotter=params_plotter,
            cb_update=cb_update,
            parallel=True
        )
    # handle null value or overflow
    if max_processes is None or max_processes > num_trajs or max_processes < 1:
        max_processes = int(np.min([os.cpu_count() - 2, num_trajs])) if num_trajs > 1 else 1
    # process-based slices for smaller dimensions
    if num_trajs / max_processes * 5 <= max_dim:
        Num_trajs = (max_processes - 1) * [int(num_trajs / max_processes)]
        if num_trajs % max_processes != 0:
            Num_trajs += [num_trajs % max_processes]
    # fixed slices for higher dimensions
    else:
        slice_dim = int(max_dim / max_processes)
        Num_trajs = int(num_trajs / slice_dim) * [slice_dim]
        if num_trajs % slice_dim != 0:
            Num_trajs += [num_trajs % slice_dim]

    # initialize logger
    init_log(parallel=True)

    # initialize solver
    solver = MCQTSolver(
        system=system,
        params=params,
        num_trajs=num_trajs,
        cb_update=cb_update,
        parallel=True
    )

    # populate arguments
    Args = list()
    for i in range(len(Num_trajs)):
        # update log string
        _s += "Process #" + str(i) + "\t"
        Args.append([system, params, Num_trajs[i], subplots, params_plotter, True, i, p_start])

    # update log
    if params['show_progress']:
        logger.info("\n" + _s + "\n")

    # multiprocess and join
    with cf.ProcessPoolExecutor(max_workers=max_processes, mp_context=mp.get_context('spawn')) as executor:
        _solvers = list(executor.map(run_mcqt_solver_instance, Args))

    # join results of solvers
    _trajs = np.concatenate([_solver.results['trajs'] for _solver in _solvers], axis=2)
    solver.results = {
        'times': solver.T,
        'trajs': _trajs,
        'expects': np.sum(_trajs, axis=2) / num_trajs,
        'runtime': time.time() - solver.p_start
    }
        
    # update log
    if params['show_progress']:
        logger.info("\rTime taken: {:0.3f} s".format(time.time() - p_start))

    # plot results
    if plot:
        plot_mcqt_solver_results(
            solver=solver,
            params_plotter=params_plotter
        )

    return solver

def run_mcqt_solver_instance(args):
    """Function to run a single instance of ``wrap_mcqt_solver``.
    
    Parameters
    ----------
    args : list
        Arguments of the ``wrap_mcqt_solver`` function.

    Returns
    -------
    solver : :class:`qom.solvers.stochastic.MCQTSolver`
        Instance of the solver.
    """

    # return solver
    return wrap_mcqt_solver(
        system=args[0],
        params=args[1],
        num_trajs=args[2],
        plot=args[3],
        params_plotter=args[4],
        cb_update=None,
        parallel=args[5],
        p_index=args[6],
        p_start=args[7]
    )

def wrap_mcqt_solver(system, params:dict, num_trajs:int=1000, plot:bool=False, params_plotter:dict={}, cb_update=None, parallel=False, p_index:int=0, p_start:float=None):
    """Function to wrap MCQTSolver.
    
    Parameters
    ----------
    system : :class:`qom.systems.base`
        Instance of the system. Requires predefined system methods ``get_ops_collapse``, ``get_ops_expect``, ``get_H_0`` and ``get_ivc``. For time-dependent Hamiltonians, the method ``get_H_t`` should also be defined. Refer to **Notes** of :class:`qom.solvers.stochastic.MCQTSolver` for their implementations.
    params : dict
        Parameters of the solver. Refer to **Notes** of :class:`qom.solvers.stochastic.MCQTSolver` for all available options.
    num_trajs : int, default=1000
        Number of trajectories.
    plot : bool, default=False
        Option to plot the results of the main process.
    params_plotter : dict, optional
        Parameters of the plotter.
    cb_update : callable
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.

    Returns
    -------
    solver : :class:`qom.solvers.stochastic.MCQTSolver`
        Instance of the solver.
    """

    # initialize logger
    init_log(parallel=parallel)

    # initialize solver
    solver = MCQTSolver(
        system=system,
        params=params,
        num_trajs=num_trajs,
        cb_update=cb_update,
        parallel=parallel,
        p_index=p_index,
        p_start=p_start
    )

    # solve for results
    solver.solve()

    # plot results
    if plot:
        plot_mcqt_solver_results(
            solver=solver,
            params_plotter=params_plotter
        )

    return solver

def plot_mcqt_solver_results(solver, params_plotter:dict):
    """Helper function to plot results.
    
    Parameters
    ----------
    solver : :class:`qom.solvers.stochastic.MCQTSolver`
        Instance of the solver.
    params_plotter : dict
        Parameters of the plotter. Refer to **Notes** of :class:`qom.ui.plotters.base.BasePlotter` for all available parameters.
    """

    # initialize plot
    plotter = MPLPlotter(
        axes={
            'X': solver.results['times']
        },
        params=params_plotter
    )
    
    # update plotter
    plotter.update(
        vs=solver.results['expects'].T,
        xs=solver.results['times'],
    )
    plotter.show(
        hold=True
    )