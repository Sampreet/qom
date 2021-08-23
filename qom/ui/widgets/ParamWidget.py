#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for each parameter."""

__name__    = 'qom.ui.widgets.ParamWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-08-23'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle exceptions.

class ParamWidget(BaseWidget):
    """Class to create a widget for each parameter.
    
    Parameters
    ----------
    parent : :class:`qom.ui.widgets.*`
        Parent class for the widget.
    wide : bool, optional
        Option for a wide value-placeholder.
    """

    @property
    def key(self):
        """str: Name of the key."""

        return self.lbl_key.text()

    @key.setter
    def key(self, key):
        self.lbl_key.setText(str(key))

    @property
    def val(self):
        """str or list: Text or option for value."""

        return self.le_val.text()

    @val.setter
    def val(self, val):
        self.le_val.setText(str(val))

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
        width = 160
        row_height = 32
        padding = 32

        # fix size
        self.setFixedSize(width, 2 * row_height)

        # initialize UI elements
        # key label
        self.lbl_key = QtWidgets.QLabel()
        self.lbl_key.setFixedSize(width, row_height)
        self.lbl_key.setFont(QtGui.QFont('Segoe UI', pointSize=9, italic=False))
        # value
        self.le_val = QtWidgets.QLineEdit()
        self.le_val.setFixedSize(width - padding, row_height)
        self.le_val.setFont(QtGui.QFont('Segoe UI', pointSize=9, italic=False))

        # update layout 
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.lbl_key, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(self.le_val, 1, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)