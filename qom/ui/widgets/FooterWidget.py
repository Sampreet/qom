#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a custom footer."""

__name__    = 'qom.ui.widgets.FooterWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2023-10-28'

# dependencies
from PyQt5 import QtCore, QtWidgets
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class FooterWidget(BaseWidget):
    """Class to create a custom footer.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
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
        width = 300
        height = 32
        padding = 32

        # update layout 
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # initialize left blank label
        self.lbl_left = QtWidgets.QLabel('')
        self.lbl_left.setFixedSize(padding, height)
        self.layout.addWidget(self.lbl_left)
        # initialize status label
        self.lbl_status = QtWidgets.QLabel('Ready')
        self.lbl_status.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_status.setFixedSize(width, height)
        self.layout.addWidget(self.lbl_status)
        # initialize status line edit
        self.le_status = QtWidgets.QLineEdit('')
        self.le_status.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.le_status.setFixedSize(width, height)
        self.layout.addWidget(self.le_status)
        # initialize center blank label
        self.lbl_center = QtWidgets.QLabel('')
        self.lbl_center.setFixedSize(int(padding / 2), height)
        self.layout.addWidget(self.lbl_center)
        # initialize progress bar
        self.pb = QtWidgets.QProgressBar()
        self.pb.setAlignment(QtCore.Qt.AlignCenter)
        self.pb.setFixedSize(2 * width, height)
        self.layout.addWidget(self.pb)
        # initialize right blank label
        self.lbl_right = QtWidgets.QLabel('')
        self.lbl_right.setFixedSize(padding, height)
        self.layout.addWidget(self.lbl_right)

        # update main layout
        self.move(0, 720 - height)
        self.setFixedWidth(1280)
        self.setFixedHeight(height)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

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
            self.setStyleSheet(self.get_stylesheet('footer_light'))
        else:
            # styles
            self.setStyleSheet(self.get_stylesheet('footer_dark'))

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

        # update status
        if status is not None:
            parts = str(status.replace('-', '')).split(': ')
            status = parts[0]
            self.lbl_status.setText(str(status))
            value = ''
            for part in parts[1:]:
                value += part
            self.le_status.setText(value)

        # update progress
        if progress is not None:
            self.pb.setValue(int(progress))
            self.pb.setTextVisible(True)

        # reset progress
        if reset:
            self.pb.setValue(0)
            self.pb.setTextVisible(False)