#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the plotters."""

__name__    = 'qom.ui.widgets.PlotterWidget'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-08-20"
__updated__ = "2025-03-08"

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import re

# qom modules
from ..plotters.base import BaseAxis
from ..plotters import MPLPlotter
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class PlotterWidget(BaseWidget):
    """Class to create a widget for the plotters.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the widget.
    """

    def __init__(self, parent):
        """Class constructor for PlotterWidget."""

        # initialize super class
        super().__init__(parent)

        # set attributes
        self.PlotterClass = None
        self.PlotterClasses = [MPLPlotter]
        self.widget_params = dict()

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        offset = 480
        row_height = 32
        padding = 32
        base_rows = 2
        param_rows = 4

        # initialize grid layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, padding, 0)

        # initialize plotter name
        self.lbl_name = QtWidgets.QLabel('Select Plotter')
        self.lbl_name.setFixedSize(int(width / 4), row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.lbl_name, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize type label
        self.lbl_type = QtWidgets.QLabel('Type:')
        self.lbl_type.setFixedSize(int(width / 2), row_height) 
        self.lbl_type.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_type, 0, 1, 1, 2, alignment=QtCore.Qt.AlignLeft)
        # initialize colorbar check box
        self.chbx_cbar = QtWidgets.QCheckBox('Colorbar')
        self.chbx_cbar.setFixedSize(int(width / 4), row_height)
        self.chbx_cbar.setDisabled(True)
        self.layout.addWidget(self.chbx_cbar, 0, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize type combo box
        self.cmbx_dim = QtWidgets.QComboBox()
        self.cmbx_dim.setFixedSize(int(width / 4 - 1.25 * padding), row_height)
        self.cmbx_dim.addItems(['1D Plot', '2D Plot', '3D Plot'])
        self.cmbx_dim.setDisabled(True)
        self.cmbx_dim.currentTextChanged.connect(self.set_curr_dim)
        self.layout.addWidget(self.cmbx_dim, 1, 0, 1, 1, alignment=QtCore.Qt.AlignRight)
        # initialize type combo box
        self.cmbx_type = QtWidgets.QComboBox()
        self.cmbx_type.setFixedSize(int(width / 2 - 1.5 * padding), row_height)
        self.cmbx_type.setDisabled(True)
        self.cmbx_type.currentTextChanged.connect(self.set_curr_type)
        self.layout.addWidget(self.cmbx_type, 1, 1, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize legend check box
        self.chbx_legend = QtWidgets.QCheckBox('Legend')
        self.chbx_legend.setFixedSize(int(width / 4), row_height)
        self.chbx_legend.setDisabled(True)
        self.layout.addWidget(self.chbx_legend, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
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
        # initialize extra label
        self.lbl_extra = QtWidgets.QLabel('Extra Parameters:')
        self.lbl_extra.setFixedSize(int(width / 2), row_height) 
        self.lbl_extra.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_extra, 2, 2, 1, 2, alignment=QtCore.Qt.AlignLeft)
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
        # plotter parameters
        self.te_params = QtWidgets.QTextEdit('')
        self.te_params.setFixedSize(int(width / 2 - 1.5 * padding), row_height * 3)
        self.te_params.setDisabled(True)
        self.layout.addWidget(self.te_params, 3, 2, 3, 2, alignment=QtCore.Qt.AlignRight)

        # update main layout
        self.move(width, offset + 4)
        self.setFixedWidth(width)
        self.setFixedHeight((base_rows + param_rows) * row_height)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def get_list_items(self):
        """Method to obtain the names of available plotters.
        
        Returns
        -------
        codes : list
            Codenames of the plotters.
        """

        # initialize lists
        codes = list()

        # iterate through available plotters
        for PlotterClass in self.PlotterClasses:
            codes.append(PlotterClass.name)

        return codes
    
    def get_params(self):
        """Method to obtain the parameters for the plotter.
        
        Returns
        -------
        params: dict
            Parameters for the plotter.
        """

        # initialize dict
        params = dict()

        # get type combo box
        params['type'] = self.cmbx_type.currentText()
        # get colorbar check box
        params['show_cbar'] = self.chbx_cbar.isChecked()
        # get legend check box
        params['show_legend'] = self.chbx_legend.isChecked()
        # combo box params
        for key in self.widget_params:
            params[key] = self.widget_params[key]
        # evaulate parameter text edit
        te_params = eval(self.te_params.toPlainText()) if self.te_params.toPlainText() != '' else {}
        for key in te_params:
            params[key] = te_params[key]
        
        return params

    def set_curr_item(self, pos):
        """Method to set the current plotter.
        
        Parameters
        ----------
        pos : int
            Position of the current plotter.
        """

        # enable all widgets
        for idx in range(self.layout.count()):
            self.layout.itemAt(idx).widget().setEnabled(True)
            
        # update plotter
        self.PlotterClass = self.PlotterClasses[pos]

        # update widget
        self.lbl_name.setText(self.PlotterClass.name)
        self.set_curr_dim(self.cmbx_dim.currentText())

    def set_curr_dim(self, value):
        """Method to update widgets when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        self.cmbx_type.clear()
        if '3D' in value:
            self.cmbx_type.addItems(self.PlotterClass.types_3D)
        elif '2D' in value:
            self.cmbx_type.addItems(self.PlotterClass.types_2D)
        else:
            self.cmbx_type.addItems(self.PlotterClass.types_1D)

    def set_curr_type(self, value):
        """Method to update widgets when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # initialize parameters
        params = dict()
        for key in self.PlotterClass.required_params.get(value, []):
            if key[0:2] in ['x_', 'y_', 'z_', 'v_']:
                params[key] = BaseAxis.axis_defaults[key[2:]]
            else:
                params[key] = self.PlotterClass.plotter_defaults.get(key, '')

        # set parameters
        self.set_params(params)
    
    def set_params(self, params):
        """Method to set the parameters for the plotter.
        
        Parameters
        ----------
        params: dict
            Parameters for the plotter.
        """
        
        # set type combo box
        if params.get('type', None) is not None:
            self.cmbx_type.setCurrentText(params['type'])
        # set colorbar check box
        self.chbx_cbar.setChecked(params.get('show_cbar', self.chbx_cbar.isChecked()))
        # set legend check box
        self.chbx_legend.setChecked(params.get('show_legend', self.chbx_legend.isChecked()))
        
        # set widget params
        self.cmbx_key.clear()
        self.widget_params = dict()
        keys = list()
        for key in params:
            if key not in ['type', 'show_cbar', 'show_legend']:
                self.widget_params[key] = params[key]
                keys.append(key)
        self.cmbx_key.addItems(keys)
        # set parameter text edit
        self.te_params.setText('')

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