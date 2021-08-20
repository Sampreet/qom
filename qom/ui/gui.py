#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""GUI module for systems and scripts."""

__name__    = 'qom.ui.gui'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-19'
__updated__ = '2021-08-20'

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
        Display theme:
            'dark': Dark mode.
            'light': Light mode.
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
        self.header = HeaderWidget(self)
        # footer
        self.footer = FooterWidget(self)
        # solver
        self.solver = SolverWidget(self)
        self.sidebar_solver = SidebarWidget(self, self.solver, 'top-right', 'Solvers')
        # system
        self.system = SystemWidget(self)
        self.sidebar_system = SidebarWidget(self, self.system, 'left', 'Systems')
        # plotter
        self.plotter = PlotterWidget(self)
        self.sidebar_plotter = SidebarWidget(self, self.plotter, 'bottom-right', 'Plotters')
        # looper
        self.looper = LooperWidget(self, self.solver, self.system, self.plotter)
        self.sidebar_looper = SidebarWidget(self, self.looper, 'center-right', 'Loopers')

    def set_theme(self, theme):
        """Method to update the application theme.
        
        Parameters
        ----------
        theme : str
            Display theme:
                'dark': Dark mode.
                'light': Light mode.
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
        self.solver.set_theme(theme)
        self.sidebar_solver.set_theme(theme)
        # system
        self.system.set_theme(theme)
        self.sidebar_system.set_theme(theme)
        # plotter
        self.plotter.set_theme(theme)
        self.sidebar_plotter.set_theme(theme)
        # looper
        self.looper.set_theme(theme)
        self.sidebar_looper.set_theme(theme)

    def update_status(self, status):
        """Method to update status.
        
        Parameters
        ----------
        status : str
            Status message.
        """

        self.footer.update_status(status)

    def reset_progress(self):
        """Method to reset the progress."""

        self.footer.reset_progress()

    def update_progress(self, progress):
        """Method to update progress.
        
        Parameters
        ----------
        progress : int or float
            Progress percentage.
        """

        self.footer.update_progress(progress)

def run(theme='dark'):
    """Function to run the PyQt application.
    
    Parameters
    ----------
    theme : str, optional
        Display theme:
            'dark': Dark mode.
            'light': Light mode.
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