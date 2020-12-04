#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface an optomechanical system.

References:

[1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86** (4), 1931 (2014)."""

__name__    = 'qom.systems.BaseSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2020-12-04'

# dependencies
import logging
import numpy as np
import scipy.constants as sc

# module logger
logger = logging.getLogger(__name__)

class BaseSystem():
    """Class to interface an optomechanical system.

    Parameters
    ----------
    data : dict
        Data for the system.
    """

    @property
    def code(self):
        """str: Short code for the model."""

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
    def params(self):
        """dict: Base Parameters of the model."""

        return self.__params

    @params.setter
    def params(self, params):
        self.__params = params

    def __init__(self, data):
        """Class constructor for BaseSystem."""

        # validate parameters
        assert type(data) is dict, 'Data should be a `dict`'

    def get_intracavity_photon_number_basic(self, lambda_l, mu, gamma_o, P_l, Delta):
        r"""Method to obtain the intracavity photon number.

        The steady state is assumed to be of the form [1],

        .. math::
        
            \alpha_{s} = \frac{\eta_{l}}{\frac{\gamma_{o}}{2} - \iota \Delta}

        where :math:`\eta_{l} = \sqrt{\mu \gamma_{o} P_{l} / (\hbar \omega_{l})}`, with :math:`\omega_{l} = 2 \pi c / \lambda_{l}`.

        Parameters
        ----------
        lambda_l : float
            Wavelength of the laser.  
        mu : float
            Laser-cavity coupling parameter.
        gamma_o : float
            Optical decay rate.
        P_l : float
            Power of the laser.
        Delta : float
            Effective detuning.
        
        Returns
        -------
        N_o : float
            Intracavity photon number.
        """

        # validate parameters
        assert type(lambda_l) is float, 'Wavelength should be of type `float`'
        assert type(mu) is float, 'Laser-cavity coupling parameter should be of type `float`'
        assert type(gamma_o) is float, 'Optical decay rate should be of type `float`'
        assert type(P_l) is float, 'Power of the laser should be of type `float`'
        assert type(Delta) is float, 'Effective detuning should be of type `float`'

        # get amplitude of the laser
        omega_l = 2 * np.pi * sc.c / lambda_l
        eta_l = np.sqrt(mu * gamma_o * P_l / sc.hbar / omega_l)

        # get steady state amplitude
        alpha_s = eta_l / (gamma_o / 2 - 1j * Delta)

        # return intracavity photon number
        return np.real(np.conjugate(alpha_s) * alpha_s)

    def get_intracavity_photon_number_cubic(self, lambda_l, mu, gamma_o, P_l, Delta_l, C):
        r"""Method to obtain the intracavity photon number.

        The steady states are assumed to be of the form [1],

        .. math::
        
            \alpha_{s} = \frac{\eta_{l}}{\frac{\gamma_{o}}{2} - \iota (\Delta_{l} + C |\alpha_{s}|^{2})}

        where :math:`\eta_{l} = \sqrt{\mu \gamma_{o} P_{l} / (\hbar \omega_{l})}`, with :math:`\omega_{l} = 2 \pi c / \lambda_{l}`.

        Parameters
        ----------
        lambda_l : float
            Wavelength of the laser.
        mu : float
            Laser-cavity coupling parameter.
        gamma_o : float
            Optical decay rate.
        P_l : float
            Power of the laser.
        Delta_l : float
            Detuning of the laser.
        C : float
            Coefficient of :math:`|\alpha_{s}|^{2}`.
        
        Returns
        -------
        N_o : float
            Intracavity photon number.
        """

        # validate parameters
        assert type(lambda_l) is float, 'Wavelength should be of type `float`'
        assert type(mu) is float, 'Laser-cavity coupling parameter should be of type `float`'
        assert type(gamma_o) is float, 'Optical decay rate should be of type `float`'
        assert type(P_l) is float, 'Power of the laser should be of type `float`'
        assert type(Delta_l) is float, 'Detuning of the laser should be of type `float`'
        assert type(C) is float or type(C) is np.complex, 'Constant should be of type `float`'

        # get amplitude of the laser
        omega_l = 2 * np.pi * sc.c / lambda_l
        eta_l = np.sqrt(mu * gamma_o * P_l / sc.hbar / omega_l)

        # get coefficients
        coeff_0 = 4 * C**2
        coeff_1 = 8 * Delta_l * C
        coeff_2 = 4 * Delta_l**2 + gamma_o**2
        coeff_3 = - 4 * eta_l

        # get roots
        roots = np.roots([coeff_0, coeff_1, coeff_2, coeff_3])

        # retain real roots
        N_o = list()
        for root in roots:
            if np.imag(root) == 0.0:
                N_o.append(root)

        # return intracavity photon number
        return N_o