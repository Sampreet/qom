#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the systems."""

__name__    = 'qom.ui.widgets.SystemWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2022-07-26'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import importlib
import inspect
import logging
import os
import re

# qom modules
from .BaseWidget import BaseWidget
from .ParamWidget import ParamWidget

# module logger
logger = logging.getLogger(__name__)

class SystemWidget(BaseWidget):
    """Class to create a widget for the systems.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the widget.
    """

    def __init__(self, parent):
        """Class constructor for SystemWidget."""

        # initialize super class
        super().__init__(parent)
        self.system = None
        self.param_widgets = list()

        # initialize layout
        self.__init_layout()

        # set systems
        self.__set_systems()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        row_height = 32
        padding = 32

        # fix size
        self.setFixedWidth(width)
        # move under header
        self.move(0, padding)

        # initialize UI elements
        # system name
        self.lbl_name = QtWidgets.QLabel('Select a system to begin')
        self.lbl_name.setFixedSize(width, 2 * row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=16, italic=True))
        # function label
        self.lbl_func = QtWidgets.QLabel('Function:')
        self.lbl_func.setFixedSize(width, row_height) 
        self.lbl_func.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_func.setVisible(False)
        # function combo box
        self.cmbx_func = QtWidgets.QComboBox()
        self.cmbx_func.setFixedSize(width * 3 / 4 - padding, row_height)
        self.cmbx_func.currentTextChanged.connect(self.set_curr_func)
        self.cmbx_func.setVisible(False)
        # calculate button
        self.btn_calc = QtWidgets.QPushButton('Calculate')
        self.btn_calc.setFixedSize(width / 4 - padding, row_height)
        self.btn_calc.clicked.connect(self.calculate)
        self.btn_calc.setVisible(False)
        # value label
        self.lbl_value = QtWidgets.QLabel('Value:')
        self.lbl_value.setFixedSize(width, row_height)
        self.lbl_value.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_value.setVisible(False)
        # value line edit
        self.le_value = QtWidgets.QLineEdit('')
        self.le_value.setFixedSize(width - padding, row_height)
        self.le_value.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.le_value.setVisible(False)
        # parameter label
        self.lbl_params = QtWidgets.QLabel('Parameters:')
        self.lbl_params.setFixedSize(width, row_height)
        self.lbl_params.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_params.setVisible(False)

        # update layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.lbl_name, 0, 0, 2, 4)
        self.layout.addWidget(self.lbl_func, 2, 0, 1, 4)
        self.layout.addWidget(self.cmbx_func, 3, 0, 1, 3, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.btn_calc, 3, 3, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lbl_value, 4, 0, 1, 4)
        self.layout.addWidget(self.le_value, 5, 0, 1, 4, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lbl_params, 6, 0, 1, 4)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def __set_systems(self):
        """Method to set the system."""

        # update status
        self.parent.update(status='Searching for available systems...')

        # initialize list
        self.systems = list()

        # check for systems directory
        if 'systems' in os.listdir():
            # import all system modules
            module_names = importlib.import_module('systems', '*')
            # add available system classes
            for module_name in module_names.__dict__:
                if module_name[0] != '_':
                    self.systems.append(getattr(module_names, module_name))

        # update status
        if len(self.systems) == 0:
            status = 'No systems available'
        else: 
            status = 'Select a system to begin'
        self.lbl_name.setText(status)
        self.parent.update(status=status)
    
    def calculate(self):
        """Method to calcualte a selected function."""

        # disable calculate button
        self.btn_calc.setDisabled(True)

        # handle no function found
        if self.cmbx_func.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return

        else:
            # update status
            self.parent.update(status='Calculating...')

            # update value
            self.le_value.setText(str(self.get_value(self.get_params())))

            # update footer
            self.parent.update(status='Value Calculated', progress=None, reset=True)

            # enable calculate button
            self.btn_calc.setDisabled(False)
    
    def get_params(self):
        """Method to obtain the parameters for the system.
        
        Returns
        -------
        params: dict
            Parameters for the system.
        """

        # initialize dict
        params = dict()
        # evaluate parameters
        for widget in self.param_widgets:
            key = widget.key
            val = widget.val
            params[key] = eval(val) if re.match('\-*\d+\.*e*\-*\d*', val) is not None else val
        
        return params

    def get_value(self, params):
        """Method to obtain the calculated value.
        
        Parameters
        ----------
        params : dict
            Parameters of the system.
        """

        # selected function name
        func_name = self.cmbx_func.currentText()

        # initialize system
        system = self.system(params=params, cb_update=self.parent.update)

        # extract parameters
        _, c = system.get_ivc()
        _len_D = 4 * system.num_modes**2
        params = c[_len_D:] if len(c) > _len_D else c

        # get value
        value = getattr(system, 'get_' + func_name)(params)

        return value

    def get_list_items(self):
        """Method to obtain the codenames of available systems.
        
        Returns
        -------
        items : list
            Names of the systems.
        """

        # initialize lists
        items = list()

        # iterate through available systems
        for system in self.systems:
            items.append(system(params={}, cb_update=None).__class__.__name__)

        return items

    def set_curr_func(self, value):
        """Method to update the widget when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # enable button
        self.btn_calc.setDisabled(False)

        # update label
        self.le_value.setText('')

        # update footer
        self.parent.update(status='Ready', progress=None, reset=True)

    def set_curr_item(self, pos):
        """Method to set the system.
        
        Parameters
        ----------
        pos : int
            Position of the available system.
        """

        # frequently used parameters
        width = 640
        row_height = 32
        pre_count = 7

        # update system
        self.system = self.systems[pos]

        # initalize system
        system = self.system(params={}, cb_update=None)

        # search for available functions
        func_names = [func[4:] for func in dir(system) if callable(getattr(system, func)) and func[:4] == 'get_']
        # filter functions with system parameters
        cmbx_items = list()
        for func_name in func_names:
            func = getattr(system, 'get_' + func_name)
            func_args = inspect.getfullargspec(func).args[1:]
            if len(func_args) == 1 and func_args[0] == 'params':
                cmbx_items.append(func_name)
        # no functions found
        if len(cmbx_items) == 0:
            cmbx_items.append('NA')

        # clear widgets
        for widget in self.param_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
            
        # reset list
        self.param_widgets = list()

        # add widgets
        params = system.params
        widget_col = 0
        for param in params:
            # new widget
            widget = ParamWidget(parent=self, width=width / 4)
            widget.key = param
            widget.val = params[param]
            # update list
            self.param_widgets.append(widget)
            self.layout.addWidget(widget, int(widget_col / 4) * 2 + pre_count, int(widget_col % 4), 2, 1)
            # update count
            widget_col += 1

        # update UI elements
        self.lbl_name.setText(system.name)
        self.lbl_func.setVisible(True)
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_items)
        self.cmbx_func.setVisible(True)
        self.btn_calc.setVisible(True)
        self.lbl_value.setVisible(True)
        self.le_value.setVisible(True)
        self.lbl_params.setVisible(True)
        param_rows = int(widget_col / 4) * 2 + (2 if widget_col % 4 != 0 else 0)
        self.setFixedHeight((pre_count + param_rows) * row_height)

        self.get_scripts()

        # update theme
        self.set_theme()
    
    def set_params(self, params):
        """Method to set the parameters for the system.
        
        Parameters
        ----------
        params: dict
            Parameters for the system.
        """

        # set parameters
        for widget in self.param_widgets:
            if widget.key in params:
                widget.val = params[widget.key]

    def get_scripts(self):
        """Method to obtain available scripts."""

        # initialize list
        fig_names = list()

        # if system is selected 
        if self.system is not None:
            # initialize system
            system = self.system(params={}, cb_update=None)
            # script directory
            script_dir = 'scripts/' + str(system.code)

            # if script directory exists
            if os.path.isdir(script_dir):
                # search scripts
                for script_name in os.listdir(script_dir):
                    # if script found
                        # collect figure names
                        fig_names.append(script_name)

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