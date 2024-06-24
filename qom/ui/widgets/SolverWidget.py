#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the solvers."""

__name__    = 'qom.ui.widgets.SolverWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2024-06-23'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import inspect
import logging
import re

# qom modules
from ...solvers.deterministic import HLESolver, SSHLESolver, LLESolver, NLSESolver
from ...solvers.measure import QCMSolver
from ...solvers.stability import RHCSolver
from .BaseWidget import BaseWidget

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
        self.SolverClass = None
        self.SolverClasses = [HLESolver, SSHLESolver, LLESolver, NLSESolver, QCMSolver, RHCSolver]
        self.system_widget = system_widget
        self.plotter_widget = plotter_widget
        self.widget_params = dict()

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

        # initialize solver label
        self.lbl_name = QtWidgets.QLabel('Select Solver')
        self.lbl_name.setFixedSize(int(width * 3 / 4), row_height) 
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.lbl_name, 0, 0, 1, 3, alignment=QtCore.Qt.AlignLeft)
        # initialize function combo box
        self.cmbx_func = QtWidgets.QComboBox()
        self.cmbx_func.setFixedSize(int(width / 2 - 1.5 * padding), row_height)
        self.cmbx_func.currentTextChanged.connect(self.set_curr_func)
        self.cmbx_func.setDisabled(True)
        self.layout.addWidget(self.cmbx_func, 1, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize progress check box
        self.chbx_progress = QtWidgets.QCheckBox('Progress')
        self.chbx_progress.setFixedSize(int(width / 4), row_height)
        self.chbx_progress.setDisabled(True)
        self.layout.addWidget(self.chbx_progress, 1, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot')
        self.chbx_plot.setFixedSize(int(width / 4), row_height)
        self.chbx_plot.setDisabled(True)
        self.layout.addWidget(self.chbx_plot, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize key label
        self.lbl_key = QtWidgets.QLabel('key')
        self.lbl_key.setFixedSize(int(width / 4), row_height)
        self.lbl_key.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_key, 2, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize value label
        self.lbl_key = QtWidgets.QLabel('value')
        self.lbl_key.setFixedSize(int(width / 4), row_height)
        self.lbl_key.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_key, 2, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize solve button
        self.btn_solve = QtWidgets.QPushButton('Solve')
        self.btn_solve.setFixedSize(int(width / 2 - 1.5 * padding), row_height)
        self.btn_solve.clicked.connect(self.solve)
        self.btn_solve.setDisabled(True)
        self.layout.addWidget(self.btn_solve, 2, 2, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize type combo box
        self.cmbx_key = QtWidgets.QComboBox()
        self.cmbx_key.setFixedSize(int(width / 4 - 1.25 * padding), row_height)
        self.cmbx_key.currentTextChanged.connect(self.set_value)
        self.cmbx_key.setDisabled(True)
        self.layout.addWidget(self.cmbx_key, 3, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        # plotter parameters
        self.le_value = QtWidgets.QLineEdit('')
        self.le_value.setFixedSize(int(width / 4 - 1.25 * padding), row_height)
        self.le_value.textChanged.connect(self.update_value)
        self.le_value.setDisabled(True)
        self.layout.addWidget(self.le_value, 3, 1, 1, 1, alignment=QtCore.Qt.AlignRight)
        # solver parameters
        self.te_params = QtWidgets.QTextEdit('')
        self.te_params.setFixedSize(int(width / 2 - 1.5 * padding), 3 * row_height)
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
        for SolverClass in self.SolverClasses:
            codes.append(SolverClass.name)

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
        # combo box params
        for key in self.widget_params:
            params[key] = self.widget_params[key]
        # evaulate parameter text edit
        te_params = eval(self.te_params.toPlainText()) if self.te_params.toPlainText() != '' else {}
        for key in te_params:
            params[key] = te_params[key]
        
        return params

    def set_curr_func(self, value):
        """Method to update widgets when combo box selection changes.
        
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
        self.chbx_plot.setDisabled(True) # not supported

        # frequently used parameters=
        cmbx_items = list()

        # update solver
        self.SolverClass = self.SolverClasses[pos]

        # set parameters
        self.set_params(self.SolverClass.solver_defaults)

        # initialize combo box
        if self.system_widget.SystemClass is not None:
            # initialize system
            system = self.system_widget.SystemClass(params=self.system_widget.get_params(), cb_update=None)
            # initialize solver
            solver = self.SolverClass(system=system, params=self.get_params(), cb_update=None)
            # search for available functions
            func_names = [func_name[4:] for func_name in dir(solver) if callable(getattr(solver, func_name)) and func_name[:4] == 'get_']
            # filter functions with solver parameters and plotter parameters
            for func_name in func_names:
                func = getattr(solver, 'get_' + func_name)
                func_args = inspect.getfullargspec(func).args[1:]
                # if one or all three required arguments are present
                if len(func_args) == 0:
                    cmbx_items.append(func_name)
        # if no functions found
        if len(cmbx_items) == 0:
            cmbx_items.append('NA')

        # update widget
        self.lbl_name.setText(str(self.SolverClass.desc))
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
        self.chbx_plot.setChecked(params.get('plot', False))
        # set parameter widgets
        used_keys = ['show_progress', 'plot']
        # set widget params
        keys = list()
        self.cmbx_key.clear()
        self.widget_params = dict()
        for key in self.SolverClass.required_params:
            if key not in used_keys:
                used_keys.append(key)
                self.widget_params[key] = params[key]
                keys.append(key)
        self.cmbx_key.addItems(keys)
        # set parameter text edit
        te_params = dict()
        for key in params:
            if key not in used_keys:
                te_params[key] = params[key]
        self.te_params.setText(str(te_params) if len(te_params) > 1 else '')

    def set_value(self, key):
        self.le_value.setText(str(self.widget_params[key]) if key != '' else '')

    def update_value(self):
        val = self.le_value.text()
        self.widget_params[self.cmbx_key.currentText()] = eval(val) if re.match('\-*\d+\.*e*\-*\d*', val) is not None else val

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
            system = self.system_widget.SystemClass(params=self.system_widget.get_params(), cb_update=None)
            # initialize solver
            solver = self.SolverClass(system=system, params=self.get_params(), cb_update=None)
            # get selected function
            func_name = self.cmbx_func.currentText()
            
            # plot results
            results = getattr(solver, 'get_' + func_name)()
                
            # update footer
            self.parent.update(status='Results Obtained{}'.format(': ' + str(results) if type(results) is not tuple else ''), progress=None, reset=True)

            # enable calculate button
            self.btn_solve.setDisabled(False)