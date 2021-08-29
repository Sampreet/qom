#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the loopers."""

__name__    = 'qom.ui.widgets.LooperWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-19'
__updated__ = '2021-08-28'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import importlib
import logging
import numpy as np
import os

# qom modules
from ...loopers import XLooper, XYLooper, XYZLooper
from ...utils import default_looper_func_names, get_looper_func
from . import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class LooperWidget(BaseWidget):
    """Class to create a widget for the loopers.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the widget.
    solver_widget : :class:`qom.ui.widgets.SolverWidget`
        Solver widget.
    system_widget : :class:`qom.ui.widgets.SystemWidget`
        System widget.
    plotter_widget : :class:`qom.ui.widgets.PlotterWidget`
        Plotter widget.
    """

    def __init__(self, parent, solver_widget, system_widget, plotter_widget):
        """Class constructor for LooperWidget."""

        # initialize super class
        super().__init__(parent)

        # set attributes
        self.loopers = [XLooper, XYLooper, XYZLooper]
        self.solver_widget = solver_widget
        self.system_widget = system_widget
        self.plotter_widget = plotter_widget
        self.param_widgets = list()
        self.looper = None

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize main layout."""
        
        # frequently used variables
        width = 640
        offset = 240
        row_height = 32
        padding = 32
        base_rows = 4
        axes_rows = 3

        # initialize grid layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, padding, 0)

        # initialize function label
        self.lbl_func = QtWidgets.QLabel('Function:')
        self.lbl_func.setFixedSize(width / 4, row_height) 
        self.lbl_func.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.layout.addWidget(self.lbl_func, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize looper name
        self.lbl_name = QtWidgets.QLabel('Select a looper to begin')
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
        # initialize wrap check box
        self.chbx_wrap = QtWidgets.QCheckBox('Wrap')
        self.chbx_wrap.setFixedSize(width / 4, row_height)
        self.chbx_wrap.stateChanged.connect(self.toggle_wrap)
        self.chbx_wrap.setDisabled(True)
        self.layout.addWidget(self.chbx_wrap, 1, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot')
        self.chbx_plot.setFixedSize(width / 4, row_height)
        self.chbx_plot.setDisabled(True)
        self.layout.addWidget(self.chbx_plot, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize cache path line edit
        self.le_path = QtWidgets.QLineEdit('')
        self.le_path.setFixedSize(width / 2 - 1.5 * padding, row_height)
        self.le_path.setDisabled(True)
        self.layout.addWidget(self.le_path, 2, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize mode combo box
        self.cmbx_mode = QtWidgets.QComboBox()
        self.cmbx_mode.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.cmbx_mode.addItems(['serial', 'multithread'])
        self.cmbx_mode.setDisabled(True)
        self.layout.addWidget(self.cmbx_mode, 2, 2, 1, 1, alignment=QtCore.Qt.AlignRight)
        # initialize loop button
        self.btn_loop = QtWidgets.QPushButton('Loop')
        self.btn_loop.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.btn_loop.clicked.connect(self.loop)
        self.btn_loop.setDisabled(True)
        self.layout.addWidget(self.btn_loop, 2, 3, 1, 1, alignment=QtCore.Qt.AlignRight)
        # initialize variable label
        self.lbl_var = QtWidgets.QLabel('var')
        self.lbl_var.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_var.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_var, 3, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize minimum value label
        self.lbl_min = QtWidgets.QLabel('min')
        self.lbl_min.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_min.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_min, 3, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize maximum value label
        self.lbl_max = QtWidgets.QLabel('max')
        self.lbl_max.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_max.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_max, 3, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize dimension label
        self.lbl_dim = QtWidgets.QLabel('dim')
        self.lbl_dim.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_dim.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_dim, 3, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)

        # initialize most useful parameters
        axes_prefix = ['x_', 'y_', 'z_']
        keys = ['var', 'min', 'max', 'dim']
        for row in range(axes_rows):
            for col in range(4):
                # initialize each widget
                widget = QtWidgets.QLineEdit('')
                widget.setPlaceholderText(str(axes_prefix[row]) + str(keys[col]))
                widget.setFixedSize(width / 4 - 1.25 * padding, row_height)
                widget.setDisabled(True)
                # update widget list
                self.param_widgets.append(widget)
                self.layout.addWidget(widget, base_rows + row, col, 1, 1, alignment=QtCore.Qt.AlignRight)

        # update main layout
        self.move(width, offset + 4)
        self.setFixedWidth(width)
        self.setFixedHeight((base_rows + axes_rows) * row_height)
        self.setLayout(self.layout)
        
        # set theme
        self.theme = 'dark'
        self.set_theme()

    def get_list_items(self):
        """Method to obtain the names of available loopers.
        
        Returns
        -------
        codes : list
            Codenames of the loopers.
        """

        # initialize lists
        codes = list()

        # iterate through available loopers
        for looper in self.loopers:
            codes.append(looper.code)

        return codes

    def loop(self):
        """Method to loop the variables."""

        # disable loop button
        self.btn_loop.setDisabled(True)

        # handle no function found
        if self.cmbx_func.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return
        # extract axes parameters from widgets
        looper_params = dict()
        axes = ['X', 'Y', 'Z']
        keys = ['var', 'min', 'max', 'dim']
        for i in range(self.loopers.index(self.looper) + 1):
            looper_params[axes[i]] = {}
            for j in range(4):
                looper_params[axes[i]][keys[j]] = self.param_widgets[i * 4 + j].text()

        # get file path to save/load data
        path_text = self.le_path.text()
        file_path = path_text if path_text != '' else None

        # get all parameters
        params = {
            'looper': looper_params,
            'solver': self.solver_widget.get_params(),
            'system': self.system_widget.get_params(),
            'plotter': self.plotter_widget.get_params()
        }
        
        # get function
        func = get_looper_func(SystemClass=self.system_widget.system, solver_params=params['solver'], func_code=self.cmbx_func.currentText())

        # initialize looper
        looper = self.looper(func=func, params=params, cb_update=self.parent.update)

        # run looper on main thread
        looper.wrap(file_path=file_path, plot=self.chbx_plot.isChecked())

        # enable loop button
        self.btn_loop.setEnabled(True)

    def set_curr_func(self, value):
        """Method to update the widget when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # frequently used variables
        axes = ['X', 'Y', 'Z']
        keys = ['var', 'min', 'max', 'dim']
        expr = ['v=' + value + '.py', 'x=', 'y=', 'z=']

        # enable loop button
        self.btn_loop.setEnabled(True)
        
        # if system is selected
        if self.system_widget.system is not None:
            # initialize system
            system = self.system_widget.system(params={}, cb_update=None)

            # set cache path
            cache_dir = 'data/' + system.code
            self.le_path.setText(cache_dir + '/'+ (value if value != 'NA' else 'V'))

            # searching function
            found = lambda name, dim: sum([0 if name.find(e) == -1 else 1 for e in expr[:dim + 1]]) == dim + 1 and sum([0 if name.find(e) == -1 else 1 for e in expr]) == dim + 1
            # search templates
            for template_name in os.listdir('gui_templates'):
                # if template found
                if system is not None and template_name.find(system.code) != -1 and found(template_name, self.loopers.index(self.looper) + 1):
                    # import template
                    template = importlib.import_module('gui_templates.' + template_name[:-3])
                    # if template contains parameters
                    if template.__dict__.get('params', None) is not None:
                        # extract parameters
                        params = template.__dict__['params']
                        # set looper parameters
                        if params.get('looper', None) is not None:
                            [[self.param_widgets[i * 4 + j].setText(str(params['looper'][axes[i]][keys[j]])) if keys[j] in params['looper'][axes[i]] else None for j in range(4)] for i in range(self.loopers.index(self.looper) + 1)]
                        # set system parameters
                        if self.system_widget.system is not None:
                            self.system_widget.set_params(params.get('system', {}))
                        # set solver parameters
                        if self.solver_widget.solver is not None:
                            self.solver_widget.set_params(params.get('solver', {}))
                        # set plotter parameters
                        if self.plotter_widget.plotter is not None:
                            self.plotter_widget.set_params(params.get('plotter', {}))

        # update footer
        self.parent.update(status='Ready', progress=None, reset=True)

    def set_curr_item(self, pos):
        """Method to set the current looper.
        
        Parameters
        ----------
        pos : int
            Position of the current looper.
        """

        # enable all widgets
        for idx in range(self.layout.count()):
            self.layout.itemAt(idx).widget().setEnabled(True)

        # update looper
        self.looper = self.loopers[pos]

        # update parameter widgets
        axes = ['x', 'y', 'z']
        for idx in range(len(self.param_widgets)):
            vals = [axes[int(idx / 4)], 0.0, 100.0, 1001]
            self.param_widgets[idx].setText('' if int(idx / 4) > pos else str(vals[idx % 4]))
            self.param_widgets[idx].setDisabled(True if int(idx / 4) > pos else False)

        # get combo box items
        cmbx_items = ['NA'] if self.system_widget.cmbx_func.count() == 0 or self.system_widget.cmbx_func.currentText() == 'NA' else [self.system_widget.cmbx_func.itemText(i) for i in range(self.system_widget.cmbx_func.count())]

        # update widget
        self.lbl_name.setText(str(pos + 1) + 'D Looper')
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_items)

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

    def toggle_wrap(self):
        """Method to set up wrapper functions."""

        # if checked, add wrapper functions
        if self.chbx_wrap.isChecked() and self.system_widget.system is not None:
            self.cmbx_func.addItems([key for key in default_looper_func_names])
        
        # else remove wrapper functions
        else:
            num_items = self.cmbx_func.count()
            for idx in range(num_items):
                if self.cmbx_func.itemText(num_items - idx - 1) in default_looper_func_names:
                    self.cmbx_func.removeItem(num_items - idx - 1)