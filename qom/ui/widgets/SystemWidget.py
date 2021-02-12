#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the systems."""

__name__    = 'qom.ui.widgets.SystemWidget'
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

class SystemWidget(BaseWidget):
    """Class to create a widget for the systems.

    Inherits :class:`qom.ui.widgets.BaseWidget`.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the widget.
    """

    def __init__(self, parent):
        """Class constructor for SystemWidget."""

        # initialize super class
        super().__init__(parent)
        self.curr_system = None
        self.system_params = None
        self.solver_params = None
        self.param_widgets = list()

        # initialize layout
        self.__init_layout()

        # set systems
        self.__set_systems()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        label_height = 48
        param_height = 32
        padding = 32

        # fix size
        self.setFixedWidth(width)
        # move under header
        self.move(0, padding)

        # initialize UI elements
        # name
        self.lbl_name = QtWidgets.QLabel()
        self.lbl_name.setFixedSize(width, 64)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=16, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # property label
        self.lbl_prop = QtWidgets.QLabel('Property')
        self.lbl_prop.setFixedSize(width, label_height) 
        self.lbl_prop.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_prop.setVisible(False)
        # measure label
        self.lbl_meas = QtWidgets.QLabel('Measure')
        self.lbl_meas.setFixedSize(width, label_height) 
        self.lbl_meas.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_meas.setVisible(False)
        # property combo box
        self.cmbx_prop = QtWidgets.QComboBox()
        self.cmbx_prop.setFixedSize(width / 2 - padding, param_height)
        self.cmbx_prop.addItems(['NA'])
        self.cmbx_prop.setVisible(False)
        # calculate button
        self.btn_calc = QtWidgets.QPushButton('Calculate')
        self.btn_calc.setFixedSize(width / 2 - padding, param_height)
        self.btn_calc.clicked.connect(self.calculate_property)
        self.btn_calc.setVisible(False)
        # measure combo box
        self.cmbx_meas = QtWidgets.QComboBox()
        self.cmbx_meas.setFixedSize(width / 2 - padding, param_height)
        self.cmbx_meas.addItems(['NA'])
        self.cmbx_meas.setVisible(False)
        # plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot Dynamics')
        self.chbx_plot.setFixedSize(width / 2 - padding, param_height)
        self.chbx_plot.setVisible(False)
        # parameter label
        self.lbl_params = QtWidgets.QLabel('Parameters')
        self.lbl_params.setFixedSize(width, label_height)
        self.lbl_params.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_params.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_params.setVisible(False)

        # update layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.lbl_name, 0, 0)
        self.layout.addWidget(self.lbl_prop, 1, 0)
        self.layout.addWidget(self.cmbx_prop, 2, 0, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.btn_calc, 2, 1, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lbl_meas, 3, 0)
        self.layout.addWidget(self.cmbx_meas, 4, 0, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.chbx_plot, 4, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.lbl_params, 5, 0)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def __set_systems(self):
        """Method to obtain the system."""

        # update status
        self.parent.update_status('Searching for available systems...')

        # initialize list
        systems = list()

        # check for systems directory
        if 'systems' in os.listdir():
            # import all system modules
            modules = importlib.import_module('systems', '*')
            # add available system classes
            for module_name in modules.__dict__:
                if module_name[0] != '_':
                    systems.append(modules.__getattribute__(module_name))
            
        self.systems = systems

        # update status
        if len(systems) == 0:
            status = 'No systems available'
        else: 
            status = 'Select a system to begin'
        self.parent.update_status(status)
        self.lbl_name.setText(status)
    
    def calculate_property(self):
        """Method to calcualte a system property."""

        # disable button
        self.btn_calc.setDisabled(True)

        # selected property name
        prop_name = self.cmbx_prop.currentText()

        # no property selected
        if prop_name == 'NA':
            # update status
            self.parent.update_status('Select the system property to calcuate')

        # system parameters not initialized
        elif self.system_params is None:
            # update status
            self.parent.update_status('System parameters not initialized')

        # solver parameters not initialized
        elif self.solver_params is None:
            # update status
            self.parent.update_status('Solver parameters not initialized')

        # load parameters
        for widget in self.param_widgets:
            key = widget.get_key()
            val = widget.get_val()
            self.system_params[key] = json.loads(val)

        # enable button
        self.btn_calc.setDisabled(False)

    def get_list_items(self):
        """Method to obtain the codenames of available systems.
        
        Returns
        -------
        codes : list
            Codenames of the systems.
        """

        # initialize lists
        codes = list()

        # iterate through available systems
        for system in self.systems:
            codes.append(system({}).code)

        return codes

    def set_curr_item(self, pos):
        """Method to set the system.
        
        Parameters
        ----------
        pos : int
            Position of the available system.
        """

        # frequently used parameters
        base_height = 64 + 3 * 48 + 2 * 32

        # update parameter
        self.pos = pos
        self.curr_system = self.systems[pos]

        # system name
        self.lbl_name.setText(self.curr_system({}).name)
        # available properties
        properties = [func[13:] for func in dir(self.curr_system) if callable(getattr(self.curr_system, func)) and func[:13] == 'get_property_']
        # available measures
        measures = [func[12:] for func in dir(self.curr_system) if callable(getattr(self.curr_system, func)) and func[:12] == 'get_measure_']
        
        # update combo boxes
        self.cmbx_prop.clear()
        self.cmbx_prop.addItem('NA')
        self.cmbx_prop.addItems(properties)
        self.cmbx_meas.clear()
        self.cmbx_meas.addItem('NA')
        self.cmbx_meas.addItems(measures)

        # clear widgets
        for widget in self.param_widgets:
            self.layout.removeWidget(widget)

        # add widgets
        self.system_params = self.curr_system({}).params
        widget_col = 12
        for param in self.system_params:
            # new widget
            widget = ParamWidget(self)
            widget.set_key(param)
            widget.set_val(self.system_params[param])
            # update list
            self.param_widgets.append(widget)
            self.layout.addWidget(widget, int(widget_col / 2), int(widget_col % 2))
            # update count
            widget_col += 1

        # update UI elements
        self.lbl_prop.setVisible(True)
        self.lbl_meas.setVisible(True)
        self.cmbx_prop.setVisible(True)
        self.btn_calc.setVisible(True)
        self.cmbx_meas.setVisible(True)
        self.chbx_plot.setVisible(True)
        self.lbl_params.setVisible(True)
        self.setFixedHeight(base_height + int((widget_col - 11) / 2) * 32)

        # update theme
        self.set_theme()

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

        # widgets
        for widget in self.param_widgets:
            widget.set_theme(self.theme)
