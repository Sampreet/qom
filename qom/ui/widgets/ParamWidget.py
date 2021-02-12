#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for each parameter."""

__name__    = 'qom.ui.widgets.ParamWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-01-23'

# dependencies
from PyQt5 import QtWidgets
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle exceptions.

class ParamWidget(BaseWidget):
    """Class to create a widget for each parameter.

    Inherits :class:`qom.ui.widgets.BaseWidget`.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the widget.
    wide : bool, optional
        Option for a wide value-placeholder.
    """

    def __init__(self, parent, wide=False):
        """Class constructor for ParamWidget."""

        # initialize super class
        super().__init__(parent)

        # set parameters
        self.wide = wide

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640 if self.wide else 320
        key_width = 300 if self.wide else 180

        # fix size
        self.setFixedSize(width, 32)

        # initialize UI elements
        # key
        self.key = QtWidgets.QLabel()
        self.key.setFixedSize(key_width, 32)
        # value
        self.val = QtWidgets.QLineEdit()
        self.val.setFixedSize(width - key_width, 32)

        # update layout 
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.key)
        layout.addWidget(self.val)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def get_key(self):
        """Method to get the name of the key.
        
        Returns
        -------
        key : str
            Name of the key.
        """

        return self.key.text()

    def get_val(self):
        """Method to get text or options for the value.
        
        Returns
        -------
        val : str or list
            Text or options to set.
        """

        return self.val.text()

    def set_key(self, key):
        """Method to set the name of the key.
        
        Parameters
        ----------
        key : str
            Name of the key.
        """

        self.key.setText(str(key))

    def set_theme(self, theme=None):
        """Method to update the theme.
        
        Parameters
        ----------
        theme : str, optional
            Display theme:
                'dark': Dark mode.
                'light': Light mode.
        """

        # update theme
        if theme is not None:
            self.theme = theme

        if self.theme == 'light':
            # styles
            self.setStyleSheet(self.get_stylesheet('param_light'))
        else:
            # styles
            self.setStyleSheet(self.get_stylesheet('param_dark'))

    def set_val(self, val):
        """Method to set text or options for the value.
        
        Parameters
        ----------
        val : str or list
            Text or options to set.
        """

        self.val.setText(str(val))