#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a custom header."""

__name__    = 'qom.ui.widgets.HeaderWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-01-21'

# dependencies
from PyQt5 import QtCore, QtWidgets
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class HeaderWidget(BaseWidget):
    """Class to create a custom header.

    Inherits :class:`qom.ui.widgets.BaseWidget`.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the header.
    """

    def __init__(self, parent):
        """Class constructor for HeaderWidget."""

        # initialize super class
        super().__init__(parent)

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        icon_height = 32
        icon_width = 48

        # match parent width
        self.setFixedWidth(1280)
        # move to top
        self.move(0, 0)
        # drag offset
        self.parent.offset = None

        # initialize UI elements
        # menu button
        self.btn_menu = QtWidgets.QPushButton()
        self.btn_menu.setFixedSize(icon_height, icon_height)
        self.btn_menu.setMenu(self.__get_menu())
        # title
        self.lbl_title = QtWidgets.QLabel('GUI - QOM Toolbox')
        self.lbl_title.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_title.setFixedSize(1280 - 2 * icon_width - icon_height, icon_height)
        # minimize button
        self.btn_minimize = QtWidgets.QPushButton()
        self.btn_minimize.setFixedSize(icon_width, icon_height)
        self.btn_minimize.clicked.connect(self.parent.showMinimized)
        # close button
        self.btn_close = QtWidgets.QPushButton()
        self.btn_close.setFixedSize(icon_width, icon_height)
        self.btn_close.clicked.connect(self.parent.close)

        # update layout 
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.btn_menu)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_close)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # update theme
        self.theme = 'dark'
        self.set_theme()

    def __get_menu(self):
        """Method to populate the menu items."""

        # initialize menu
        menu = QtWidgets.QMenu(self)

        # theme menu
        theme_menu = QtWidgets.QMenu('Theme', menu)
        # dark theme
        action = theme_menu.addAction('Dark')
        action.triggered.connect(self.__set_app_theme_dark)
        action.setIconVisibleInMenu(False)
        # light theme
        action = theme_menu.addAction('Light')
        action.triggered.connect(self.__set_app_theme_light)
        action.setIconVisibleInMenu(False)
        # add menu item
        menu.addMenu(theme_menu)

        return menu

    def __set_app_theme_dark(self):
        """Method to set the dark theme."""
        
        self.parent.set_theme('dark')

    def __set_app_theme_light(self):
        """Method to set the light theme."""
        
        self.parent.set_theme('light')

    def mousePressEvent(self, event):
        """Method to override mouse press events."""
        
        # detect parent position
        if event.button() == QtCore.Qt.LeftButton:
            self.parent.offset = event.pos()
        # default behaviour
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Method to override mouse move events."""

        # update parent position
        if self.parent.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.parent.move(self.parent.pos() + event.pos() - self.parent.offset)
        # default behaviour
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Method to override mouse release events."""

        # reset offset
        self.parent.offset = None
        # default behaviour
        super().mouseReleaseEvent(event)

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
            # icons
            self.btn_menu.setIcon(self.get_icon('menu_dark'))
            self.btn_minimize.setIcon(self.get_icon('window_minimize_dark'))
            self.btn_close.setIcon(self.get_icon('window_close_dark'))
            # styles
            self.setStyleSheet(self.get_stylesheet('header_light'))
            self.btn_close.setStyleSheet(self.get_stylesheet('window_close_light'))
        else:
            # icons
            self.btn_menu.setIcon(self.get_icon('menu_light'))
            self.btn_minimize.setIcon(self.get_icon('window_minimize_light'))
            self.btn_close.setIcon(self.get_icon('window_close_light'))
            # styles
            self.setStyleSheet(self.get_stylesheet('header_dark'))
            self.btn_close.setStyleSheet(self.get_stylesheet('window_close_dark'))