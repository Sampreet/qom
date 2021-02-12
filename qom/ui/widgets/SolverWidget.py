#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the solvers."""

__name__    = 'qom.ui.widgets.SolverWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-01-23'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import importlib
import json
import logging
import os

# qom modules
from .BaseWidget import BaseWidget
from .ParamWidget import ParamWidget

# module logger
logger = logging.getLogger(__name__)

class SolverWidget(BaseWidget):
    """Class to create a widget for the solvers.

    Inherits :class:`qom.ui.widgets.BaseWidget`.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the widget.
    """

    def __init__(self, parent):
        """Class constructor for SolverWidget."""

        # initialize super class
        super().__init__(parent)
        self.curr_solver = None
        self.solver_params = None
        self.param_widgets = list()

        # initialize layout
        self.__init_layout()

        # set solvers
        self.__set_solvers()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        label_height = 48
        padding = 32

        # fix size
        self.setFixedWidth(width)
        # move under header
        self.move(640, padding)

        # initialize UI elements
        # name
        self.lbl_name = QtWidgets.QLabel()
        self.lbl_name.setFixedSize(width, 64)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=16, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # parameter label
        self.lbl_params = QtWidgets.QLabel('Solver Parameters')
        self.lbl_params.setFixedSize(width, label_height)
        self.lbl_params.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_params.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_params.setVisible(False)

        # update layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.lbl_name, 0, 0)
        self.layout.addWidget(self.lbl_params, 5, 0)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def __set_solvers(self):
        """Method to obtain the available solvers."""

        # initialize list
        solvers = list()
            
        self.solvers = solvers

    def get_list_items(self):
        """Method to obtain the names of available solvers.
        
        Returns
        -------
        names : list
            Names of the solvers.
        """

        # initialize lists
        names = list()

        # iterate through available solvers
        for solver in self.solvers:
            names.append(solver({}).name)

        return names

    def set_curr_item(self, pos):
        """Method to set the current solver.
        
        Parameters
        ----------
        pos : int
            Position of the current solver.
        """

        # update parameter
        self.pos = pos
        self.curr_solver = self.solvers[pos]

        # solver name
        self.lbl_name.setText(self.curr_solver({}).name)

        # update UI elements
        self.lbl_params.setVisible(True)

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
            self.setStyleSheet(self.get_stylesheet('system_light'))
        else:
            # styles
            self.setStyleSheet(self.get_stylesheet('system_dark'))

        for widget in self.param_widgets:
            widget.set_theme(self.theme)