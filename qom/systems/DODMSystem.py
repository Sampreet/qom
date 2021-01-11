#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a double-optical double-mechanical system."""

__name__    = 'qom.systems.DODMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2021-01-11'

# dependencies
import logging

# qom modules
from .BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class DODMSystem(BaseSystem):
    """Class to interface a double-optical double-mechanical system.
    
    Inherits :class:`qom.systems.BaseSystem`.
        
    Parameters
    ----------
    params : dict
        Parameters for the system.
    """

    def __init__(self, params):
        """Class constructor for DODMSystem."""

        # initialize super class
        super().__init__(params)

        # set attributes
        self.code = 'dodms'
        self.name = 'DODMSystem'
        self.num_modes = 4