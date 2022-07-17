#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module to interface axes."""

__name__    = 'qom.ui.axes.BaseAxis'
__authors__ = ['Sampreet Kalita']
__created__ = '2020-10-10'
__updated__ = '2022-04-24'

# dependencies
from decimal import Decimal
import logging
import numpy as np

# module logger
logger = logging.getLogger(__name__)

# TODO: Randomize colors, styles and sizes.

class BaseAxis():
    """Class to interface axes.

    Initializes ``bound``, ``dim``, ``label``, ``label_pad``, ``limits``, ``scale``, ``tick_dim``, ``tick_labels``, ``tick_pad``, ``tick_position``, ``ticks``, ``ticks_minor`` and ``val``. Inherited objects need to set the other properties individually.

    Parameters
    ----------
    axis : str
        Name of the axis, "X", "Y", "Z" or "V".
    axis_params : dict or list
        Values for the axis supporting a list of values or a dictionary containing the range of values with keys "min", "max", "dim" and "scale" or the values themselves under key "val".
    plotter_params : dict
        Parameters for the plotter. Currently supported keys are:
            ==============  ====================================================
            key             value
            ==============  ====================================================
            "label"         (*str*) text of the axis label.
            "label_color"   (*str*) color of the axis label.
            "label_pad"     (*int*) padding of the axis label.
            "limits"        (*list*) minimum and maximum limits for the axis.
            "scale"         (*str*) step scale for the values. Options are "linear" and "log".
            "tick_dim"      (*float*) dimension of the ticks.
            "tick_labels"   (*list*) tick labels of the plots.
            "tick_pad"      (*int*) padding of the tick labels.
            "tick_position" (*str*) position of ticks on the plot. Options are "both", "bottom", "left", "right" or "top".
            "ticks"         (*list*) ticks of the plots.
            "ticks_minor"   (*list*) positions of minor ticks of the plots.
            ==============  ====================================================
    """

    # attributes
    axis_defaults = {
        'colors': list(),
        'label': '',
        'label_color': 'k',
        'label_pad': 4,
        'legend': list(),
        'limits': None, 
        'name': '',
        'scale': 'linear',
        'sizes': list(),
        'styles': list(),
        'tick_dim': 5,
        'tick_labels': None,
        'tick_pad': 8,
        'tick_position': 'both-in',
        'ticks': list(),
        'ticks_minor': None,
        'unit': ''
    }

    def __init__(self, axis, axis_params, plotter_params):
        """Class constructor for BaseAxis."""

        # extract frequently used variables
        _axis = axis_params.get(axis, None)

        # supersede axis parameters by plotter parameters
        params = dict()
        for key in self.axis_defaults:
            params[key] = plotter_params.get(axis.lower() + '_' + key, self.axis_defaults[key])

        # convert to list if numpy array
        if type(_axis) is np.ndarray:
            _axis = _axis.tolist()

        # handle list of values
        if type(_axis) is list:
            _axis = {
                'val': _axis
            }

        # if values available
        if _axis is not None:
            # if axis values are provided
            _val = _axis.get('val', None)
            # convert to list if numpy array
            if type(_val) is np.ndarray:
                _val = _val.tolist()
            # set values
            if type(_val) is list:
                # validate values
                assert len(_val) != 0, 'Key "{}" should contain key "val" with a non-empty list'.format(axis)

                self.val = _val
            else:
                # validate range
                assert 'min' in _axis and 'max' in _axis, 'Key "{}" should contain keys "min" and "max" to define axis range'.format(axis)

                self.val = self._init_array(np.float_(_axis['min']), np.float_(_axis['max']), int(_axis.get('dim', 101)), str(_axis.get('scale', 'linear')))

            # set range
            _min = 0 if type(self.val[0]) is str else np.min(self.val)
            _max = len(self.val) if type(self.val[0]) is str else np.max(self.val)
        # no values available
        else:
            self.val = self._init_array(0, params['tick_dim'], int(params['tick_dim']), params['scale'])

            # set range
            _min = self.val[0]
            _max = self.val[-1]

        # set dimension
        self.dim = len(self.val)

        # set label
        self.label = params['label']

        # set label
        self.label_color = params['label_color']

        # set label padding
        self.label_pad = int(params['label_pad'])

        # set scale
        self.scale = params['scale']

        # set tick dimension
        self.tick_dim = params['tick_dim']

        # set tick padding
        self.tick_pad = int(params['tick_pad'])

        # set tick padding
        self.tick_position = params['tick_position']

        # set ticks
        _ticks = params['ticks']
        # if ticks are defined
        if type(_ticks) is list and len(_ticks) != 0:
            self.ticks = _ticks
            self.tick_dim = len(_ticks)
            self.bound = True
            self.limits = params['limits'] if params['limits'] is not None else [np.min(_ticks), np.max(_ticks)]
        # else initialize ticks
        else:
            self.ticks = self._init_array(_min, _max, self.tick_dim, self.scale)
            self.bound = False

        # set minor ticks
        self.ticks_minor = params['ticks_minor']

        # set tick labels
        _tick_labels = params['tick_labels']
        # if ticks labels are defined
        if type(_tick_labels) is list and len(_tick_labels) != 0:
            self.tick_labels = _tick_labels
        # else same as ticks
        else:
            self.tick_labels = self.ticks 

        # supersede ticks by tick labels
        if len(self.tick_labels) != len(self.ticks):
            self.ticks = self._init_array(1, len(self.tick_labels), len(self.tick_labels), self.scale)

    def _init_array(self, mini, maxi, dim: int, scale: str):
        """Function to initialize an array given a range and number of elements.

        Parameters
        ----------
        mini : int
            Minimum value of the range.
        maxi : int 
            Maximum value of the range.
        dim : int
            Number of elements to consider.
        scale : str
            Step scale for the values. Options are "linear" and "log".

        Returns
        -------
        values : list
            Initialized array.
        """

        # set values
        if scale == 'log': 
            values = np.logspace(mini, maxi, dim)
        else:
            values = np.linspace(mini, maxi, dim)
            # truncate values
            _step_size = (Decimal(str(maxi)) - Decimal(str(mini))) / (dim - 1)
            _decimals = - _step_size.as_tuple().exponent
            values = np.around(values, _decimals)

        return values.tolist()