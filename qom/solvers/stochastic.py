#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to solve stochastic equations of motion."""

__name__ = 'qom.solvers.stochastic'
__authors__ = ["Sampreet Kalita"]
__created__ = "2023-08-13"
__updated__ = "2023-09-14"

# dependencies
from copy import deepcopy
import numpy as np
import time

# qom modules
from .base import get_all_times, validate_system
from .differential import ODESolver
from ..io import Updater

# TODO: Implement saving/loading

class MCQTSolver():
    r"""Class to solve for the expectation values of operators using the Monte-Carlo quantum trajectories method.

    Initializes ``system``, ``num_trajs``, ``T`` and ``updater``.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system methods ``get_ops_collapse``, ``get_ops_expect``, ``get_H_0`` and ``get_ivc``. For time-dependent Hamiltonians, the method ``get_H_t`` should also be defined. Refer to **Notes** below for their implementations.
    params : dict
        Parameters for the solver. Refer to **Notes** below for all available options. Required options are:
            ========    ====================================================
            key         value
            ========    ====================================================
            't_min'     (*float*) minimum time at which integration starts.
            't_max'     (*float*) maximum time at which integration stops.
            't_dim'     (*int*) number of values from ``'t_max'`` to ``'t_min'``, both inclusive.
            ========    ====================================================
    num_trajs : int
        Number of trajectories.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.

    Notes
    -----
        The following system methods follow a strict formatting:
            ================    ================================================
            method              returns
            ================    ================================================
            get_H_0             the time-independent part of the Hamiltonian, formatted as ``get_H_0(c)``, where ``c`` is an array of the derived constants and controls of the system.
            get_H_t             the time-dependent part of the Hamiltonian, formatted as ``get_H_t(c, t)``, where ``c`` is an array of the derived constants and controls of the system and ``t`` is the time at which the Hamiltonian is obtained.
            get_ops_collapse    the collapse operators of the system. It follows the same formatting as ``get_H_0``.
            get_ops_expect      the operators of the system for which the expectation values are to be obtained. It follows the same formatting as ``get_H_0``.
            get_ivc             the initial state vector and the derived constants and controls, formatted as ``get_ivc()``.
            ================    ================================================
        
        The ``params`` dictionary currently supports the following keys:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
            'ode_method'        (*str*) method used to solve the ODEs. Available options are ``'BDF'``, ``'DOP853'``, ``'LSODA'``, ``'Radau'``, ``'RK23'``, ``'RK45'`` (fallback), ``'dop853'``, ``'dopri5'``, ``'lsoda'``, ``'vode'`` and ``'zvode'``. Refer to :class:`qom.solvers.differential.ODESolver` for details of each method. Default is ``'RK45'``.
            'ode_is_stiff'      (*bool*) option to select whether the integration is a stiff problem or a non-stiff one. Default is ``False``.
            'ode_atol'          (*float*) absolute tolerance of the integrator. Default is ``1e-12``.
            'ode_rtol'          (*float*) relative tolerance of the integrator. Default is ``1e-6``.
            't_min'             (*float*) minimum time at which integration starts. Default is ``0.0``.
            't_max'             (*float*) maximum time at which integration stops. Default is ``1000.0``.
            't_dim'             (*int*) number of values from ``'t_max'`` to ``'t_min'``, both inclusive. Default is ``10001``.
            ================    ====================================================
    """

    # attributes
    name = 'MCQTSolver'
    """str : Name of the solver."""
    desc = "Monte-Carlo Quantum Trajectories Solver"
    """str : Description of the solver."""
    solver_defaults = {
        'show_progress': False,
        'ode_method': 'zvode',
        'ode_is_stiff': False,
        'ode_atol': 1e-8,
        'ode_rtol': 1e-6,
        't_min': 0.0,
        't_max': 1000.0,
        't_dim': 10001
    }
    """dict : Default parameters of the solver."""

    def __init__(self, system, params:dict, num_trajs:int, cb_update=None, parallel:bool=False, p_index:int=0, p_start:float=None):
        """Class constructor for MCQTSolver."""

        # set constants
        self.system = system
        self.num_trajs = num_trajs
        self.parallel = parallel
        self.p_index = p_index
        self.p_start = p_start if p_start is not None else time.time()

        # set attribute
        self.is_H_constant = True
        if getattr(self.system, 'get_H_t', None) is not None:
            self.is_H_constant = False

        # set parameters
        self.set_params(params)

        # set times
        self.T = get_all_times(self.params)

        # set updater
        self.updater = Updater(
            name='qom.solvers.MCQTSolver',
            cb_update=cb_update,
            parallel=parallel,
            p_index=p_index,
            p_start=self.p_start
        )

    def set_params(self, params):
        """Method to set the solver parameters.
        
        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

    def solve(self):
        """Method to solve for the quantum trajectories.

        Sets the results with keys ``'times'``, ``'trajs'``, ``'expects'`` and ``'runtimes'`` for the time steps, individual trajectories of expectation values, pooled expectation values and execution times of each trajectory respectively.
        """

        # validate system
        validate_system(
            system=self.system,
            required_system_attributes=['get_ops_collapse', 'get_ops_expect', 'get_H_0', 'get_ivc']
        )

        # initial state vector, derived constants and controls
        iv_psi, c = self.system.get_ivc()
        # collapse operators
        ops_c = self.system.get_ops_collapse(
            c=c
        )
        # evaluation operators
        ops_e = self.system.get_ops_expect(
            c=c
        )
        # initialize time-independent Hamiltonian with collapse operators
        H_0_eff = self.system.get_H_0(
            c=c
        ) - 0.5j * sum([op.T.conj() * op for op in ops_c])

        # extract frequently used variables
        t_dim = len(self.T)
        t_ssz = self.T[1] - self.T[0]
        size_0 = iv_psi.shape[0]
        size_c = len(ops_c)
        size_e = len(ops_e)

        # pseudo-random number generator
        epsilons= np.random.random_sample(size=(t_dim, 2, self.num_trajs))

        # initialize variables
        psis = np.repeat(iv_psi, repeats=self.num_trajs, axis=1)
        trajs = np.zeros((t_dim, size_e, self.num_trajs), dtype=np.float_)
        Phis_jump = np.zeros((size_c, size_0, self.num_trajs), dtype=np.complex_)
        phi_norms = np.zeros((size_c, self.num_trajs), dtype=np.float_)

        # ODE function
        def func_ode(t, v, c):
            # get effective Hamiltonian
            H_eff = H_0_eff if self.is_H_constant else (H_0_eff + self.system.get_H_t(
                c=c,
                t=t
            ))

            return -1.0j * np.dot(H_eff, np.reshape(v, (size_0, int(v.shape[0] / size_0)))).ravel()
        
        # initialize ODE solver
        ode_params = deepcopy(self.params)
        ode_params['show_progress'] = False
        ode_solver = ODESolver(
            func=func_ode,
            params=ode_params,
            cb_update=self.updater.cb_update
        )
        
        # for each time step
        for i in range(t_dim):
            # update expectation values
            for j in range(len(ops_e)):
                trajs[i, j] = np.real(np.sum(psis.conj() * np.dot(ops_e[j], psis), axis=0))

            # calculate collapse probabilities and new psis
            for j in range(size_c):
                Phis_jump[j] = ops_c[j].dot(psis)
                phi_norms[j] = np.real(np.linalg.norm(Phis_jump[j], axis=0))**2

            # sum of norms
            norm_sums = np.sum(phi_norms, axis=0)
            # check whether to continue time evolution
            continues = epsilons[i, 0] > t_ssz * norm_sums
            continues_k = np.squeeze(np.argwhere(continues), axis=1)
            # renormalize norms
            nnz_sums_k = norm_sums > 0
            phi_norms[:, nnz_sums_k] /= norm_sums[nnz_sums_k]
            # cumulative sums
            p_cumsums = np.cumsum(phi_norms, axis=0)
            # check first true value of breaking condition and reduce one index
            phi_indices = np.argmax(np.int_((epsilons[i][1] <= p_cumsums)), axis=0) - 1
            # set negatives to 0 as they always fulfil breaking condition
            phi_indices[phi_indices < 0] = 0
            
            # continue trajectory
            if len(continues_k):
                # frequently used variables
                size_1 = len(continues_k)

                psis[:, continues_k] = np.reshape(ode_solver.solve(
                    T=[self.T[i], self.T[i] + t_ssz],
                    iv=psis[:, continues_k].ravel(),
                    c=c
                )[-1], (size_0, size_1))

            # collapse
            jumps_k = np.argwhere(np.logical_not(continues)).ravel()
            for k in jumps_k:
                psis[:, k] = Phis_jump[phi_indices[k], :, k]
            # normalize
            psis = psis / np.real(np.linalg.norm(psis, axis=0))
            
            if self.params['show_progress']:
                self.updater.update_progress(
                    pos=i,
                    dim=t_dim,
                    status="-" * (19 - len(self.name)) + "Obtaining the trajectories",
                    reset=False
                )

        # clear memory
        del iv_psi, c, ops_c, ops_e, H_0_eff, t_dim, t_ssz, size_0, size_c, size_e
        del epsilons, psis, Phis_jump, phi_norms

        # set results
        self.results = {
            'times': self.T,
            'trajs': trajs,
            'expects': np.sum(trajs, axis=2) / self.num_trajs,
            'runtime': time.time() - self.p_start
        }