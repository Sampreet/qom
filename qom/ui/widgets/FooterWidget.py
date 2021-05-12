#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a custom footer."""

__name__    = 'qom.ui.widgets.FooterWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-01-22'

# dependencies
from PyQt5 import QtCore, QtWidgets
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class FooterWidget(BaseWidget):
    """Class to create a custom footer.

    Inherits :class:`qom.ui.widgets.BaseWidget`.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the sidebar.
    """

    def __init__(self, parent):
        """Class constructor for FooterWidget."""

        # initialize super class
        super().__init__(parent)

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 600
        height = 32

        # match parent width
        self.setFixedWidth(1280)
        # move to bottom
        self.move(0, 720 - height)

        # initialize UI elements
        # blank left
        self.blank_left = QtWidgets.QLabel('')
        self.blank_left.setFixedSize(32, height)
        # status
        self.status = QtWidgets.QLabel('Ready')
        self.status.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.status.setFixedSize(width, height)
        # blank center
        self.blank_center = QtWidgets.QLabel('')
        self.blank_center.setFixedSize(16, height)
        # progress
        self.progress = QtWidgets.QProgressBar()
        self.progress.setAlignment(QtCore.Qt.AlignCenter)
        self.progress.setFixedSize(width, height)
        # blank right
        self.blank_right = QtWidgets.QLabel('')
        self.blank_right.setFixedSize(32, height)

        # update layout 
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.blank_left)
        self.layout.addWidget(self.status)
        self.layout.addWidget(self.blank_center)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.blank_right)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def reset_progress(self):
        """Method to reset progress."""

        self.progress.setValue(0)
        self.progress.setTextVisible(False)

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
            self.setStyleSheet(self.get_stylesheet('footer_light'))
        else:
            # styles
            self.setStyleSheet(self.get_stylesheet('footer_dark'))

    def update_progress(self, progress):
        """Method to update progress.
        
        Parameters
        ----------
        progress : int or float
            Progress percentage.
        """

        self.progress.setValue(int(progress))
        self.progress.setTextVisible(True)

    def update_status(self, status):
        """Method to update status.
        
        Parameters
        ----------
        status : str
            Status message.
        """

        self.status.setText(str(status))