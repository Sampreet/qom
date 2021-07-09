#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface QOM systems."""

__name__    = 'qom.systems.BaseSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2021-07-06'

# dependencies
from typing import Union
import copy
import logging
import numpy as np
from numpy.matrixlib.defmatrix import _convert_from_string
import scipy.constants as sc
import scipy.linalg as sl
import scipy.optimize as so

# qom modules
from ..solvers import HLESolver
from ..solvers import QCMSolver
from ..solvers import RHCSolver
from ..ui.plotters import MPLPlotter

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]
t_float = Union[float, np.float, np.float_]

# TODO: Handle other measures in `get_measure_dynamics`.
# TODO: Amplitude-based parameters in `get_mean_*`.
# TODO: Add `check_limit_cycle`.

class BaseSystem():
    """Class to interface QOM systems.

    Initializes `params` property.

    References:

    [1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86** (4), 1931 (2014).

    [2] F. Galve, G. L. Giorgi, R. Zambrini, *Quantum Correlations and Synchronization Measures*, Lectures on General Quantum Correlations and their Applications, Quantum Science and Technology, Springer (2017).

    Parameters
    ----------
    params : dict
        Parameters for the system.
    """

    # attributes
    types_measures = ['corr_ele', 'mode_amp', 'qcm']
    types_qcm = [func[4:] for func in dir(QCMSolver) if callable(getattr(QCMSolver, func)) and func[:4] == 'get_']
    types_plots = MPLPlotter.types_1D + MPLPlotter.types_2D + MPLPlotter.types_3D

    @property
    def code(self):
        """str: Codename of the system."""

        return self.__code

    @code.setter
    def code(self, code: str):
        self.__code = code

    @property
    def name(self):
        """str: Name of the system."""

        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def num_modes(self):
        """int: Number of modes."""

        return self.__num_modes

    @num_modes.setter
    def num_modes(self, num_modes: int):
        self.__num_modes = num_modes

    @property
    def params(self):
        """dict: Parameters for the system."""

        return self.__params

    @params.setter
    def params(self, params: dict):
        self.__params = params

    def __init__(self, params: dict):
        """Class constructor for BaseSystem."""

        # set properties
        self.params = params

    def __validate_params_corr_ele(self, solver_params: dict, count: int=None):
        """Method to validate parameters for elements of correlation matrix.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        count : int
            Number of elements.
        """
        
        # row and column indices
        for key in ['idx_row', 'idx_col']:
            assert key in solver_params, 'Solver parameters should contain the keys "idx_row" and "idx_col" for row and column indices'
            assert type(solver_params[key]) is list or type(solver_params[key]) is int, 'Keys "idx_row" and "idx_col" should be integers or lists of integers'
        
        # extract frequently used variables
        _idx_row = solver_params['idx_row']
        _idx_col = solver_params['idx_col']

        # same type
        assert type(_idx_row) is type(_idx_col), 'Keys "idx_row" and "idx_col" should be of same type'
        
        # same shape
        assert len(_idx_row) == len(_idx_col) if type(_idx_row) is list else True, 'Keys "idx_row" and "idx_col" should be of same shape'

        # for fixed number of elements
        if count is not None:
            assert len(_idx_row) == count, 'Keys "idx_row" and "idx_col" should contain exactly {} entries'.format(count)
    
    def __validate_params_eigs_max(self, solver_params: dict):
        """Method to validate parameters for maximum eigenvalue of the drift matrix.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        """

        # validate parameters
        assert 'idx_eig' in solver_params, 'Solver parameters should contain the key "idx_eig" for the eigenvalue indices'

        # extract frequently used variables
        _idx_eig = solver_params['idx_eig']

        # validate limits
        if type(_idx_eig) is int:
            _idx_eig = [_idx_eig]
        for idx in _idx_eig:
            assert idx < 2 * self.num_modes, 'Eigenvalue indices should not exceed total number of quadratures'
    
    def __validate_params_measure(self, solver_params: dict):
        """Method to validate parameters for measures.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        """

        # measure type
        assert 'measure_type' in solver_params, 'Solver parameters should contain key "measure_type" for the type of measure'

        # extract frequently used variables
        _measure_type = solver_params['measure_type']

        # supported types
        assert _measure_type in self.types_measures, 'Supported types of measures are {}'.format(str(self.types_measures))

        # correlation matrix elements
        if _measure_type == 'corr_ele':
            self.__validate_params_corr_ele(solver_params)
        # mode amplitudes
        if _measure_type == 'mode_amp':
            self.__validate_params_mode_amp(solver_params)
        # quantum correlation measure
        if _measure_type == 'qcm':
            self.__validate_params_qcm(solver_params)

    def __validate_params_mode_amp(self, solver_params: dict):
        """Method to validate parameters for amplitudes of modes.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        """
        
        # mode indices
        assert 'idx_mode' in solver_params, 'Solver parameters should contain the key "idx_mode" for indices of the modes'

        # extract frequently used variables
        _idx_mode = solver_params['idx_mode']

        # index type
        assert type(_idx_mode) is list or type(_idx_mode) is int, 'Key "idx_mode" should be integer or list of integers'
        
        # index limits
        if type(_idx_mode) is int:
            _idx_mode = [_idx_mode]
        for idx in _idx_mode:
            assert idx < self.num_modes, 'Mode indices should not exceed total number of modes'

    def __validate_params_qcm(self, solver_params: dict):
        """Method to validate parameters for quantum correlations measures.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        """
        
        # quantum correlation measure type
        assert 'qcm_type' in solver_params, 'Solver parameters should contain key "qcm_type" for the type of correlation measure'

        # supported types
        assert solver_params['qcm_type'] in self.types_qcm, 'Supported quantum correlation measures are {}'.format(str(self.types_qcm))
        
        # mode indices
        for key in ['idx_mode_i', 'idx_mode_j']:
            assert key in solver_params, 'Solver parameters should contain the keys "idx_mode_i" and "idx_mode_j" for the mode indices'
            assert type(solver_params[key]) is list or type(solver_params[key]) is int, 'Keys "idx_mode_i" and "idx_mode_j" should be integers or lists of integers'

        # extract frequently used variables
        _idx_mode_i = solver_params['idx_mode_i']
        _idx_mode_j = solver_params['idx_mode_j']

        # same type
        assert type(_idx_mode_i) is type(_idx_mode_j), 'Keys "idx_mode_i" and "idx_mode_j" should be of same type'
        
        # same shape
        assert len(_idx_mode_i) == len(_idx_mode_j) if type(_idx_mode_i) is list else True, 'Keys "idx_mode_i" and "idx_mode_j" should be of same shape'
        
        # index limits
        if type(_idx_mode_i) is int:
            _idx_mode_i = [_idx_mode_i]
        for idx in _idx_mode_i:
            assert idx < self.num_modes, 'Mode indices should not exceed total number of modes'
        if type(_idx_mode_j) is int:
            _idx_mode_j = [_idx_mode_j]
        for idx in _idx_mode_j:
            assert idx < self.num_modes, 'Mode indices should not exceed total number of modes'

    def get_corr_ele(self, solver_params: dict, corrs: list):
        """Method to obtain a particular element or list of elements of the correlation matrix.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        corrs : list
            Matrix of quantum correlations.

        Returns
        -------
        ele : list
            Selected elements.
        """

        # extract frequently used variables
        _idx_row = solver_params['idx_row']
        _idx_col = solver_params['idx_col']
        
        # single element
        if type(_idx_row) is int:
            _idx_row = [_idx_row]
        if type(_idx_col) is int:
            _idx_col = [_idx_col]
        
        # extract elements
        ele = [corrs[_idx_row[j]][_idx_col[j]] for j in range(len(_idx_row))]

        return ele

    def get_eig_max(self, solver_params: dict, ode_func, get_ivc, get_A, ode_func_corrs=None):
        """Function to obtain the maximum eigenvalue of the drift matrix.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        get_ivc : function
            Function returning the initial values and constants.
        get_A : function
            Function to obtain the drift matrix given the list of modes as parameter.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations.
        
        Returns
        -------
        eig_max : list
            Maximum eigenvalue of the drift matrix.
        """

        # validate parameters
        self. __validate_params_eigs_max(solver_params)

        # update a deep copy of parameters
        _solver_params = copy.deepcopy(solver_params)
        _solver_params['measure_type'] = 'mode_amp'
        _solver_params['idx_mode'] = [i for i in range(self.num_modes)]

        # get averaged modes
        modes = self.get_measure_average(_solver_params, ode_func, get_ivc, ode_func_corrs)

        # extract parameters
        _, c = get_ivc()
        params = c[4 * self.num_modes**2:]

        # drift matrix
        A = get_A(modes, params, np.inf)

        # extract frequently used variables
        _idx_eig = solver_params['idx_eig']
        
        # single mode
        if type(_idx_eig) is int:
            _idx_eig = [_idx_eig]

        # initialize lists
        eigs = list()
        
        # update eigenvalues
        eigenvalues, _ = np.linalg.eig(A)
        for idx in _idx_eig:
            eigs.append(eigenvalues[idx])

        # calculate maximum eigenvalue
        eig_max = np.max(eigs)

        return eig_max

    def get_mean_optical_amplitude(self, lambda_l: t_float, mu: t_float, gamma_o: t_float, P_l: t_float, Delta: t_float, C: t_float=0, mode='basic'):
        r"""Method to obtain the mean optical amplitude.

        The optical steady state is assumed to be of the form [1],

        .. math::
            \alpha_{s} = \frac{\eta_{l}}{\frac{\gamma_{o}}{2} - \iota \Delta}

        where :math:`\Delta = \Delta_{l} + C |\alpha_{s}|^{2}`, :math:`\eta_{l} = \sqrt{\mu \gamma_{o} P_{l} / (\hbar \omega_{l})}`, with :math:`\omega_{l} = 2 \pi c / \lambda_{l}`.

        Parameters
        ----------
        lambda_l : float or numpy.float
            Wavelength of the laser.  
        mu : float or numpy.float
            Laser-cavity coupling parameter.
        gamma_o : float or numpy.float
            Optical decay rate.
        P_l : float or numpy.float
            Power of the laser.
        Delta : float or numpy.float
            Effective detuning if mode is 'basic', else detuning of the laser.
        G : float or numpy.float
            Frequency pull parameter.
        C : float or numpy.float, optional
            Coefficient of :math:`|\alpha_{s}|^{2}`.
        mode : str, optional
            Mode of calculation of intracavity photon number:
                * 'basic' : Assuming constant effective detuning.
                * 'cubic' : Cubic variation with laser detuning.
        
        Returns
        -------
        alpha_s : float or numpy.float or list
            Mean optical amplitude.
        """

        # basic mode
        if mode == 'basic':
            # get amplitude of the laser
            omega_l = 2 * np.pi * sc.c / lambda_l
            eta_l = np.sqrt(mu * gamma_o * P_l / sc.hbar / omega_l)
            # mean optical amplitude
            alpha_s = eta_l / (gamma_o / 2 - 1j * Delta)
        
        # cubic mode
        elif mode == 'cubic':
            # get mean optical occupancy
            N_o = self.get_mean_optical_occupancy(lambda_l, mu, gamma_o, P_l, Delta, C, 'cubic')
            # mean optical amplitude
            alpha_s = np.sqrt(N_o).tolist()

        # return
        return alpha_s

    def get_mean_optical_occupancy(self, lambda_l: t_float, mu: t_float, gamma_o: t_float, P_l: t_float, Delta: t_float, C: t_float=0, mode='basic'):
        r"""Method to obtain the mean optical occupancy.

        The mean optical occupancy can be written as [1],

        .. math::
            N_{o} = |\alpha_{s}|^{2} = \frac{\eta_{l}^{2}}{\frac{\gamma_{o}^{2}}{4} + \Delta^{2}}

        where :math:`\Delta = \Delta_{l} + C N_{o}`, :math:`\eta_{l} = \sqrt{\mu \gamma_{o} P_{l} / (\hbar \omega_{l})}`, with :math:`\omega_{l} = 2 \pi c / \lambda_{l}`.

        Parameters
        ----------
        lambda_l : float or numpy.float
            Wavelength of the laser.
        mu : float or numpy.float
            Laser-cavity coupling parameter.
        gamma_o : float or numpy.float
            Optical decay rate.
        P_l : float or numpy.float
            Power of the laser.
        Delta : float or numpy.float
            Effective detuning if mode is 'basic', else detuning of the laser.
        C : float or numpy.float, optional
            Coefficient of :math:`N_{o}` in the expression of :math:`\Delta`.
        mode : str, optional
            Mode of calculation of intracavity photon number:
                * 'basic' : Assuming constant effective detuning.
                * 'cubic' : Cubic variation with laser detuning.
        
        Returns
        -------
        N_o : float or numpy.float or list
            Mean optical amplitude.
        """

        # basic mode
        if mode == 'basic':
            # get mean optical amplitude
            alpha_s = self.get_mean_optical_amplitude(lambda_l, mu, gamma_o, P_l, Delta)
            # mean optical occupancy
            N_o = np.real(np.conjugate(alpha_s) * alpha_s)

        # cubic mode
        elif mode == 'cubic':
            # get amplitude of the laser
            omega_l = 2 * np.pi * sc.c / lambda_l
            eta_l = np.sqrt(mu * gamma_o * P_l / sc.hbar / omega_l)

            # get coefficients
            coeff_0 = 4 * C**2
            coeff_1 = 8 * C * Delta
            coeff_2 = 4 * Delta**2 + gamma_o**2
            coeff_3 = - 4 * eta_l**2

            # get roots
            roots = np.roots([coeff_0, coeff_1, coeff_2, coeff_3])

            # mean optical occupancy
            N_o = list()
            # retain real roots
            for root in roots:
                if np.imag(root) == 0.0:
                    N_o.append(np.real(root))

        # return
        return N_o

    def get_measure_average(self, solver_params: dict, ode_func, get_ivc, ode_func_corrs=None, plot: bool=False, plotter_params: dict=None):
        """Method to obtain the average value of a measure.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        get_ivc : function
            Function returning the initial values and constants.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations.
        plot: bool, optional
            Option to plot the measures. Requires `plotter_params` parameter if `True`.
        plotter_params: dict, optional
            Parameters for the plotter.
        
        Returns
        -------
        M_avg : float
            Average value of the measures.
        """

        # get measures at all times
        M, T = self.get_measure_dynamics(solver_params, ode_func, get_ivc, ode_func_corrs, plot, plotter_params)

        # calculate average over first axis
        M_avg = np.mean(M, 0)

        return M_avg
    
    def get_measure_dynamics(self, solver_params: dict, ode_func, get_ivc, ode_func_corrs=None, plot: bool=False, plotter_params: dict=None):
        """Method to obtain the dynamics of a particular measure.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        get_ivc : function
            Function returning the initial values and constants.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations.
        plot: bool, optional
            Option to plot the measures. Requires `plotter_params` parameter if `True`.
        plotter_params: dict, optional
            Parameters for the plotter.

        Returns
        -------
        M : list
            Measures calculated at all times.
        """

        # validate measure parameters
        self.__validate_params_measure(solver_params)

        # get mode and correlation dynamics
        Modes, Corrs, T = self.get_modes_corrs_dynamics(solver_params, ode_func, get_ivc, ode_func_corrs)

        # extract frequently used variables
        _show_progress = solver_params.get('show_progress', False)
        _range_min = solver_params.get('range_min', 0)
        _range_max = solver_params.get('range_max', len(T))
        _measure_type = solver_params['measure_type']
        _module_names = {
            'corr_ele': __name__,
            'mode_amp': __name__,
            'qcm': 'qom.solvers.QCMSolver'
        }

        # display initialization
        if _show_progress:
            logger.info('------------------Obtaining Measures-----------------\n')

        # initialize list
        M = list()

        # iterate for all times in given range
        for i in range(_range_min, _range_max):
            # update progress
            progress = float(i - _range_min)/float(_range_max - _range_min - 1) * 100
            # display progress
            if _show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Computing ({module_name}): Progress = {progress:3.2f}'.format(module_name=_module_names[_measure_type], progress=progress))

            # correlation matrix elements
            if _measure_type == 'corr_ele':
                measure = self.get_corr_ele(solver_params, Corrs[i])
            # mode amplidutes
            elif _measure_type == 'mode_amp':
                measure = self.get_mode_amp(solver_params, Modes[i])
            # quantum correlation measure
            elif _measure_type == 'qcm':
                measure = self.get_qcm(solver_params, Modes[i], Corrs[i])

            # update list
            M.append(measure)

        # display completion
        if _show_progress:
            logger.info('------------------Measures Obtained------------------\n')

        # plot measures
        if plot: 
            # display initialization
            if _show_progress:
                logger.info('------------------Initializing Plotter---------------\n')

            # plot
            self.plot_measures(plotter_params, T[_range_min:_range_max], M)

            # display completion
            if _show_progress:
                logger.info('------------------Results Plotted--------------------\n')

        return M, T[_range_min:_range_max]

    def get_measure_pearson(self, solver_params: dict, ode_func, get_ivc, ode_func_corrs=None, plot: bool=False, plotter_params: dict=None):
        r"""Method to obtain the Pearson synchronization measure.

        The implementation measure reads as [2],

        .. math::
            {S_{Pearson}}_{ij} = \frac{\Sigma_{t} \langle \delta O_{i} (t) \delta O_{j} (t) \rangle}{\sqrt{\Sigma_{t} \langle \delta O_{i}^{2} (t) \rangle} \sqrt{\Sigma_{t} \langle \delta O_{j}^{2} (t) \rangle}}

        where :math:`\delta O_{i}` and :math:`\delta O_{j}` are the corresponding quadratures of fluctuations.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        get_ivc : function
            Function returning the initial values and constants.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations.
        plot: bool, optional
            Option to plot the measures. Requires `plotter_params` parameter if `True`.
        plotter_params: dict, optional
            Parameters for the plotter.
        
        Returns
        -------
        S_Pearson : float
            Pearson synchronization measure.
        """

        # validate correlation matrix params
        self.__validate_params_corr_ele(solver_params, 3)

        # get measures at all times
        M, T = self.get_measure_dynamics(solver_params, ode_func, get_ivc, ode_func_corrs, plot, plotter_params)

        # get mean values
        mean_ii = np.mean([m[0] for m in M])
        mean_ij = np.mean([m[1] for m in M])
        mean_jj = np.mean([m[2] for m in M])

        # Pearson synchronztion measure
        S_Pearson = mean_ij / np.sqrt(mean_ii * mean_jj)

        return S_Pearson

    def get_measure_stationary(self, solver_params: dict, modes: list, corrs: list):
        """Method to obtain the a stationary measure.
        
        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        corrs : list
            Matrix of quantum correlations.
        modes : list
            Values of classical mode amplitudes.
        
        Returns
        -------
        measure : float
            The stationary measure.
        """

        # extract frequently used variables
        _show_progress = solver_params.get('show_progress', False)
        _measure_type = solver_params['measure_type']
        _module_names = {
            'corr_ele': __name__,
            'mode_amp': __name__,
            'qcm': 'qom.solvers.QCMSolver'
        }

        # display progress
        if _show_progress:
            logger.info('Computing ({module_name})...'.format(module_name=_module_names[_measure_type]))

        # correlation matrix elements
        if _measure_type == 'corr_ele':
            measure = self.get_corr_ele(solver_params, corrs)
        # mode amplidutes
        elif _measure_type == 'mode_amp':
            measure = self.get_mode_amp(solver_params, modes)
        # quantum correlation measure
        elif _measure_type == 'qcm':
            measure = self.get_qcm(solver_params, modes, corrs)

        return measure

    def get_mode_amp(self, solver_params: dict, modes: list):
        """Method to obtain the amplitude of a particular mode.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        modes : list
            Values of classical mode amplitudes.

        Returns
        -------
        amp : list
            Calculated amplitudes.
        """

        # extract frequently used variables
        _idx_mode = solver_params['idx_mode']
        
        # single mode
        if type(_idx_mode) is int:
            _idx_mode = [_idx_mode]
        
        # extract amplitude
        amp = [modes[idx] for idx in _idx_mode]

        return amp

    def get_modes_corrs_dynamics(self, solver_params: dict, ode_func, get_ivc, ode_func_corrs=None):
        """Method to obtain the dynamics of the classical mode amplitudes and quantum correlations from the Heisenberg and Lyapunov equations.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        get_ivc : function
            Function returning the initial values and constants.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations.

        Returns
        -------
        Modes : list
            All the modes calculated at all times.
        Corrs : list
            All the correlations calculated at all times.
        T : list
            Times at which values are calculated.
        """

        # extract frequently used variables
        _method = solver_params.get('method', 'RK45')
        _cache = solver_params.get('cache', False)
        _cache_dir = solver_params.get('cache_dir', 'data')
        _cache_file = solver_params.get('cache_file', 'V')

        # get initial values and constants
        iv, c = get_ivc()
        # handle null constants
        if c is None:
            c = list()

        # initialize solver
        solver = HLESolver(solver_params)

        # cache path
        if _cache:
            # update directory
            if _cache_dir == 'data':
                _cache_dir += '\\' + self.code + '\\' + str(solver.T[0]) + '_' + str(solver.T[-1]) + '_' + str(len(solver.T))
            # update filename
            if _cache_file == 'V' and self.params is not None:
                for key in self.params:
                    _cache_file += '_' + str(self.params[key])
        
        # solve and set results
        solver.solve(ode_func, iv, c, ode_func_corrs, self.num_modes, _method, _cache, _cache_dir, _cache_file)

        # get modes, correlations and times
        Modes = solver.get_Modes(self.num_modes)
        Corrs = solver.get_Corrs(self.num_modes)
        T = solver.T
        
        return Modes, Corrs, T

    def get_modes_corrs_stationary(self, get_mode_rates, get_ivc, get_A, func_type: str='complex'):
        """Method to obtain the steady states of the classical mode amplitudes and quantum correlations from the Heisenberg and Lyapunov equations.

        Parameters
        ----------
        get_mode_rates : function
            Set of rates of the classical mode amplitudes for a given list of modes. If the function is complex-valued, `func_type` parameter should be passed as 'complex'.
        get_ivc : function
            Function returning the initial values and constants.
        get_A : function
            Function to obtain the drift matrix given the list of modes as parameter.
        func_type : str, optional
            Return data-type of `ode_func_modes`. Available options are:
                'real' : Real-valued.
                'complex' : Complex-valued.

        Returns
        -------
        modes : list
            All the modes calculated at steady-state.
        corrs : list
            All the correlations calculated at steady-state.
        """

        # extract the modes and correlations
        _dim = 2 * self.num_modes

        # get initial values and constants
        iv, c = get_ivc()
        # handle null constants
        if c is None:
            c = list()

        # get parameters
        if len(c) >= _dim**2:
            params = c[_dim**2:]
        else: 
            params = list()

        # if modes are to be calculated
        if get_mode_rates is not None:
            # complex-valued function
            if func_type == 'complex':
                # real-valued function
                def get_mode_rates_real(modes_real):
                    """Function to obtain the rates of the optical and mechanical modes.
                    
                    Returns
                    -------
                    modes_real : list
                        List of real-valued values of the modes.
                    
                    Returns
                    -------
                    mode_rates_real : list
                        List of real-valued rates splitted as real and imaginary parts for each mode.
                    """
                    
                    # convert to complex
                    modes = [modes_real[2 * i] + 1j * modes_real[2 * i + 1] for i in range(self.num_modes)]

                    # complex-valued mode rates
                    mode_rates = get_mode_rates(modes, params, np.inf)

                    # convert to real
                    mode_rates_real = list()
                    for mode_rate in mode_rates:
                        mode_rates_real.append(np.real(mode_rate))
                        mode_rates_real.append(np.imag(mode_rate))

                    return mode_rates_real

                # real-valued initial values
                iv_real = list()
                for mode in iv[:self.num_modes]:
                    iv_real.append(np.real(mode))
                    iv_real.append(np.imag(mode))
            else:
                # real-valued function
                get_mode_rates_real = get_mode_rates
                # real-valued initial values
                iv_real = iv
        
            # solve for modes
            roots_real = so.fsolve(get_mode_rates_real, iv_real)
            modes = [roots_real[2 * i] + 1j * roots_real[2 * i + 1] for i in range(int(len(roots_real) / 2))] 
        # modes not required
        else:
            modes = None

        # get matrices
        _A = get_A(modes, params, np.inf)
        _D = np.array(c[:_dim**2]).reshape((_dim, _dim))

        # convert to numpy arrays
        _A = np.array(_A) if type(_A) is list else _A
        _D = np.array(_D) if type(_D) is list else _D

        # solve for correlations
        corrs = sl.solve_lyapunov(_A, - _D)
        
        return modes, corrs

    def get_rhc_count_dynamics(self, solver_params: dict, ode_func, get_ivc, get_A, ode_func_corrs=None):
        """Function to obtain the number of positive real roots of the drift matrix using the Routh-Hurwitz criterion.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        get_ivc : function
            Function returning the initial values and constants.
        get_A : function
            Function to obtain the drift matrix given the list of modes and parameters.
        ode_func_corrs : function, optional
            Set of ODEs returning rate equations of the quantum correlations.
        
        Returns
        -------
        Counts : list
            Number of positive real roots of the drift matrix.
        """

        # get modes
        Modes, _, T = self.get_modes_corrs_dynamics(solver_params, ode_func, get_ivc, ode_func_corrs)

        # extract frequently used variables
        _show_progress = solver_params.get('show_progress', False)
        _range_min = solver_params.get('range_min', 0)
        _range_max = solver_params.get('range_max', len(T))
        _t_ss = solver_params.get('t_max', T[-1] - T[0]) / solver_params.get('t_dim', len(T))

        # extract parameters
        _, c = get_ivc()
        params = c[4 * self.num_modes**2:]

        # display initialization
        if _show_progress:
            logger.info('------------------Obtaining Counts-------------------\n')

        # initialize counter
        Counts = list()
        # iterate for all times in given range
        for i in range(_range_min, _range_max):
            # update progress
            progress = float(i - _range_min)/float(_range_max - _range_min - 1) * 100
            # display progress
            if _show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Computing ({module_name}): Progress = {progress:3.2f}'.format(module_name=__name__, progress=progress))
            # drift matrix

            A = get_A(Modes[i], params, i * _t_ss)
            # indices of the RHC sequence
            solver = RHCSolver(A)
            _idxs = solver.get_indices()
            # update counter
            Counts.append(len(_idxs))

        # display completion
        if _show_progress:
            logger.info('------------------Counts Obtained--------------------\n')

        return Counts, T[_range_min:_range_max]

    def get_qcm(self, solver_params: dict, modes: list, corrs: list):
        """Method to obtain a particular measure of quantum correlations.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        corrs : list
            Matrix of quantum correlations.
        modes : list
            Values of classical mode amplitudes.

        Returns
        -------
        measure : float
            Calculated measure.
        """

        # extract frequently used variables
        _qcm_type = solver_params['qcm_type']
        _idx_mode_i = solver_params['idx_mode_i']
        _idx_mode_j = solver_params['idx_mode_j']

        # get solver
        solver = QCMSolver(modes, corrs)
        # calculate measure
        measure = getattr(solver, 'get_' + _qcm_type)(_idx_mode_i, _idx_mode_j)
    
        return measure

    def ode_func(self, t, v, c):
        """Wrapper function for the rate equations of the modes and quadrature correlations.
        
        The variables are complex-valued, hence the model requires a complex-valued integrator.
        
        Parameters
        ----------
        t : *float*
            Time at which the rate is calculated.
        v : list
            Complex-valued variables defining the system.
        c : list
            Constants of the integration. First (4 * num_modes^2) elements contain the noise matrix. Remaining elements contain the constant parameters.

        Returns
        -------
        rates : list
            Rates of the complex-valued variables defining the system.
        """

        # extract the modes and correlations
        _dim    = [2 * self.num_modes, 2 * self.num_modes]
        modes   = v[0:self.num_modes]
        corrs   = np.real(v[self.num_modes:]).reshape(_dim)
        D       = np.array(c[:_dim[0] * _dim[1]]).reshape(_dim)
        if len(c) >= _dim[0] * _dim[1]:
            params = c[_dim[0] * _dim[1]:]
        else: 
            params = list()

        # mode rates
        mode_rates  = self.get_mode_rates(modes, params, t)

        # drift matrix
        A = self.get_A(modes, params, t)

        # quadrature correlation rate equation
        dcorrs_dt = A.dot(corrs) + corrs.dot(np.transpose(A)) + D

        # mirror matrix
        for i in range(len(dcorrs_dt)):
            for j in range(0, i):
                dcorrs_dt[i, j] = dcorrs_dt[j, i]

        # convert to 1D list and concatenate all rates
        rates = mode_rates + [np.complex(element) for element in dcorrs_dt.flatten()]

        return rates

    def plot_measures(self, plotter_params: dict, T: list, M: list):
        """Method to plot the measures.
        
        Parameters
        ----------
        plotter_params : dict
            Parameters for the plotter.
        T : list
            Times at which values are calculated.
        M : list
            Measures calculated at all times.
        """

        # validate parameters
        assert plotter_params is not None, 'Parameter `plotter_params` should be a dictionary containing the key `type`'
        assert 'type' in plotter_params and plotter_params['type'] in self.types_plots, 'Parameter `plotter_params` should contain key `type` with values in {}'.format(self.types_plots)

        # initialize plot
        plotter = MPLPlotter({'X': T}, plotter_params)
        
        # update plotter
        plotter.update(xs=T, vs=M)
        plotter.show(True)