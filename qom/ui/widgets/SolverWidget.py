#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the solvers."""

__name__    = 'qom.ui.widgets.SolverWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-08-28'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import importlib
import inspect
import logging
import numpy as np
import os

# qom modules
from ...solvers import HLESolver
from . import BaseWidget, ParamWidget

# module logger
logger = logging.getLogger(__name__)

# TODO: Add solver selection criteria for systems.

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
        rows = 6

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
        # initialize progress check box
        self.chbx_progress = QtWidgets.QCheckBox('Progress')
        self.chbx_progress.setFixedSize(width / 4, row_height)
        self.chbx_progress.setDisabled(True)
        self.layout.addWidget(self.chbx_progress, 1, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot')
        self.chbx_plot.setFixedSize(width / 4, row_height)
        self.chbx_plot.setDisabled(True)
        self.layout.addWidget(self.chbx_plot, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize solve button
        self.btn_solve = QtWidgets.QPushButton('Solve')
        self.btn_solve.setFixedSize(width / 2 - 1.5 * padding, row_height)
        self.btn_solve.clicked.connect(self.solve)
        self.btn_solve.setDisabled(True)
        self.layout.addWidget(self.btn_solve, 2, 2, 1, 2, alignment=QtCore.Qt.AlignRight)
        # solver parameters
        self.te_params = QtWidgets.QTextEdit('')
        self.te_params.setFixedSize(width / 2 - 1.5 * padding, 3 * row_height)
        self.layout.addWidget(self.te_params, 3, 2, 3, 2, alignment=QtCore.Qt.AlignRight)
        self.te_params.setDisabled(True)

        # update main layout
        self.move(width, offset + 4)
        self.setFixedWidth(width)
        self.setFixedHeight(rows * row_height)
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
        
        # get progress check box
        params['show_progress'] = self.chbx_progress.isChecked()
        # get plot check box
        params['plot'] = self.chbx_plot.isChecked()
        # evaluate parameter widgets
        for widget in self.param_widgets:
            params[widget.key] = widget.val
        # evaulate parameter text edit
        te_params = eval(self.te_params.toPlainText()) if self.te_params.toPlainText() != '' else {}
        for key in te_params:
            params[key] = te_params[key]
        
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

        # if a system is selected
        if self.system_widget.system is not None and value != 'NA':
            # initialize system
            system = self.system_widget.system(params={}, cb_update=None)
            
            # initialize parameters
            params = dict()
            for key in system.required_params.get('get_' + value, []):
                # set ui defaults
                params[key] = system.ui_defaults[key]
            self.set_params(params)
        
            # if template directory exists
            if os.path.isdir('gui_templates'):
                # search for the first matching template with parameters
                for template_name in os.listdir('gui_templates'):
                    # if template found
                    if template_name.find(system.code + '_v=' + value) != -1:
                        # import template
                        template = importlib.import_module('gui_templates.' + template_name[:-3])
                        # if template contains parameters
                        if template.__dict__.get('params', None) is not None:
                            # extract parameters
                            params = template.__dict__['params']
                            # set solver parameters
                            self.set_params(params.get('solver', {}))
                            # set system parameters
                            self.system_widget.set_params(params.get('system', {}))
                            # set plotter parameters
                            if self.plotter_widget.plotter is not None:
                                self.plotter_widget.set_params(params.get('plotter', {}))
                            break

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
        padding = 32

        # update solver
        self.solver = self.solvers[pos]

        # initialize combo box
        cmbx_items = list()
        if self.system_widget.system is not None:
            # initialize system
            system = self.system_widget.system(params={}, cb_update=None)
            # search for available functions
            func_names = [func_name[4:] for func_name in dir(system) if callable(getattr(system, func_name)) and func_name[:4] == 'get_']
            # filter functions with solver parameters and plotter parameters
            required_args = ['solver_params', 'plot', 'plotter_params']
            for func_name in func_names:
                func = getattr(system, 'get_' + func_name)
                func_args = inspect.getfullargspec(func).args[1:]
                counter = sum([1 if arg in func_args else 0 for arg in required_args])
                # if one or all three required arguments are present
                if counter == 3 or func_args[:1] == required_args[:1]:
                    # if all functions required for the calculation are declared
                    if system.validate_required_funcs(func_name='get_' + func_name, mode='silent'):
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
            else: 
                widget.val = self.solver.ui_params[param]
            self.layout.addWidget(widget, 2 + int(widget_col / 2) * 2, int(widget_col % 2), 2, 1, alignment=QtCore.Qt.AlignRight)
            # update widget list
            self.param_widgets.append(widget)
            # update count
            widget_col += 1

        # update widget
        self.lbl_name.setText(str(self.solver.name))
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_items)
    
    def set_params(self, params):
        """Method to set the parameters for the solver.
        
        Parameters
        ----------
        params: dict
            Parameters for the solver.
        """

        # set progress check box
        self.chbx_progress.setChecked(params.get('show_progress', False))
        # set plot check box
        self.chbx_plot.setChecked(params.get('plot', True))
        # set parameter widgets
        used_keys = ['show_progress', 'plot']
        # set parameters
        for widget in self.param_widgets:
            if widget.key in params:
                widget.val = params[widget.key]
                used_keys.append(widget.key)
        # set parameter text edit
        te_params = dict()
        for key in params:
            if key not in used_keys:
                te_params[key] = params[key]
        self.te_params.setText(str(te_params) if len(te_params) > 1 else '')

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

            # initialize system
            system = self.system_widget.system(params=self.system_widget.get_params(), cb_update=self.parent.update)
            # get selected function
            func_name = self.cmbx_func.currentText()
            solver_params = self.get_params()
            # options
            plot = self.chbx_plot.isChecked()
            # get plotter parameters
            plotter_params = self.plotter_widget.get_params() if plot else dict()
            # get results
            if self.plotter_widget.plotter is not None and 'plot' in inspect.getfullargspec(getattr(system, 'get_' + func_name)).args[1:]:
                getattr(system, 'get_' + func_name)(solver_params=solver_params, plot=plot, plotter_params=plotter_params)
            else:
                getattr(system, 'get_' + func_name)(solver_params=solver_params)
            
            # update footer
            self.parent.update(status='Results Obtained', progress=None, reset=True)

            # enable calculate button
            self.btn_solve.setDisabled(False)