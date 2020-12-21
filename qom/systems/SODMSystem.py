#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a single-optical double-mechanical system.

References:

[1] M. Aspelmeyer, T. J. Kippenberg, and F. Marquardt, *Cavity Optomechanics*, Review of Modern Physics **86** (4), 1931 (2014).
"""

__name__    = 'qom.systems.SODMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2020-12-21'

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
    params : dict
        Parameters for the system.
    """

    def __init__(self, params):
        """Class constructor for SODMSystem."""

        # initialize super class
        super().__init__(params)

        # set attributes
        self.code = 'sodms'
        self.name = 'SODMSystem'