#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""GUI module for systems and scripts."""

__name__    = 'qom.ui.gui'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-01-19"
__updated__ = "2025-03-08"

# dependencies
from PyQt5 import QtCore, QtWidgets
import sys

# qom modules
from .log import init_log
from .widgets import *

# TODO: Add option to resize window.
# TODO: Integrate layouts.

class GUI(QtWidgets.QFrame):
    """Class to display the GUI.
    
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

    def __init__(self, theme='dark'):
        """Class constructor for GUI."""

        # initialize super class
        super().__init__()

        # 720p fixed window frame
        self.resize(1280, 720)

        # remove default titlebar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # application widgets
        self.__init_widgets()
        # update theme
        self.set_theme(theme)

    def __init_widgets(self):
        """Method to initialize the application widgets."""

        # header
        self.header = HeaderWidget(parent=self)
        # footer
        self.footer = FooterWidget(parent=self)
        # system
        self.system_widget = SystemWidget(self)
        self.sidebar_system = SidebarWidget(parent=self, widget=self.system_widget, pos='left', name='Systems')
        # plotter
        self.plotter_widget = PlotterWidget(self)
        self.sidebar_plotter = SidebarWidget(parent=self, widget=self.plotter_widget, pos='bottom-right', name='Plotters')
        # solver
        self.solver_widget = SolverWidget(parent=self, system_widget=self.system_widget, plotter_widget=self.plotter_widget)
        self.sidebar_solver = SidebarWidget(parent=self, widget=self.solver_widget, pos='top-right', name='Solvers')
        # looper
        self.looper_widget = LooperWidget(parent=self, solver_widget=self.solver_widget, system_widget=self.system_widget, plotter_widget=self.plotter_widget)
        self.sidebar_looper = SidebarWidget(parent=self, widget=self.looper_widget, pos='center-right', name='Loopers')

    def set_theme(self, theme):
        """Method to update the application theme.
        
        Parameters
        ----------
        theme : str
            Display theme. Available options are:
                ==========  ==============
                value       meaning
                ==========  ==============  
                "dark"      dark mode.
                "light"     light mode.
                ==========  ==============
        """
        
        # frame
        if theme == 'light':
            self.setStyleSheet('background-color: #FAFAFA')
        else:
            self.setStyleSheet('background-color: #212121')
        
        # header
        self.header.set_theme(theme)
        # footer
        self.footer.set_theme(theme)
        # solver
        self.solver_widget.set_theme(theme)
        self.sidebar_solver.set_theme(theme)
        # system
        self.system_widget.set_theme(theme)
        self.sidebar_system.set_theme(theme)
        # plotter
        self.plotter_widget.set_theme(theme)
        self.sidebar_plotter.set_theme(theme)
        # looper
        self.looper_widget.set_theme(theme)
        self.sidebar_looper.set_theme(theme)

    def update(self, status=None, progress=None, reset=False):
        """Method to update status.
        
        Parameters
        ----------
        status : str, optional
            Status message.
        progress : int or float, optional
            Progress percentage.
        reset : boolean, optional
            Option to reset progress.
        """

        # update footer
        self.footer.update(status=status, progress=progress, reset=reset)

def run(theme='dark'):
    """Function to run the PyQt application.
    
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

    # initialize logging
    init_log()

    # get application
    app = QtWidgets.QApplication(sys.argv)

    # initialize GUI
    gui = GUI(theme)
    gui.show()

    # run application
    app.exec_()