#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface optomechanical systems."""

__name__    = 'qom.systems.BaseSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2021-01-13'

# dependencies
from typing import Union
import logging
import numpy as np
import scipy.constants as sc

# qom modules
from qom.solvers import HLESolver
from qom.solvers import QCMSolver
from qom.ui.plotters import MPLPlotter

# module logger
logger = logging.getLogger(__name__)

# datatypes
t_array = Union[list, np.matrix, np.ndarray]
t_float = Union[float, np.float32, np.float64]

# TODO: Handle other measures in `get_dynamics_measure`.

class BaseSystem():
    """Class to interface optomechanical systems.

    Initializes `params` property.

    References:

    [1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86** (4), 1931 (2014).

    Parameters
    ----------
    params : dict
        Parameters for the system.
    """

    @property
    def code(self):
        """str: Short code for the system."""

        return self.__code

    @code.setter
    def code(self, code):
        self.__code = code

    @property
    def name(self):
        """str: Name of the system."""

        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def num_modes(self):
        """int: Number of classical modes."""

        return self.__num_modes

    @num_modes.setter
    def num_modes(self, num_modes):
        self.__num_modes = num_modes

    @property
    def params(self):
        """dict: Parameters for the system."""

        return self.__params

    @params.setter
    def params(self, params):
        self.__params = params

    def __init__(self, params: dict):
        """Class constructor for BaseSystem."""

        # set params
        self.params = params

    def __get_qcm(self, solver_params: dict, corrs: list, modes: list):
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

        # validate parameters
        _supported_types = [func[4:] for func in dir(QCMSolver) if callable(getattr(QCMSolver, func)) and func[:4] == 'get_']
        assert 'qcm_type' in solver_params, 'Solver parameters should contain key "qcm_type" for the type of correlation.'
        assert solver_params['qcm_type'] in _supported_types, 'Supported quantum correlation measures are {}'.format(str(_supported_types))
        
        # validate parameters
        for key in ['idx_mode_i', 'idx_mode_j']:
            assert key in solver_params, 'Solver parameters should contain the keys "idx_mode_i" and "idx_mode_j" for synchronization'

        # extract frequently used variables
        qcm_type = solver_params['qcm_type']
        idx_mode_i = solver_params['idx_mode_i']
        idx_mode_j = solver_params['idx_mode_j']

        # get solver
        solver = QCMSolver(modes, corrs)
        measure = getattr(solver, 'get_' + qcm_type)(idx_mode_i, idx_mode_j)
    
        return measure
    
    def get_dynamics_measure(self, solver_params: dict, ode_func, ivc_func, ode_func_corrs=None, plot: bool=False, plotter_params: dict=None):
        """Method to obtain the dynamics of a particular measure.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        ivc_func : function
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

        # validate parameters
        _supported_types = ['qcm']
        assert 'measure_type' in solver_params, 'Solver parameters should contain key "measure_type" for the type of measure.'
        assert solver_params['measure_type'] in _supported_types, 'Supported types of measures are {}'.format(str(_supported_types))

        # get mode and correlation dynamics
        _Modes, _Corrs, _T = self.get_dynamics_modes_corrs(solver_params, ode_func, ivc_func, ode_func_corrs)

        # extract frequently used variables
        show_progress = solver_params.get('show_progress', False)
        _range_min = solver_params.get('range_min', 0)
        _range_max = solver_params.get('range_max', len(_T))
        _measure_type = solver_params.get('measure_type', 'qcm')
        _module_names = {
            'qcm': 'qom.solvers.QCMSolver'
        }

        # display initialization
        if show_progress:
            logger.info('------------------Obtaining Measures-----------------\n')

        # initialize list
        M = list()

        # iterate for all times in given range
        for i in range(_range_min, _range_max):
            # update progress
            progress = float(i - _range_min)/float(_range_max - _range_min - 1) * 100
            # display progress
            if show_progress and int(progress * 1000) % 10 == 0:
                logger.info('Computing ({module_name}): Progress = {progress:3.2f}'.format(module_name=_module_names[_measure_type], progress=progress))

            # get quantum correlation measure
            if _measure_type == 'qcm':
                measure = self.__get_qcm(solver_params, _Corrs[i], _Modes[i])

            # update list
            M.append(measure)

        # display completion
        if show_progress:
            logger.info('------------------Measures Obtained------------------\n')

        # plot measures
        if plot: 
            # display initialization
            if show_progress:
                logger.info('------------------Initializing Plotter---------------\n')

            # plot
            self.plot_measures(plotter_params, _T[_range_min:_range_max], M)

            # display completion
            if show_progress:
                logger.info('------------------Results Plotted--------------------\n')

        return M

    def get_dynamics_modes_corrs(self, solver_params: dict, ode_func, ivc_func, ode_func_corrs=None):
        """Method to obtain the dynamics of the classical mode amplitudes and quantum correlations from the Heisenberg and Lyapunov equations.

        Parameters
        ----------
        solver_params : dict
            Parameters for the solver.
        ode_func : function
            Set of ODEs returning rate equations of the classical mode amplitudes and quantum correlations. If `ode_func_corrs` parameter is given, this function is treated as the function for the modes only.
        ivc_func : function
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
        solver_method = solver_params.get('method', 'RK45')
        cache = solver_params.get('cache', False)
        cache_dir = solver_params.get('cache_dir', 'data')
        cache_file = solver_params.get('cache_file', 'V')

        # get initial values and constants
        _iv, _c = ivc_func()

        # initialize solver
        solver = HLESolver(solver_params)

        # cache path
        if cache:
            # update directory
            cache_dir += '\\' + self.code + '\\' + str(solver.T[0]) + '_' + str(solver.T[-1]) + '_' + str(len(solver.T))
            # upate filename
            if cache_file == 'V' and self.params is not None:
                for key in self.params:
                    cache_file += '_' + str(self.params[key])
        
        # solve and set results
        solver.solve(ode_func, _iv, _c, ode_func_corrs, self.num_modes, solver_method, cache, cache_dir, cache_file)

        # get modes, correlations and times
        Modes = solver.get_Modes(self.num_modes)
        Corrs = solver.get_Corrs(self.num_modes)
        T = solver.T
        
        return Modes, Corrs, T

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
            N_o = np.conjugate(alpha_s) * alpha_s

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
        _supported_types = MPLPlotter.types_1D + MPLPlotter.types_2D + MPLPlotter.types_3D
        assert plotter_params is not None, 'Parameter `plotter_params` should be a dictionary containing the key `type`.'
        assert 'type' in plotter_params and plotter_params['type'] in _supported_types, 'Parameter `plotter_params` should contain key `type` with values in {}.'.format(_supported_types)

        # initialize plot
        plotter = MPLPlotter({'X': T}, plotter_params)
        
        # update plotter
        plotter.update(xs=T, vs=M)
        plotter.show(True)