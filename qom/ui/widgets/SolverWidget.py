#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the solvers."""

__name__    = 'qom.ui.widgets.SolverWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-08-20'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import importlib
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class SolverWidget(BaseWidget):
    """Class to create a widget for the solvers.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the widget.
    """

    def __init__(self, parent):
        """Class constructor for SolverWidget."""

        # initialize super class
        super().__init__(parent)
        self.solver = None

        # initialize layout
        self.__init_layout()

        # set solvers
        self.solvers = list()
        # import all looper modules
        module_names = importlib.import_module('qom.solvers', '*')
        # add available system classes
        for module_name in module_names.__dict__:
            if module_name[0] != '_':
                self.solvers.append(getattr(module_names, module_name))

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        row_height = 32
        padding = 32

        # fix size
        self.setFixedWidth(width)
        # move under header
        self.move(640, padding + 4)

        # initialize UI elements
        # solver label
        self.lbl_name = QtWidgets.QLabel('Select a solver to begin')
        self.lbl_name.setFixedSize(width, row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        # solver parameters
        self.te_params = QtWidgets.QTextEdit('')
        self.te_params.setFixedSize(width - 2 * padding, row_height * 5)
        self.te_params.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))

        # update layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.lbl_name, 0, 0)
        self.layout.addWidget(self.te_params, 1, 0, alignment=QtCore.Qt.AlignRight)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, padding, 0)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def get_list_items(self):
        """Method to obtain the codes of available solvers.
        
        Returns
        -------
        codes : list
            Codenames of the solvers.
        """

        # initialize lists
        codes = list()

        # iterate through available solvers
        for solver in self.solvers:
            codes.append(solver.code)

        return codes
    
    def get_params(self):
        # get parameters
        params = eval(self.te_params.toPlainText()) if self.te_params.toPlainText() != '' else {}
        
        return params

    def set_curr_item(self, pos):
        """Method to set the current solver.
        
        Parameters
        ----------
        pos : int
            Position of the current solver.
        """

        # update parameter
        self.pos = pos
        self.solver = self.solvers[pos]

        # update UI elements
        self.lbl_name.setText('Solver Parameters:')
    
    def set_params(self, params):
        # set parameters
        self.te_params.setText(str(params))

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
            self.setStyleSheet(self.get_stylesheet('widget_light'))
        else:
            # styles
            self.setStyleSheet(self.get_stylesheet('widget_dark'))