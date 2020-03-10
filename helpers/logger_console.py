#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Modules to output log to console."""

__authors__ = ['Sampreet Kalita']
__created__ = '2020-02-05'
__updated__ = '2020-02-26'

# dependencies
import logging

def get_logger(module_name, log_format='short', debug=False):
    """Function to obtain the logger for output to console.
    
    Parameters
    ----------
    module_name : str
        Name of the module calling the logger.
    
    log_format : str
        Format type for output to console.

    debug : boolean
        Option to enable DEBUG log level.
        
    Returns
    -------
    logger : :class:`logging.Logger`
        Logger for output to console.
    """

    # get logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
    logging.captureWarnings(True)

    # if logger for module exists
    if len(logger.handlers) != 0:
        return logger

    # set stream handler
    formatter = get_formatter(log_format)
    handler = get_handler(formatter)
    logger.addHandler(handler)

    return logger
    
def get_formatter(log_format='short'):
    """Function to obtain the formatter for stream handler.
    
    Parameters
    ----------    
    log_format : str
        Format type for output to console.

    Returns
    -------
    formatter : :class:`logging.Formatter`
        Formatter for stream handler.
    """

    # default format
    if log_format == 'default':
        return logging.Formatter('\r%(asctime)s %(levelname)s: (%(name)s) %(message)s')

    # short format
    if log_format == 'short':
        return logging.Formatter('\r(%(levelname)s) %(name)s: %(message)s')
        
def get_handler(formatter):
    """Function to obtain the stream handler for console logger.
    
    Parameters
    ----------    
    formatter : :class:`logging.Formatter`
        Formatter for stream handler.

    Returns
    -------
    handler : :class:`logging.StreamHandler`
        Stream handler for console logger.
    """
    
    # get stream handler
    handler = logging.StreamHandler()

    # set formatter
    handler.setFormatter(formatter)
    handler.terminator = ''

    return handler

