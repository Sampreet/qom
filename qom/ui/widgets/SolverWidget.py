#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the solvers."""

__name__    = 'qom.ui.widgets.SolverWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-08-26'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import inspect
import logging
import numpy as np
import re

# qom modules
from ...solvers import HLESolver
from . import BaseWidget, ParamWidget

# module logger
logger = logging.getLogger(__name__)

class SolverWidget(BaseWidget):
    """Class to create a widget for the solvers.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the widget.
    system_widget : :class:`qom.ui.widgets.SystemWidget`
        System widget.
    plotter_widget : :class:`qom.ui.widgets.PlotterWidget`
        Plotter widget.
    """

    def __init__(self, parent, system_widget, plotter_widget):
        """Class constructor for SolverWidget."""

        # initialize super class
        super().__init__(parent)

        # set attributes
        self.solvers = [HLESolver]
        self.system_widget = system_widget
        self.plotter_widget = plotter_widget
        self.param_widgets = list()
        self.solver = None

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        offset = 32
        row_height = 32
        padding = 32
        base_rows = 2

        # initialize grid layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, padding, 0)

        # initialize function label
        self.lbl_func = QtWidgets.QLabel('Function:')
        self.lbl_func.setFixedSize(width / 4, row_height) 
        self.lbl_func.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.layout.addWidget(self.lbl_func, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize solver name
        self.lbl_name = QtWidgets.QLabel('Select a solver to begin')
        self.lbl_name.setFixedSize(width * 3 / 4 + 0.25 * padding, row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.lbl_name, 0, 1, 1, 3, alignment=QtCore.Qt.AlignRight)
        # initialize function combo box
        self.cmbx_func = QtWidgets.QComboBox()
        self.cmbx_func.setFixedSize(width / 2 - 1.5 * padding, row_height)
        self.cmbx_func.currentTextChanged.connect(self.set_curr_func)
        self.cmbx_func.setDisabled(True)
        self.layout.addWidget(self.cmbx_func, 1, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot')
        self.chbx_plot.setFixedSize(width / 4, row_height)
        self.chbx_plot.setDisabled(True)
        self.layout.addWidget(self.chbx_plot, 1, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize solve button
        self.btn_solve = QtWidgets.QPushButton('Solve')
        self.btn_solve.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.btn_solve.clicked.connect(self.solve)
        self.btn_solve.setDisabled(True)
        self.layout.addWidget(self.btn_solve, 1, 3, 1, 1, alignment=QtCore.Qt.AlignRight)

        # update main layout
        self.move(width, offset + 4)
        self.setFixedWidth(width)
        self.setFixedHeight(base_rows * row_height)
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
        """Method to obtain the parameters for the solver.
        
        Returns
        -------
        params: dict
            Parameters for the solver.
        """

        # initialize dict
        params = dict()
        # evaluate parameters
        for widget in self.param_widgets:
            key = widget.key
            val = widget.val
            params[key] = eval(val) if re.match('\-*\d+\.*e*\-*\d*', val) is not None else val
        
        return params

    def set_curr_func(self, value):
        """Method to update the widget when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # enable solve button
        self.btn_solve.setEnabled(True)

        # update footer
        self.parent.update(status='Ready', progress=None, reset=True)

    def set_curr_item(self, pos):
        """Method to set the current solver.
        
        Parameters
        ----------
        pos : int
            Position of the current solver.
        """

        # enable all widgets
        for idx in range(self.layout.count()):
            self.layout.itemAt(idx).widget().setEnabled(True)

        # frequently used parameters
        width = 640
        row_height = 32
        padding = 32
        base_rows = 2

        # update solver
        self.solver = self.solvers[pos]

        # initialize combo box
        cmbx_items = list()
        if self.system_widget is not None:
            # search for available functions
            func_names = [func_name[4:] for func_name in dir(self.system_widget.system) if callable(getattr(self.system_widget.system, func_name)) and func_name[:4] == 'get_']
            # filter functions with solver parameters and plotter parameters
            required_args = ['solver_params', 'plot', 'plotter_params']
            for func_name in func_names:
                func = getattr(self.system_widget.system, 'get_' + func_name)
                func_args = inspect.getfullargspec(func).args[1:]
                if func_args == required_args or func_args == required_args[:1]:
                    cmbx_items.append(func_name)
        # if no functions found
        if len(cmbx_items) == 0:
            cmbx_items.append('NA')

        # clear widgets
        for widget in self.param_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
            
        # reset list
        self.param_widgets = list()

        # update parameter widgets
        widget_col = 0
        for param in self.solver.ui_params:
            # new widget
            val = self.solver.ui_params[param]
            widget = ParamWidget(parent=self, width=(width - padding) / 4, val_type=type(val))
            widget.key = param
            if type(val) is list:
                widget.w_val.addItems(self.solver.ui_params[param])
                widget.val = self.solver.ui_params[param][0]
                if param in self.solver.ui_defaults:
                    widget.val = self.solver.ui_defaults[param]
            else: 
                widget.val = self.solver.ui_params[param]
            self.layout.addWidget(widget, int(widget_col / 4) * 2 + base_rows, int(widget_col % 4), 1, 1, alignment=QtCore.Qt.AlignRight)
            # update widget list
            self.param_widgets.append(widget)
            # update count
            widget_col += 1

        # update widget
        self.lbl_name.setText('(' + str(self.solver.name) + ')')
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_items)

        # update main looper
        self.setFixedHeight((base_rows + int(widget_col / 4) * 2) * row_height)
    
    def set_params(self, params):
        """Method to set the parameters for the solver.
        
        Parameters
        ----------
        params: dict
            Parameters for the solver.
        """

        # set parameters
        for widget in self.param_widgets:
            if widget.key in params:
                widget.val = params[widget.key]

    def set_theme(self, theme=None):
        """Method to update the theme.
        
        Parameters
        ----------
        theme : str, optional
            Display theme. Available options are:
                ==========  ==============
                value       meaning
                ==========  ==============  
                "dark"      dark mode.
                "light"     light mode.
                ==========  ==============
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

    def solve(self):
        """Method to solve using the selected function."""

        # disable calculate button
        self.btn_solve.setDisabled(True)

        # handle no function found
        if self.cmbx_func.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return

        else:
            # update status
            self.parent.update(status='Solving...')

            # system_parameters
            system_params = self.system_widget.get_params()
            # get selected function
            func_name = self.cmbx_func.currentText()
            solver_params = self.get_params()
            # options
            solver_params['cache'] = True
            solver_params['show_progress'] = True
            plot = self.chbx_plot.isChecked()
            # plotter parameters
            plotter_params = self.plotter_widget.get_params() if plot else dict()
            # get results
            getattr(self.system_widget.system(params=system_params, cb_update=self.parent.update), 'get_' + func_name)(solver_params=solver_params, plot=plot, plotter_params=plotter_params)
            
            # update footer
            self.parent.update(status='Results Obtained', progress=None, reset=True)

            # enable calculate button
            self.btn_solve.setDisabled(False)