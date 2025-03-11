#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the systems."""

__name__    = 'qom.ui.widgets.SystemWidget'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-01-21"
__updated__ = "2025-03-08"

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
from subprocess import call
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

        # set attributes
        self.SystemClass = None
        self.SystemClasses = list()
        self.param_widgets = list()
        self.script_names = list()

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

        # initialize grid layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # system name
        self.lbl_name = QtWidgets.QLabel('Select a system to begin')
        self.lbl_name.setFixedSize(width, 2 * row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=14, italic=True))
        self.layout.addWidget(self.lbl_name, 0, 0, 2, 4)
        # function label
        self.lbl_script = QtWidgets.QLabel('Script:')
        self.lbl_script.setFixedSize(width, row_height) 
        self.lbl_script.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_script.setVisible(False)
        self.layout.addWidget(self.lbl_script, 2, 0, 1, 4)
        # function combo box
        self.cmbx_script = QtWidgets.QComboBox()
        self.cmbx_script.setFixedSize(int(width * 3 / 4 - padding), row_height)
        self.cmbx_script.currentTextChanged.connect(self.set_curr_script)
        self.cmbx_script.setVisible(False)
        self.layout.addWidget(self.cmbx_script, 3, 0, 1, 3, alignment=QtCore.Qt.AlignRight)
        # calculate button
        self.btn_run = QtWidgets.QPushButton('Run Script')
        self.btn_run.setFixedSize(int(width / 4 - padding), row_height)
        self.btn_run.clicked.connect(self.run_script)
        self.btn_run.setVisible(False)
        self.layout.addWidget(self.btn_run, 3, 3, 1, 1, alignment=QtCore.Qt.AlignRight)
        # function label
        self.lbl_func = QtWidgets.QLabel('Function:')
        self.lbl_func.setFixedSize(width, row_height) 
        self.lbl_func.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_func.setVisible(False)
        self.layout.addWidget(self.lbl_func, 4, 0, 1, 4)
        # function combo box
        self.cmbx_func = QtWidgets.QComboBox()
        self.cmbx_func.setFixedSize(int(width * 3 / 4 - padding), row_height)
        self.cmbx_func.currentTextChanged.connect(self.set_curr_func)
        self.cmbx_func.setVisible(False)
        self.layout.addWidget(self.cmbx_func, 5, 0, 1, 3, alignment=QtCore.Qt.AlignRight)
        # calculate button
        self.btn_calc = QtWidgets.QPushButton('Calculate')
        self.btn_calc.setFixedSize(int(width / 4 - padding), row_height)
        self.btn_calc.clicked.connect(self.calculate)
        self.btn_calc.setVisible(False)
        self.layout.addWidget(self.btn_calc, 5, 3, 1, 1, alignment=QtCore.Qt.AlignRight)
        # value label
        self.lbl_value = QtWidgets.QLabel('Value:')
        self.lbl_value.setFixedSize(width, row_height)
        self.lbl_value.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_value.setVisible(False)
        self.layout.addWidget(self.lbl_value, 6, 0, 1, 4)
        # value line edit
        self.le_value = QtWidgets.QLineEdit('')
        self.le_value.setFixedSize(width - padding, row_height)
        self.le_value.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.le_value.setVisible(False)
        self.layout.addWidget(self.le_value, 7, 0, 1, 4, alignment=QtCore.Qt.AlignRight)
        # parameter label
        self.lbl_params = QtWidgets.QLabel('Parameters:')
        self.lbl_params.setFixedSize(width, row_height)
        self.lbl_params.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_params.setVisible(False)
        self.layout.addWidget(self.lbl_params, 8, 0, 1, 4)

        # update main layout
        self.move(0, padding)
        self.setFixedWidth(width)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def __set_systems(self):
        """Method to set the system."""

        # update status
        self.parent.update(status='Searching for available systems...')

        # initialize list
        self.SystemClasses = list()

        # check for systems directory
        if 'systems' in os.listdir():
            # import all system modules
            module_names = os.listdir('systems')
            # add available system classes
            for module_name in module_names:
                if os.path.isfile(os.path.join('systems', module_name)) and module_name[-2:] == 'py' and module_name[0:2] != '__':
                    module = importlib.import_module('systems.' + module_name[:-3], '*')
                    for system_name in module.__all__:
                        self.SystemClasses.append(getattr(module, system_name))

        # update status
        if len(self.SystemClasses) == 0:
            status = 'No systems available'
        else: 
            status = 'Select a system to begin'
        self.lbl_name.setText(status)
        self.parent.update(status=status)
    
    def run_script(self):
        """Method to calcualte a selected function."""

        # disable run button
        self.btn_run.setDisabled(True)

        # handle no function found
        if self.cmbx_script.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return

        else:
            # update status
            self.parent.update(status='Calculating...', progress=None, reset=True)

            # call file
            call(['python', 'scripts/' + str(self.SystemClass.__name__.lower()) + '/' + self.cmbx_script.currentText()])
            # # execute file
            # os.system('python ' + 'scripts/' + str(self.SystemClass.__name__.lower()) + '/' + self.cmbx_script.currentText())

            # update footer
            self.parent.update(status='Completed', progress=None, reset=True)

            # enable calculate button
            self.btn_run.setDisabled(False)
    
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
        system = self.SystemClass(params=params, cb_update=self.parent.update)

        # extract parameters
        _, _, c = system.get_ivc()
        # get value
        value = getattr(system, 'get_' + func_name)(
            c=c
        )

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
        for SystemClass in self.SystemClasses:
            items.append(SystemClass.__name__)

        return items

    def set_curr_script(self, value):
        """Method to update the widget when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # enable button
        self.btn_run.setDisabled(False)

        # update footer
        self.parent.update(status='Ready', progress=None, reset=True)

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
        pre_count = 9

        # update system
        self.SystemClass = self.SystemClasses[pos]

        # initalize system
        system = self.SystemClass(params={}, cb_update=None)

        # initialize list
        cmbx_script_items = list()
        # script directory
        script_dir = 'scripts/' + str(self.SystemClass.__name__.lower())
        # if script directory exists
        if os.path.isdir(script_dir):
            # search scripts
            for script_name in os.listdir(script_dir):
                # if script found collect figure names
                cmbx_script_items.append(script_name)
        # no scripts found
        if len(cmbx_script_items) == 0:
            cmbx_script_items.append('NA')

        # search for available functions
        func_names = [func[4:] for func in dir(system) if callable(getattr(system, func)) and func[:4] == 'get_']
        # filter functions with system parameters
        cmbx_func_items = list()
        for func_name in func_names:
            func = getattr(system, 'get_' + func_name)
            func_args = inspect.getfullargspec(func).args[1:]
            if len(func_args) == 1 and func_args[0] == 'c':
                cmbx_func_items.append(func_name)
        # no functions found
        if len(cmbx_func_items) == 0:
            cmbx_func_items.append('NA')

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
        self.lbl_name.setText(system.desc)
        self.lbl_script.setVisible(True)
        self.cmbx_script.clear()
        self.cmbx_script.addItems(cmbx_script_items)
        self.cmbx_script.setVisible(True)
        self.btn_run.setVisible(True)
        self.lbl_func.setVisible(True)
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_func_items)
        self.cmbx_func.setVisible(True)
        self.btn_calc.setVisible(True)
        self.lbl_value.setVisible(True)
        self.le_value.setVisible(True)
        self.lbl_params.setVisible(True)
        param_rows = int(widget_col / 4) * 2 + (2 if widget_col % 4 != 0 else 0)
        self.setFixedHeight((pre_count + param_rows) * row_height)

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