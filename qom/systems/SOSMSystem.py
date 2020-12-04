#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface a single-optical single-mechanical system."""

__name__    = 'qom.systems.SOSMSystem'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-12-04'
__updated__ = '2020-12-04'

# dependencies
import logging

# dev dependencies
from qom.systems.BaseSystem import BaseSystem

# module logger
logger = logging.getLogger(__name__)

class SOSMSystem(BaseSystem):
    """Class to interface a single-optical single-mechanical system.
    
    Inherits :class:`qom.systems.BaseSystem`.
        
    Parameters
    ----------
    data : dict
        Data for the system.
    """

    def __init__(self, data):
        """Class constructor for SOSMSystem."""

        # initialize super class
        super().__init__(data)

        # initialize properties
        self.name = data.get('name', 'SOSMSystem')
        self.code = data.get('code', 'sosms')
        self.params = data.get('params', {})