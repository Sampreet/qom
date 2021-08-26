#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for each parameter."""

__name__    = 'qom.ui.widgets.ParamWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-08-26'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

# qom modules
from . import BaseWidget

# module logger
logger = logging.getLogger(__name__)

# TODO: Handle exceptions.

class ParamWidget(BaseWidget):
    """Class to create a widget for each parameter.
    
    Parameters
    ----------
    parent : :class:`qom.ui.widgets.*`
        Parent class for the widget.
    width : int, optional
        Width of the widget.
    val_type : :class:`list` or :class:`str`, optional
        Type of the value for the widget.
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

        return self.w_val.currentText() if type(self.w_val) is QtWidgets.QComboBox else self.w_val.text()

    @val.setter
    def val(self, val):
        if type(self.w_val) is QtWidgets.QComboBox:
            self.w_val.setCurrentText(val)
        else:
            self.w_val.setText(str(val))

    def __init__(self, parent, width=160, val_type=str):
        """Class constructor for ParamWidget."""

        # initialize super class
        super().__init__(parent)

        # initialize layout
        self.__init_layout(width, val_type)

    def __init_layout(self, width, val_type):
        """Method to initialize layout.
        
        Parameters
        ----------
        width : int
            Width of the widget.
        val_type : :class:`list` or :class:`str`
            Type of the value for the widget.
        """
        
        # frequently used variables
        row_height = 32
        padding = 32

        # initialize grid layout 
        layout = QtWidgets.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # initialize key label
        self.lbl_key = QtWidgets.QLabel('')
        self.lbl_key.setFixedSize(width, row_height)
        self.lbl_key.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        layout.addWidget(self.lbl_key, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize value widget
        self.w_val = QtWidgets.QComboBox() if val_type is list else QtWidgets.QLineEdit()
        self.w_val.setFixedSize(width - padding, row_height)
        layout.addWidget(self.w_val, 1, 0, 1, 1, alignment=QtCore.Qt.AlignRight)

        # update main layout
        self.setFixedSize(width, 2 * row_height)
        self.setLayout(layout)