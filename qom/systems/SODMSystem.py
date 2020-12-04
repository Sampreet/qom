#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a single-optical double-mechanical system.

References:

[1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86** (4), 1931 (2014).
"""

__name__    = 'qom.systems.SODMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2020-12-04'

# dependencies
import logging

# dev dependencies
from qom.systems.BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class SODMSystem(BaseSystem):
    """Class to interface a single-optical double-mechanical system.
    
    Inherits :class:`qom.systems.BaseSystem`.
        
    Parameters
    ----------
    data : dict
        Data for the system.
    """

    def __init__(self, data):
        """Class constructor for SODMSystem."""

        # initialize super class
        super().__init__(data)

        # initialize properties
        self.name = data.get('name', 'SODMSystem')
        self.code = data.get('code', 'sodms')
        self.params = data.get('params', {})

    def get_intracavity_photon_number(self, lambda_l, mu, gamma_o, P_l, Delta, C=0, mode='basic'):
        r"""Method to obtain the intracavity photon number.

        The steady states are assumed to be of the form [1],

        .. math::
        
            \alpha_{s} = \frac{\eta_{l}}{\frac{\gamma_{o}}{2} - \iota \Delta}

        where :math:`\Delta = \Delta_{l} + C |\alpha_{s}|^{2}`, :math:`\eta_{l} = \sqrt{\mu \gamma_{o} P_{l} / (\hbar \omega_{l})}`, with :math:`\omega_{l} = 2 \pi c / \lambda_{l}`.

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
            Effective detuning if mode is 'basic', else detuning of the laser.
        G : float
            Frequency pull parameter.
        C : float
            Coefficient of :math:`|\alpha_{s}|^{2}`.
        mode : str
            Mode of calculation of intracavity photon number:
                * 'basic' : Assuming constant effective detuning.
                * 'cubic' : Cubic variation with laser detuning.
        
        Returns
        -------
        N_o : float
            Intracavity photon number.
        """

        # if basic, return base function
        if mode == 'basic': 
            return super().get_intracavity_photon_number_basic(lambda_l, mu, gamma_o, P_l, Delta)

        # if cubic
        elif mode == 'cubic':
            return super().get_intracavity_photon_number_cubic(lambda_l, mu, gamma_o, P_l, Delta, C)


    