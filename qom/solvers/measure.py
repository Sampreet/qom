#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module to solve for various classical and quantum signatures and system measures.

References
----------

.. [1] R. Simon, *Peres-Horodechi Separability Criterion for Continuous Variable Systems*, Phys. Rev. Lett. **84**, 2726 (2000).

.. [2] D. Vitali, S. Gigan, A. Ferreira, H. R. Bohm, P. Tombesi, A. Guerreiro, V. Vedral, A. Zeilinger and M. Aspelmeyer, *Quantum Entanglement between a Movable Mirror and a Cavity Field*, Phys. Rev. Lett. **98**, 030405 (2007).

.. [3] S. Olivares, *Quantum Optics in Phase Space: A Tutorial on Gaussian States*, Eur. Phys. J. Special Topics **203**, 3 (2012).

.. [4] M. Ludwig and F. Marquardt, *Quantum Many-body Dynamics in Optomechanical Arrays*, Phys. Rev. Lett. **111**, 073603 (2013).

.. [5] A. Mari, A. Farace, N. Didier, V. Giovannetti and R. Fazio, *Measures of Quantum Synchronization in Continuous Variable Systems*, Phys. Rev. Lett. **111**, 103605 (2013).

.. [6] F. Galve, G. L. Giorgi and R. Zambrini, *Quantum Correlations and Synchronization Measures*, Lectures on General Quantum Correlations and their Applications, Quantum Science and Technology, Springer (2017).

.. [7] N. Yang, A. Miranowicz, Y.-C. Liu, K. Xia and F. Nori, *Chaotic Synchronization of Two Optical Cavity Modes in Optomechanical Systems*, Sci. Rep. ***9***, 15874 (2019).

.. [8] T. F. Roque, F. Marquardt and O. M. Yevtushenko, *Nonlinear Dynamics of Weakly Dissipative Optomechanical Systems*, New J. Phys. **22**, 013049 (2020).
"""

__name__ = 'qom.solvers.measure'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-01-04"
__updated__ = "2023-08-13"

# dependencies
from typing import Union
import inspect
import numpy as np
import scipy.linalg as sl

# qom modules
from .base import validate_Modes_Corrs, validate_system
from .differential import ODESolver
from ..io import Updater

class QCMSolver():
    r"""Class to solve for quantum correlation measures.

    Initializes ``Modes``, ``Corrs``, ``Omega_s`` (symplectic matrix), ``params`` and ``updater``.

    Parameters
    ----------
    Modes : numpy.ndarray
        Classical modes with shape ``(dim, num_modes)``.
    Corrs : numpy.ndarray
        Quadrature quadrature correlations with shape ``(dim, 2 * num_modes, 2 * num_modes)``.
    params : dict
        Parameters for the solver. Available options are:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
            'measure_codes'     (*list* or *str*) codenames of the measures to calculate. Options are ``'discord_G'`` for Gaussian quantum discord [3]_, ``'entan_ln'`` for quantum entanglement (using matrix multiplications, fallback) [1]_, ``'entan_ln_2'`` for quantum entanglement (using analytical expressions) [2]_, ``'sync_c'`` for complete quantum synchronization [4]_, ``'sync_p'`` for quantum phase synchronization [4]_]). Default is ``['entan_ln']``.
            'indices'           (*list* or *tuple*) indices of the modes as a list or tuple of two integers. Default is ``(0, 1)``.
            ================    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    """

    # attributes
    name = 'QCMSolver'
    """str : Name of the solver."""
    desc = "Quantum Correlations Measure Solver"
    """str : Description of the solver."""
    method_codes = {
        'corrs_P_p': 'get_correlation_Pearson',
        'corrs_P_q': 'get_correlation_Pearson',
        'discord_G': 'get_discord_Gaussian',
        'entan_ln': 'get_entanglement_logarithmic_negativity',
        'entan_ln_2': 'get_entanglement_logarithmic_negativity_2',
        'sync_c': 'get_synchronization_complete',
        'sync_p': 'get_synchronization_phase'
    }
    """dict : Codenames of available methods."""
    solver_defaults = {
        'show_progress': False,
        'measure_codes': ['entan_ln'],
        'indices': (0, 1)
    }
    """dict : Default parameters of the solver."""

    def __init__(self, Modes, Corrs, params:dict, cb_update=None):
        """Class constructor for QCMSolver."""

        # validate modes and correlations
        self.Modes, self.Corrs = validate_Modes_Corrs(
            Modes=Modes,
            Corrs=Corrs
        )

        # set symplectic matrix
        self.Omega_s = np.kron(np.eye(2, dtype=np.float_), np.array([[0, 1], [-1, 0]], dtype=np.float_))

        # set parameters
        self.set_params(params)

        # set updater
        self.updater = Updater(
            name='qom.solvers.QCMSolver',
            cb_update=cb_update
        )
        
    def set_params(self, params:dict):
        """Method to validate and set the solver parameters.

        Parameters
        ----------
        params : dict
            Parameters of the solver.
        """

        # check required parameters
        assert 'measure_codes' in params, "Parameter ``params`` does not contain a required key ``'measure_codes'``"
        assert 'indices' in params, "Parameter ``params`` does not contain a required key ``'indices'``"

        # extract frequently used variables
        measure_codes = params['measure_codes']
        indices = params['indices']
        _dim = len(self.Modes[0]) if self.Modes is not None else int(len(self.Corrs[0]) / 2)

        # validate measure type
        assert isinstance(measure_codes, Union[list, str].__args__), "Value of key ``'measure_codes'`` can only be of types ``list`` or ``str``"
        # convert to list
        measure_codes = [measure_codes] if type(measure_codes) is str else measure_codes
        # check elements
        for measure_code in measure_codes:
            assert measure_code in self.method_codes, "Elements of key ``'measure_codes'`` can only be one or more keys of ``{}``".format(self.method_codes.keys)
        # update parameter
        params['measure_codes'] = measure_codes

        # validate indices
        assert isinstance(indices, Union[list, tuple].__args__), "Value of key ``'indices'`` can only be of types ``list`` or ``tuple``"
        # convert to list
        indices = list(indices) if type(indices) is tuple else indices
        # check length
        assert len(indices) == 2, "Value of key ``'indices'`` can only have 2 elements"
        assert indices[0] < _dim and indices[1] < _dim, "Elements of key ``'indices'`` cannot exceed the total number of modes ({})".format(_dim)
        # update parameter
        params['indices'] = indices

        # set solver parameters
        self.params = dict()
        for key in self.solver_defaults:
            self.params[key] = params.get(key, self.solver_defaults[key])

    def get_measures(self):
        """Method to obtain the each measure.

        Returns
        -------
        Measures : numpy.ndarray
            Measures calculated with shape ``(dim, num_measure_codes)``.
        """

        # extract frequently used variables
        show_progress = self.params['show_progress']
        measure_codes = self.params['measure_codes']
        indices = self.params['indices']
        _dim = (len(self.Corrs), len(self.params['measure_codes']))

        # initialize measures
        Measures = np.zeros(_dim, dtype=np.float_)

        # find measures
        for j in range(_dim[1]):
            # display progress
            if show_progress:
                self.updater.update_progress(
                    pos=None,
                    dim=_dim[1],
                    status="-" * (35 - len(measure_codes[j])) + "Obtaining Measures (" + measure_codes[j] + ")",
                    reset=False
                )

            func_name = self.method_codes[measure_codes[j]]

            # calculate measure
            Measures[:, j]  = getattr(self, func_name)(pos_i=2 * indices[0], pos_j=2 * indices[1]) if 'corrs_P_p' not in measure_codes[j] else getattr(self, func_name)(pos_i=2 * indices[0] + 1, pos_j=2 * indices[1] + 1)

        # display completion
        if show_progress:
            self.updater.update_info(
                status="-" * 39 + "Measures Obtained"
            )

        return Measures
    
    def get_submatrices(self, pos_i:int, pos_j:int):
        """Helper function to obtain the block matrices of the required modes and its components.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Corrs_modes : numpy.ndarray
            Correlation matrix of the required modes.
        A: numpy.ndarray
            Correlation matrix of the first mode.
        B: numpy.ndarray
            Correlation matrix of the first mode.
        C: numpy.ndarray
            Correlation matrix of the cross mode.
        """

        # correlation matrix of the ith mode
        As = self.Corrs[:, pos_i:pos_i + 2, pos_i:pos_i + 2]
        # correlation matrix of the jth mode
        Bs = self.Corrs[:, pos_j:pos_j + 2, pos_j:pos_j + 2]
        # correlation matrix of the intermodes
        Cs = self.Corrs[:, pos_i:pos_i + 2, pos_j:pos_j + 2]

        # get transposes matrices
        C_Ts = np.array(np.transpose(Cs, axes=(0, 2, 1)))

        # get block matrices
        Corrs_modes = np.concatenate((np.concatenate((As, Cs), axis=2), np.concatenate((C_Ts, Bs), axis=2)), axis=1)

        # # correlation matrix of the two modes (slow)
        # Corrs_modes = np.array([np.block([[As[i], Cs[i]], [C_Ts[i], Bs[i]]]) for i in range(len(self.Corrs))], dtype=np.float_)

        return Corrs_modes, As, Bs, Cs

    def get_invariants(self, pos_i:int, pos_j:int):
        """Helper function to calculate symplectic invariants for two modes given the correlation matrices of their quadratures.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int8
            Index of jth quadrature.

        Returns
        -------
        I_1s : numpy.ndarray
            Determinants of ``A``.
        I_2s : numpy.ndarray
            Determinants of ``B``.
        I_3s : numpy.ndarray
            Determinants of ``C``.
        I_4s : numpy.ndarray
            Determinants of ``corrs_modes``.
        """

        # get block matrices and its components
        Corrs_modes, As, Bs, Cs = self.get_submatrices(
            pos_i=pos_i,
            pos_j=pos_j
        )

        # symplectic invariants
        return np.linalg.det(As), np.linalg.det(Bs), np.linalg.det(Cs), np.linalg.det(Corrs_modes)
    
    def get_correlation_Pearson(self, pos_i:int, pos_j:int):
        r"""Method to obtain the Pearson correlation coefficient.

        The implementation measure reads as [6]_,

        .. math::

            C_{ij} = \frac{\Sigma_{t} \langle \delta \mathcal{O}_{i} (t) \delta \mathcal{O}_{j} (t) \rangle}{\sqrt{\Sigma_{t} \langle \delta \mathcal{O}_{i}^{2} (t) \rangle} \sqrt{\Sigma_{t} \langle \delta \mathcal{O}_{j}^{2} (t) \rangle}}

        where :math:`\delta \mathcal{O}_{i}` and :math:`\delta \mathcal{O}_{j}` are the corresponding quadratures of quantum fluctuations.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Corr_P : float
            Pearson correlation coefficients.
        """

        # extract mean values of correlation elements
        mean_ii = np.mean(self.Corrs[:, pos_i, pos_i])
        mean_ij = np.mean(self.Corrs[:, pos_i, pos_j])
        mean_jj = np.mean(self.Corrs[:, pos_j, pos_j])

        # Pearson correlation coefficient as a repeated array
        return np.array([mean_ij / np.sqrt(mean_ii * mean_jj)] * len(self.Corrs), dtype=np.float_)

    def get_discord_Gaussian(self, pos_i:int, pos_j:int):
        """Method to obtain Gaussian quantum discord values [3]_.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Discord_G : numpy.ndarray
            Gaussian quantum discord values.
        """

        # initialize values
        mu_pluses = np.zeros(len(self.Corrs), dtype=np.float_)
        mu_minuses = np.zeros(len(self.Corrs), dtype=np.float_)
        Ws = np.zeros(len(self.Corrs), dtype=np.float_)
        Discord_G = np.zeros(len(self.Corrs), dtype=np.float_)

        # get symplectic invariants
        I_1s, I_2s, I_3s, I_4s = self.get_invariants(
            pos_i=pos_i,
            pos_j=pos_j
        )

        # sum of symplectic invariants
        sigmas = I_1s + I_2s + 2 * I_3s
        # discriminants of the simplectic eigenvalues
        _discriminants = sigmas**2 - 4 * I_4s
        # check sqrt condition
        conditions_mu = np.logical_and(_discriminants >= 0.0, I_4s >= 0.0)
        # update valid symplectic eigenvalues
        mu_pluses[conditions_mu] = 1 / np.sqrt(2) * np.sqrt(sigmas[conditions_mu] + np.sqrt(_discriminants[conditions_mu]))
        mu_minuses[conditions_mu] = 1 / np.sqrt(2) * np.sqrt(sigmas[conditions_mu] - np.sqrt(_discriminants[conditions_mu]))

        # check main condition on W values
        conditions_W = 4 * (np.multiply(I_1s, I_2s) - I_4s)**2 / (I_1s + 4 * I_4s) / (1 + 4 * I_2s) / I_3s**2 <= 1.0
        # W values with main condition
        # check sqrt and NaN condition
        _discriminants = 4 * I_3s**2 + np.multiply(4 * I_2s - 1, 4 * I_4s - I_1s)
        _divisors = 4 * I_2s - 1
        conditions_W_1 = np.logical_and(conditions_W, np.logical_and(_discriminants >= 0.0, _divisors != 0.0))
        # update W values
        Ws[conditions_W_1] = ((2 * np.abs(I_3s[conditions_W_1]) + np.sqrt(_discriminants[conditions_W_1])) / _divisors[conditions_W_1])**2
        # W values without main condition
        # check sqrt and NaN condtition 
        _bs = np.multiply(I_1s, I_2s) + I_4s - I_3s**2
        _4acs = 4 * np.multiply(np.multiply(I_1s, I_2s), I_4s)
        _discriminants = _bs**2 - _4acs
        conditions_W_2 = np.logical_and(np.logical_not(conditions_W), np.logical_and(_discriminants >= 0.0, I_2s != 0.0))
        # update W values
        Ws[conditions_W_2] = (_bs[conditions_W_2] - np.sqrt(_bs[conditions_W_2]**2 - _4acs[conditions_W_2])) / 2 / I_2s[conditions_W_2]

        # all validity conditions
        conditions = np.logical_and(conditions_mu, np.logical_or(conditions_W_1, conditions_W_2))

        # f function 
        func_f = lambda x: np.multiply(x + 0.5, np.log10(x + 0.5)) - np.multiply(x - 0.5, np.log10(x - 1 / 2))
            
        # update quantum discord values
        Discord_G[conditions] = func_f(np.sqrt(I_2s[conditions])) \
                                - func_f(mu_pluses[conditions]) \
                                - func_f(mu_minuses[conditions]) \
                                + func_f(np.sqrt(Ws[conditions]))

        return Discord_G
    
    def get_entanglement_logarithmic_negativity(self, pos_i:int, pos_j:int):
        """Method to obtain the logarithmic negativity entanglement values using matrices [1]_.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Entan_lns : numpy.ndarray
            Logarithmic negativity entanglement values using matrices.
        """

        # get correlation matrix and its components
        Corrs_modes, _, _, _  = self.get_submatrices(
            pos_i=pos_i,
            pos_j=pos_j
        )

        # PPT criteria
        Corrs_modes[:, :, -1] = - Corrs_modes[:, :, -1]
        Corrs_modes[:, -1, :] = - Corrs_modes[:, -1, :]

        # smallest symplectic eigenvalue
        eigs, _ = np.linalg.eig(np.matmul(self.Omega_s, Corrs_modes))
        eig_min = np.min(np.abs(eigs), axis=1)

        # initialize entanglement
        Entan_ln = np.zeros_like(eig_min, dtype=np.float_)

        # update entanglement
        for i in range(len(eig_min)):
            if eig_min[i] < 0:
                Entan_ln[i] = 0
            else:
                Entan_ln[i] = np.maximum(0.0, - np.log(2 * eig_min[i]))

        return Entan_ln

    def get_entanglement_logarithmic_negativity_2(self, pos_i:int, pos_j:int):
        """Method to obtain the logarithmic negativity entanglement values using analytical expression [2]_.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Entan_ln : numpy.ndarray
            Logarithmic negativity entanglement values using analytical expression.
        """

        # initialize values
        Entan_ln = np.zeros(len(self.Corrs), dtype=np.float_)

        # symplectic invariants
        I_1s, I_2s, I_3s, I_4s = self.get_invariants(
            pos_i=pos_i,
            pos_j=pos_j
        )

        # sum of symplectic invariants after positive partial transpose
        sigmas = I_1s + I_2s - 2 * I_3s
        # discriminants of the simplectic eigenvalues
        discriminants = sigmas**2 - 4 * I_4s

        # check positive sqrt values
        conditions = np.logical_and(discriminants >= 0.0, I_4s >= 0.0)

        # calculate enganglement for positive sqrt values
        Entan_ln[conditions] = - 1 * np.log(2 / np.sqrt(2) * np.sqrt(sigmas[conditions] - np.sqrt(discriminants[conditions])))

        # clip negative values
        Entan_ln[Entan_ln < 0.0] = 0.0
        
        return Entan_ln
        
    def get_synchronization_complete(self, pos_i:int, pos_j:int):
        """Method to obtain the complete quantum synchronization values [5]_.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Sync_c : numpy.ndarray
            Complete quantum synchronization values.
        """

        # square difference between position quadratures
        q_minus_2s = 0.5 * (self.Corrs[:, pos_i, pos_i] + self.Corrs[:, pos_j, pos_j] - 2 * self.Corrs[:, pos_i, pos_j])
        # square difference between momentum quadratures
        p_minus_2s = 0.5 * (self.Corrs[:, pos_i + 1, pos_i + 1] + self.Corrs[:, pos_j + 1, pos_j + 1] - 2 * self.Corrs[:, pos_i + 1, pos_j + 1])

        # complete quantum synchronization values
        return 1.0 / (q_minus_2s + p_minus_2s)

    def get_synchronization_phase(self, pos_i:int, pos_j:int):
        """Method to obtain the quantum phase synchronization values [5]_.

        Parameters
        ----------
        pos_i : int
            Index of ith quadrature.
        pos_j : int
            Index of jth quadrature.

        Returns
        -------
        Sync_p : numpy.ndarray
            Quantum phase synchronization values.
        """

        # arguments of the modes
        arg_is = np.angle(self.Modes[:, int(pos_i / 2)])
        arg_js = np.angle(self.Modes[:, int(pos_j / 2)])

        # frequently used variables
        cos_is = np.cos(arg_is)
        cos_js = np.cos(arg_js)
        sin_is = np.sin(arg_is)
        sin_js = np.sin(arg_js)
        
        # transformation for ith mode momentum quadrature
        p_i_prime_2s = np.multiply(sin_is**2, self.Corrs[:, pos_i, pos_i]) \
                        - np.multiply(np.multiply(sin_is, cos_is), self.Corrs[:, pos_i, pos_i + 1]) \
                        - np.multiply(np.multiply(cos_is, sin_is), self.Corrs[:, pos_i + 1, pos_i]) \
                        + np.multiply(cos_is**2, self.Corrs[:, pos_i + 1, pos_i + 1])

        # transformation for jth mode momentum quadrature
        p_j_prime_2s = np.multiply(sin_js**2, self.Corrs[:, pos_j, pos_j]) \
                        - np.multiply(np.multiply(sin_js, cos_js), self.Corrs[:, pos_j, pos_j + 1]) \
                        - np.multiply(np.multiply(cos_js, sin_js), self.Corrs[:, pos_j + 1, pos_j]) \
                        + np.multiply(cos_js**2, self.Corrs[:, pos_j + 1, pos_j + 1])

        # transformation for intermode momentum quadratures
        p_i_p_j_primes = np.multiply(np.multiply(sin_is, sin_js), self.Corrs[:, pos_i, pos_j]) \
                        - np.multiply(np.multiply(sin_is, cos_js), self.Corrs[:, pos_i, pos_j + 1]) \
                        - np.multiply(np.multiply(cos_is, sin_js), self.Corrs[:, pos_i + 1, pos_j]) \
                        + np.multiply(np.multiply(cos_is, cos_js), self.Corrs[:, pos_i + 1, pos_j + 1])

        # square difference between momentum quadratures
        p_minus_prime_2s = 0.5 * (p_i_prime_2s + p_j_prime_2s - 2 * p_i_p_j_primes)

        # quantum phase synchronization values
        return 0.5 / p_minus_prime_2s

def get_average_amplitude_difference(Modes):
    """Method to obtain the average amplitude differences for two specific modes [7]_.
    
    Parameters
    ----------
    Modes : numpy.ndarray
        The two specific modes with shape ``(dim, 2)``.

    Returns
    -------
    diff_a : float
        The average amplitude difference.
    """

    # validate modes
    assert Modes is not None and (type(Modes) is list or type(Modes) is np.ndarray) and np.shape(Modes)[1] == 2, "Parameter ``Modes`` should be a list or NumPy array with dimension ``(dim, 2)``"

    # get means
    means = np.mean(Modes, axis=0)
    
    # average amplitude difference
    return np.mean([np.linalg.norm(modes[0] - means[0]) - np.linalg.norm(modes[1]- means[1]) for modes in Modes])

def get_average_phase_difference(Modes):
    """Method to obtain the average phase differences for two specific modes [4]_.
    
    Parameters
    ----------
    Modes : numpy.ndarray
        The two specific modes with shape ``(dim, 2)``.

    Returns
    -------
    diff_p : float
        The average phase difference.
    """

    # validate modes
    assert Modes is not None and (type(Modes) is list or type(Modes) is np.ndarray) and np.shape(Modes)[1] == 2, "Parameter ``Modes`` should be a list or NumPy array with dimension ``(dim, 2)``"

    # get means
    means = np.mean(Modes, axis=0)
    
    # average phase difference
    return np.mean([np.angle(modes[0] - means[0]) - np.angle(modes[1]- means[1]) for modes in Modes])

def get_bifurcation_amplitudes(Modes):
    """Method to obtain the bifurcation amplitudes of the modes.
    
    Parameters
    ----------
    Modes : numpy.ndarray
        The mode amplitudes in the trajectory with shape ``(dim, num_modes)``.

    Returns
    -------
    Amps : list
        The bifurcation amplitudes of the modes. The first ``num_modes`` arrays contain the bifurcation amplitudes of the real parts of the modes; the next ``num_modes`` arrays contain those of the imaginary parts.
    """

    # validate modes
    assert Modes is not None and (type(Modes) is list or type(Modes) is np.ndarray) and len(np.shape(Modes)) == 2, "Parameter ``Modes`` should be a list or NumPy array with dimension ``(dim, num_modes)``"

    # convert to real
    Modes_real = np.concatenate((np.real(Modes), np.imag(Modes)), axis=1, dtype=np.float_)

    # calculate gradients
    grads = np.gradient(Modes_real, axis=0)
    
    # get indices where the derivative changes sign
    idxs = grads[:-1, :] * grads[1:, :] < 0

    Amps = list()
    for i in range(idxs.shape[1]):
        # collect all crests and troughs
        extremas = Modes_real[:-1, i][idxs[:, i]]
        # save absolute values of differences
        Amps.append(np.abs(extremas[:-1] - extremas[1:]))

    return Amps

def get_correlation_Pearson(Modes):
    r"""Method to obtain the Pearson correlation coefficient for two specific modes [6]_.

    .. math::

        C_{ij} = \frac{\Sigma_{t} \langle \mathcal{O}_{i} (t) \mathcal{O}_{j} (t) \rangle}{\sqrt{\Sigma_{t} \langle \mathcal{O}_{i}^{2} (t) \rangle} \sqrt{\Sigma_{t} \langle \mathcal{O}_{j}^{2} (t) \rangle}}

    where :math:`\mathcal{O}_{i}` and :math:`\mathcal{O}_{j}` are the corresponding modes.
    
    Parameters
    ----------
    Modes : numpy.ndarray
        The two specific modes with shape ``(dim, 2)``.

    Returns
    -------
    corr_P : float
        Pearson correlation coefficient.
    """

    # validate modes
    assert Modes is not None and (type(Modes) is list or type(Modes) is np.ndarray) and np.shape(Modes)[1] == 2, "Parameter ``Modes`` should be a list or NumPy array with dimension ``(dim, 2)``"

    # get means
    means = np.mean(Modes, axis=0)
    mean_ii = np.mean([np.linalg.norm(modes[0] - means[0])**2 for modes in Modes])
    mean_ij = np.mean([np.linalg.norm(modes[0] - means[0]) * np.linalg.norm(modes[1] - means[1]) for modes in Modes])
    mean_jj = np.mean([np.linalg.norm(modes[1] - means[1])**2 for modes in Modes])

    # Pearson correlation coefficient
    return mean_ij / np.sqrt(mean_ii * mean_jj)

def get_Lyapunov_exponents(system, modes, t=None, params:dict={}, cb_update=None):
    """Method to obtain the Lyapunov exponents [8]_.

    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system method ``get_ivc`` and ``get_A``.
    modes : numpy.ndarray
        Final classical modes with shape ``(num_modes, )``.
    t : numpy.ndarray, optional
        Final time of the evolution.
    params : dict
        Parameters for the solver. Refer to :class:`qom.solvers.deterministic.ODESolver` for all available options. Additionally available options are:
            ================    ====================================================
            key                 value
            ================    ====================================================
            'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
            'num_steps'         (*int*) number of additional time steps to calculate the deviations for Lyapunov exponents. Default value is ``1000``.
            'step_size'         (*float*) step size of each time step. Default value is ``0.1``.
            'use_svd'           (*bool*) option to use the singular value decomposition method to calculate the Lyapunov exponents. If ``False``, the Gram-Schmidt orthonormalization method is used. Default is ``True``.
            ================    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.

    Returns
    -------
    lambdas : numpy.ndarray
        Lyapunov exponents with shape ``(2 * num_modes, )``.
    """

    # validate system
    validate_system(
        system=system,
        required_system_attributes=['get_ivc', 'get_A']
    )

    # set updater
    updater = Updater(
        name=__name__,
        cb_update=cb_update
    )

    # extract frequently used variables
    show_progress = params.get('show_progress', False)
    num_steps = params.get('num_steps', 1000)
    step_size = params.get('step_size', 0.1)
    use_svd = params.get('use_svd', True)
    _num = system.num_modes
    _dim = system.dim_corrs

    # initialize variables
    _t = t if t is not None else 0.0
    _T = np.linspace(_t, _t + num_steps * step_size, num_steps + 1)
    _, _, c = system.get_ivc()

    # initialize buffer variables
    v = np.empty(2 * _num + system.num_corrs, dtype=np.float_)

    # initialize solver
    ode_solver = ODESolver(
        func=system.func_ode_modes_deviations,
        params=params,
        cb_update=cb_update
    )

    # use singular value decomposition    
    if use_svd:
        # update initial real-valued modes and flattened deviations
        v[:_num] = np.real(modes)
        v[_num:2 * _num] = np.imag(modes)
        v[2 * _num:] = np.identity(_dim[0], dtype=np.float_).ravel()

        # evolve and extract final deviations
        deviations = np.reshape(ode_solver.solve(
            T=_T,
            iv=v,
            c=c,
            func_c=None
        )[-1, 2 * _num:], _dim)

        # get singular values
        _, sigmas, _ = sl.svd(deviations)

        # get Lyapunov exponents
        lambdas = np.log10(sigmas) / num_steps / step_size
    # use Gram-Schmidt orthonormalization
    else:
        # update initial real-valued modes
        v[:_num] = np.real(modes)
        v[_num:2 * _num] = np.imag(modes)

        # solve for real-valued modes
        Modes_real = ode_solver.solve(
            T=_T,
            iv=v[:2 * _num],
            c=c,
            func_c=None
        )

        # initialize variables
        deviations = np.identity(_dim[0], dtype=np.float_)
        lambdas = np.zeros(_dim[0], dtype=np.float_)

        # iterate
        for k in range(1, num_steps + 1):
            # update progress
            if show_progress:
                updater.update_progress(
                    pos=k,
                    dim=num_steps,
                    status="-" * 10 + "Obtaining Lyapunov Exponents",
                    reset=False
                )

            # update deviations
            deviations += np.matmul(system.get_A(
                modes=Modes_real[k, :_num] + 1.0j * Modes_real[k, _num:],
                c=c,
                t=_T[k]
            ), deviations) * step_size

            # perform Gram-Schmidt orthonormalization
            deviations, R = np.linalg.qr(deviations)

            # update Lyapunov exponents
            lambdas += np.log10(np.abs(np.diag(R))) / num_steps / step_size

    # display completion
    if show_progress:
        updater.update_info(
            status="-" * 41 + "Measures Obtained"
        )

    return lambdas

def get_stability_zone(counts):
    """Function to obtain the stability zone given the number of unstable roots.

    Parameters
    ----------
    counts : list or numpy.ndarray
        Array of number of eigenvalues with positive real parts.
    
    Returns
    -------
    stability_zone : int
        Stability zone indicator of the optical steady state. The indicator is calculated in the following pattern:
            ========    ================================================
            value       meaning
            ========    ================================================
            0           one unstable root.
            1           one stable root.
            2           three unstable roots.
            3           one stable root and two unstable roots.
            4           two stable roots and one unstable root.
            5           three stable roots.
            6           five unstable roots.
            7           one stable root and four unstable roots.
            8           two stable roots and three unstable root.
            9           three stable roots and two unstable root.
            10          four stable roots and one unstable root.
            11          five stable roots.
            ========    ================================================
    """

    # handle list
    if type(counts) is list:
        counts = np.array(counts, dtype=np.int_)

    # frequently used variables
    n_unstable = np.sum(counts > 0)
    n_roots = len(counts)

    # set stability zone codes
    _codes = list()
    for j in range(n_roots):
        if j % 2 == 0:
            for i in range(j + 2):
                _codes.append(10 * i + (j - i + 1))

    #return stability zone
    return _codes.index(10 * (n_roots - n_unstable) + n_unstable)

def get_system_measures(system, Modes, T=None, params:dict={}, cb_update=None):
    """Method to obtain the measures from a system method.
    
    Parameters
    ----------
    system : :class:`qom.systems.*`
        Instance of the system. Requires predefined system method ``get_ivc`` and the getter for the system measure.
    Modes : numpy.ndarray
        Classical modes with shape ``(dim, num_modes)``.
    T : numpy.ndarray, optional
        Times with shape ``(dim, )``.
    params : dict
        Parameters for the solver. Available options are:
            ========================    ====================================================
            key                         value
            ========================    ====================================================
            'show_progress'             (*bool*) option to display the progress of the solver. Default is ``False``.
            'system_measure_name'       (*str*) name of the system measure to calculate. Requires a callable formatted with the prefix ``'get_'`` and arguments ``modes``, ``c`` and ``t``. For e.g., ``get_A(modes, c, t)``.
            ========================    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    
    Returns
    -------
    measures : numpy.ndarray
        Measures obtained with shape ``(dim, )`` plus the shape of each measure.
    """

    # validate parameters
    assert 'system_measure_name' in params, "Parameter ``'system_measure_name'`` is not defined"
    system_measure_name = params.get('system_measure_name', 'A')
    assert type(system_measure_name) is str, "Value of parameter ``'system_measure_name'`` should be a string"

    # validate system
    validate_system(
        system=system,
        required_system_attributes=['get_ivc', 'get_' + system_measure_name]
    )

    # validate method
    func = getattr(system, 'get_' + system_measure_name)
    # validate method arguments
    func_args = inspect.getfullargspec(func).args[1:]
    assert 'modes' in func_args[0] and 'c' in func_args[1] and 't' in func_args[2], "System method arguments should be 'modes', 'c' and 't'"

    # set updater
    updater = Updater(
        name=__name__,
        cb_update=cb_update
    )

    # extract frequently used variables
    show_progress = params.get('show_progress', False)
    _, _, c = system.get_ivc()
    _dim = len(Modes)

    # initialize measure
    measures = np.zeros((_dim, ) + np.shape(func(
        modes=Modes[0],
        c=c,
        t=T[0] if T is not None else None
    )), dtype=np.float_)

    # iterate over all times
    for i in range(_dim):
        # update progress
        if show_progress:
            updater.update_progress(
                pos=i,
                dim=_dim,
                status="-" * (17 - len(system_measure_name)) + "Obtaining Measures (" + system_measure_name + ")",
                reset=False
            )

        # get drift matrix
        measures[i] = func(
            modes=Modes[i],
            c=c,
            t=T[i] if T is not None else None
        )

    # display completion
    if show_progress:
        updater.update_info(
            status="-" * 41 + "Measures Obtained"
        )

    return measures

def get_Wigner_distributions_single_mode(Corrs, params, cb_update=None):
    """Method to obtain single-mode Wigner distribitions.
    
    Parameters
    ----------
    Corrs : numpy.ndarray
        Quadrature quadrature correlations with shape ``(dim, 2 * num_modes, 2 * num_modes)``.
    params : dict
        Parameters of the solver. Available options are:
        ================    ====================================================
        key                 value
        ================    ====================================================
        'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
        'indices'           (*list* or *tuple*) indices of the modes as a list. Default is ``[0]``.
        'wigner_xs'         (*list*) X-axis values.
        'wigner_ys'         (*list*) Y-axis values.
        ================    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    
    Returns
    -------
    Wigners : numpy.ndarray
        Single-mode Wigner distributions of shape ``(dim_1, dim_0, p_dim, q_dim)``, where ``dim_1`` and ``dim_0`` are the first dimensions of the correlations and the indices respectively.
    """

    # validate correlations
    validate_Modes_Corrs(
        Corrs=Corrs,
        is_corrs_required=True
    )

    # validate indices
    indices = params.get('indices', [0])
    assert isinstance(indices, Union[list, tuple].__args__), "Solver parameter ``'indices'`` should be a ``list`` or ``tuple`` of mode indices"

    # validate axes
    xs = params.get('wigner_xs', None)
    ys = params.get('wigner_ys', None)
    for val in [xs, ys]:
        assert val is not None and (type(val) is list or type(val) is np.ndarray), "Solver parameters ``'wigner_xs'`` and ``'wigner_ys'`` should be either NumPy arrays or ``list``"
    # handle list
    xs = np.array(xs, dtype=np.float_) if type(xs) is list else xs
    ys = np.array(ys, dtype=np.float_) if type(xs) is list else ys

    # set updater
    updater = Updater(
        name=__name__,
        cb_update=cb_update
    )

    # extract frequently used variables
    show_progress = params.get('show_progress', False)
    dim_m = len(indices)
    dim_c = len(Corrs)
    dim_w = len(ys) * len(xs)
    # get column vectors and row vectors
    _X, _Y = np.meshgrid(xs, ys)
    _dim = (ys.shape[0], xs.shape[0], 1, 1)
    Vects = np.concatenate((np.reshape(_X, _dim), np.reshape(_Y, _dim)), axis=2)
    Vects_t = np.transpose(Vects, axes=(0, 1, 3, 2))

    # initialize measures
    Wigners = np.zeros((dim_c, dim_m, ys.shape[0], xs.shape[0]), dtype=np.float_)

    # iterate over indices
    for j in range(dim_m):
        # get position
        pos = 2 * indices[j]

        # reduced correlation matrices
        V_pos = Corrs[:, pos:pos + 2, pos:pos + 2]
        invs = np.linalg.pinv(V_pos)
        dets = np.linalg.det(V_pos)

        # calculate dot product of inverse and column vectors
        _dots = np.transpose(np.dot(invs, Vects), axes=(4, 2, 3, 1, 0))[0]

        # get Wigner distributions
        for idx_y in range(len(ys)):
            for idx_x in range(len(xs)):
                # display progress
                if show_progress:
                    _index_status = str(j + 1) + "/" + str(dim_m) 
                    updater.update_progress(
                        pos=idx_y * len(xs) + idx_x,
                        dim=dim_w,
                        status="-" * (18 - len(_index_status)) + "Obtaining Wigners (" + _index_status + ")",
                        reset=False
                    )
                # wigner function
                Wigners[:, j, idx_y, idx_x] = np.exp(- 0.5 * np.dot(Vects_t[idx_y, idx_x], _dots[idx_y, idx_x])[0]) / 2.0 / np.pi / np.sqrt(dets)

    # display completion
    if show_progress:
        updater.update_info(
            status="-" * 41 + "Measures Obtained"
        )

    return Wigners

def get_Wigner_distributions_two_mode(Corrs, params, cb_update=None):
    """Method to obtain two-mode Wigner distribitions.
    
    Parameters
    ----------
    Corrs : numpy.ndarray
        Quadrature quadrature correlations with shape ``(dim, 2 * num_modes, 2 * num_modes)``.
    params : dict
        Parameters of the solver. Available options are:
        ================    ====================================================
        key                 value
        ================    ====================================================
        'show_progress'     (*bool*) option to display the progress of the solver. Default is ``False``.
        'indices'           (*list* or *tuple*) list of indices of the modes and their quadratures as tuples or lists. Default is ``[(0, 0), (1, 0)]``.
        'wigner_xs'         (*list*) X-axis values.
        'wigner_ys'         (*list*) Y-axis values.
        ================    ====================================================
    cb_update : callable, optional
        Callback function to update status and progress, formatted as ``cb_update(status, progress, reset)``, where ``status`` is a string, ``progress`` is a float and ``reset`` is a boolean.
    
    Returns
    -------
    Wigners : numpy.ndarray
        Two-mode Wigner distributions of shape ``(dim_0, p_dim, q_dim)``, where ``dim_0`` is the first dimension of the correlations.
    """

    # validate correlations
    validate_Modes_Corrs(
        Corrs=Corrs,
        is_corrs_required=True
    )

    # validate indices
    indices = params.get('indices', [(0, 0), (1, 0)])
    assert isinstance(indices, Union[list, tuple].__args__), "Solver parameter ``'indices'`` should be a ``list`` or ``tuple`` with each element being a ``list`` or ``tuple`` of the mode index and its quadrature index"
    for idxs in indices:
        assert isinstance(idxs, Union[list, tuple].__args__), "Each element of the indices should be a ``list`` or ``tuple`` of the mode index and its quadrature index"

    # validate axes
    xs = params.get('wigner_xs', None)
    ys = params.get('wigner_ys', None)
    for val in [xs, ys]:
        assert val is not None and (type(val) is list or type(val) is np.ndarray), "Solver parameters ``'wigner_xs'`` and ``'wigner_ys'`` should be either NumPy arrays or ``list``"
    # handle list
    xs = np.array(xs, dtype=np.float_) if type(xs) is list else xs
    ys = np.array(ys, dtype=np.float_) if type(xs) is list else ys

    # set updater
    updater = Updater(
        name=__name__,
        cb_update=cb_update
    )

    # extract frequently used variables
    show_progress = params.get('show_progress', False)
    indices = params.get('indices', [0])
    dim_m = len(indices)
    dim_c = len(Corrs)
    dim_w = len(ys) * len(xs)
    pos_i = 2 * indices[0][0]
    pos_j = 2 * indices[1][0]
    # get column vectors and row vectors
    _X, _Y = np.meshgrid(xs, ys)
    _dim = (ys.shape[0], xs.shape[0], 1, 1)
    Vects_a = np.concatenate((np.reshape(_X, _dim), np.zeros(_dim, dtype=np.float_)), axis=2) if indices[0][1] == 0 else np.concatenate((np.zeros(_dim, dtype=np.float_), np.reshape(_X, _dim)), axis=2)
    Vects_b = np.concatenate((np.reshape(_Y, _dim), np.zeros(_dim, dtype=np.float_)), axis=2) if indices[1][1] == 0 else np.concatenate((np.zeros(_dim, dtype=np.float_), np.reshape(_Y, _dim)), axis=2)
    Vects = np.concatenate((Vects_a, Vects_b), axis=2)
    Vects_t = np.transpose(Vects, axes=(0, 1, 3, 2))

    # initialize measures
    Wigners = np.zeros((dim_c, ys.shape[0], xs.shape[0]), dtype=np.float_)

    # correlation matrix of the ith mode
    As = Corrs[:, pos_i:pos_i + 2, pos_i:pos_i + 2]
    # correlation matrix of the jth mode
    Bs = Corrs[:, pos_j:pos_j + 2, pos_j:pos_j + 2]
    # correlation matrix of the intermodes
    Cs = Corrs[:, pos_i:pos_i + 2, pos_j:pos_j + 2]

    # get transposes matrices
    C_Ts = np.array(np.transpose(Cs, axes=(0, 2, 1)))

    # reduced correlation matrices
    V_pos = np.concatenate((np.concatenate((As, Cs), axis=2), np.concatenate((C_Ts, Bs), axis=2)), axis=1)
    invs = np.linalg.pinv(V_pos)
    dets = np.linalg.det(V_pos)

    # calculate dot product of inverse and column vectors
    _dots = np.transpose(np.dot(invs, Vects), axes=(4, 2, 3, 1, 0))[0]

    # get Wigner distributions
    for idx_y in range(len(ys)):
        for idx_x in range(len(xs)):
            # display progress
            if show_progress:
                updater.update_progress(
                    pos=idx_y * len(xs) + idx_x,
                    dim=dim_w,
                    status="-" * 21 + "Obtaining Wigners",
                    reset=False
                )
            # wigner function
            Wigners[:, idx_y, idx_x] = np.exp(- 0.5 * np.dot(Vects_t[idx_y, idx_x], _dots[idx_y, idx_x])[0]) / 4.0 / np.pi**2 / np.sqrt(dets)

    # display completion
    if show_progress:
        updater.update_info(
            status="-" * 41 + "Measures Obtained"
        )

    return Wigners