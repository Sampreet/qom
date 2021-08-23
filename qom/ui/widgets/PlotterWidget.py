#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the plotters."""

__name__    = 'qom.ui.widgets.PlotterWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-20'
__updated__ = '2021-08-23'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

# qom modules
from ..plotters import *
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
        self.plotter = None

        # initialize layout
        self.__init_layout()

        # set plotters
        self.plotters = [MPLPlotter]

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        row_height = 32
        padding = 32

        # fix size
        self.setFixedWidth(width)
        # move under header
        self.move(640, 480 + 4)

        # initialize UI elements
        # plotter label
        self.lbl_name = QtWidgets.QLabel('Select a plotter to begin')
        self.lbl_name.setFixedSize(width, row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        # plotter parameters
        self.te_params = QtWidgets.QTextEdit('')
        self.te_params.setFixedSize(width - 2 * padding, row_height * 5)

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
        """Method to obtain the names of available plotters.
        
        Returns
        -------
        codes : list
            Codenames of the plotters.
        """

        # initialize lists
        codes = ['mpl_plotter']

        return codes
    
    def get_params(self):
        """Method to obtain the parameters for the plotter.
        
        Returns
        -------
        params: dict
            Parameters for the plotter.
        """

        # evaluate parameters
        params = eval(self.te_params.toPlainText()) if self.te_params.toPlainText() != '' else {}
        
        return params

    def set_curr_item(self, pos):
        """Method to set the current plotter.
        
        Parameters
        ----------
        pos : int
            Position of the current plotter.
        """

        # update parameter
        self.pos = pos
        self.plotter = self.plotters[pos]

        # update UI elements
        self.lbl_name.setText('Plotter Parameters:')
    
    def set_params(self, params):
        """Method to set the parameters for the plotter.
        
        Parameters
        ----------
        params: dict
            Parameters for the plotter.
        """
        
        # set parameters
        self.te_params.setText(str(params))

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