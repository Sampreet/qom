#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the plotters."""

__name__    = 'qom.ui.widgets.PlotterWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-20'
__updated__ = '2021-09-01'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import numpy as np

# qom modules
from ..plotters import MPLPlotter
from .BaseWidget import BaseWidget
from .ParamWidget import ParamWidget

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
        self.plotters = [MPLPlotter]
        self.param_widgets = list()
        self.plotter = None

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

        # initialize type label
        self.lbl_type = QtWidgets.QLabel('Type:')
        self.lbl_type.setFixedSize(width / 4, row_height) 
        self.lbl_type.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.layout.addWidget(self.lbl_type, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize plotter name
        self.lbl_name = QtWidgets.QLabel('Select a plotter to begin')
        self.lbl_name.setFixedSize(width * 3 / 4 + 0.25 * padding, row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.lbl_name, 0, 1, 1, 3, alignment=QtCore.Qt.AlignRight)
        # initialize type combo box
        self.cmbx_type = QtWidgets.QComboBox()
        self.cmbx_type.setFixedSize(width / 2 - 1.5 * padding, row_height)
        self.cmbx_type.setDisabled(True)
        self.cmbx_type.currentTextChanged.connect(self.set_curr_type)
        self.layout.addWidget(self.cmbx_type, 1, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize colorbar check box
        self.chbx_cbar = QtWidgets.QCheckBox('Colorbar')
        self.chbx_cbar.setFixedSize(width / 4, row_height)
        self.chbx_cbar.setDisabled(True)
        self.layout.addWidget(self.chbx_cbar, 1, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize legend check box
        self.chbx_legend = QtWidgets.QCheckBox('Legend')
        self.chbx_legend.setFixedSize(width / 4, row_height)
        self.chbx_legend.setDisabled(True)
        self.layout.addWidget(self.chbx_legend, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # plotter parameters
        self.te_params = QtWidgets.QTextEdit('')
        self.te_params.setFixedSize(width / 2 - 1.5 * padding, row_height * 4)
        self.layout.addWidget(self.te_params, 2, 2, 4, 2, alignment=QtCore.Qt.AlignRight)
        self.te_params.setDisabled(True)

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
        for plotter in self.plotters:
            codes.append(plotter.code)

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
        # evaluate parameter widgets
        for widget in self.param_widgets:
            params[widget.key] = widget.val
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

        # frequently used parameters
        width = 640
        padding = 32
            
        # update plotter
        self.plotter = self.plotters[pos]

        # clear widgets
        for widget in self.param_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
            
        # reset list
        self.param_widgets = list()

        # update parameter widgets
        widget_col = 0
        for param in self.plotter.ui_params:
            # new widget
            val = self.plotter.ui_params[param]
            widget = ParamWidget(parent=self, width=(width - padding) / 4, val_type=type(val))
            widget.key = param
            if type(val) is list:
                widget.w_val.addItems(self.plotter.ui_params[param])
            else: 
                widget.val = self.plotter.ui_params[param]
            self.layout.addWidget(widget, 2 + int(widget_col / 2) * 2, int(widget_col % 2), 2, 1, alignment=QtCore.Qt.AlignRight)
            # update widget list
            self.param_widgets.append(widget)
            # update count
            widget_col += 1

        # update widget
        self.lbl_name.setText(str(self.plotter.name))
        self.cmbx_type.clear()
        self.cmbx_type.addItems(self.plotter.types_1D + self.plotter.types_2D + self.plotter.types_3D)

    def set_curr_type(self, value):
        """Method to update widgets when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # clear parameter text edit
        self.te_params.setText('')

        # initialize parameters
        params = dict()
        for key in self.plotter.required_params.get(value, []):
            # set ui defaults
            params[key] = self.plotter.ui_defaults[key]

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

        # set parameter widgets
        used_keys = ['type', 'show_cbar', 'show_legend']
        for widget in self.param_widgets:
            used_keys.append(widget.key)
            if widget.key in params:
                widget.val = params[widget.key]
        # get current parameters
        te_params = self.get_params()
        # remove used keys
        for key in used_keys:
            te_params.pop(key, None)
        # update extra parameters
        for key in params:
            if key not in used_keys:
                te_params[key] = params[key]
        # set parameter text edit
        self.te_params.setText(str(te_params))

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