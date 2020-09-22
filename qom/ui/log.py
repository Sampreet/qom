#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""UI module to format logging."""

__name__    = 'qom.ui.log'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-02-05'
__updated__ = '2020-09-05'

# dependencies
import datetime as dt
import logging
    
# module logger    
logger = logging.getLogger(__name__)

def init_log(log_format='full', debug=False):
    """Function to initialize the logger for the package.
    
    Parameters
    ----------    
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
    main_logger = logging.getLogger('qom')
    main_logger.setLevel(logging.INFO)
    if debug:
        main_logger.setLevel(logging.DEBUG)
    logging.captureWarnings(True)

    # set stream handler
    formatter = get_formatter(log_format)
    handler = get_handler(formatter)
    main_logger.addHandler(handler)

    # test
    logger.debug('-------------------Logger Initialized-------------------\n')
    
def get_formatter(log_format='full'):
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
    if log_format == 'full':
        return FullFormatter('%(processName)-24s %(levelname)-7s %(asctime)s: (%(name)s) %(message)s\r'.format())

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

class FullFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = dt.datetime.fromtimestamp(record.created)
        t = ct.strftime("%Y-%m-%d %H:%M:%S")
        s = "%s.%03d" % (t, record.msecs)
        return s
