#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a custom sidebar."""

__name__    = 'qom.ui.widgets.SidebarWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-01-22'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

# qom modules
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class SidebarWidget(BaseWidget):
    """Class to create a custom sidebar.

    Inherits :class:`qom.ui.widgets.BaseWidget`.
    
    Parameters
    ----------
    parent : QtWidget.*
        Parent class for the sidebar.
    widget : QtWidget.*
        Widget connected to the sidebar list.
    pos : str, optional
        Position of the sidebar:
            'bottom-left': Bottom-left side.
            'bottom-right': Bottom-right side.
            'left': Left side.
            'right': Right side.
            'top-left': Top-left side.
            'top-right': Top-right side.
    """

    def __init__(self, parent, widget, pos='left', name='List'):
        """Class constructor for SidebarWidget."""

        # initialize super class
        super().__init__(parent)

        # set parameters
        self.widget = widget
        self.pos = pos
        self.name = name

        # initialize layout
        self.__init_layout()

        # set list
        self.set_list(widget.get_list_items(), widget.set_curr_item)

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        list_width = 256
        icon_width = 32
        # full sidebar
        sidebar_height = 720 - 2 * 32
        icon_height = 128
        # top, middle or bottom sidebar
        if self.pos.find('-') != -1:
            if self.pos.find('middle') != -1:
                sidebar_height = 240 - 16
            else:
                sidebar_height = 240 - 32
            icon_height = 96

        # fix size
        self.setFixedSize(list_width + icon_width, sidebar_height)
        # top or full sidebar
        _y = 32
        # middle sidebar
        if self.pos.find('middle') != -1:
            _y = 240 + 8
        # bottom sidebar
        elif self.pos.find('bottom') != -1:
            _y = 480
        # move sidebar
        # right side
        if self.pos.find('right') != -1:
            self.move(1280 - list_width - icon_width, _y)
        # left side
        else:
            _y = 32 if self.pos.find('-') == -1 else 360
            self.move(0, _y)

        # list status
        self.list_hidden = False

        # initialize UI elements
        # list
        self.list = QtWidgets.QListWidget()
        self.list.setFixedSize(list_width - 32, sidebar_height)
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # list label
        self.lbl_list = RotatedLabel(text=self.name, pos=self.pos)
        self.lbl_list.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=True))
        self.lbl_list.setFixedSize(32, sidebar_height)
        self.lbl_list.setAlignment(QtCore.Qt.AlignCenter)
        # arrow button
        self.btn_arrow = QtWidgets.QPushButton()
        self.btn_arrow.setFixedSize(icon_width, icon_height)
        self.btn_arrow.clicked.connect(self.toggle_list)

        # update layout 
        layout = QtWidgets.QHBoxLayout()
        # right side
        if self.pos.find('right') != -1:
            layout.addWidget(self.btn_arrow)
            layout.addWidget(self.lbl_list)
            layout.addWidget(self.list)
        # left side
        else:
            layout.addWidget(self.list)
            layout.addWidget(self.lbl_list)
            layout.addWidget(self.btn_arrow)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def set_list(self, items, callback_func):
        """Method to set the list of items and the callback on item selection.

        Parameters
        ----------
        items : list
            List of items to populate.
        callback_func : function
            Function to call on item selection.
        """

        # set items 
        self.list.clear()
        self.list.addItems(items)

        # refined callback
        def item_clicked_cb(item):
            callback_func(self.list.currentIndex().row())
            self.toggle_list()

        # item selection changed
        self.list.itemClicked.connect(item_clicked_cb)

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
            if self.list_hidden == True and self.pos.find('right') != -1:
                self.btn_arrow.setIcon(self.get_icon('left_arrow_dark'))
            elif self.list_hidden == False and self.pos.find('left') != -1:
                self.btn_arrow.setIcon(self.get_icon('left_arrow_dark'))
            else:
                self.btn_arrow.setIcon(self.get_icon('right_arrow_dark'))
            # styles
            self.setStyleSheet(self.get_stylesheet('sidebar_light'))
        else:
            # icons
            if self.list_hidden == True and self.pos.find('right') != -1:
                self.btn_arrow.setIcon(self.get_icon('left_arrow_light'))
            elif self.list_hidden == False and self.pos.find('left') != -1:
                self.btn_arrow.setIcon(self.get_icon('left_arrow_light'))
            else:
                self.btn_arrow.setIcon(self.get_icon('right_arrow_light'))
            # styles
            self.setStyleSheet(self.get_stylesheet('sidebar_dark'))

        # update theme
        self.theme = theme

    def toggle_list(self):

        # frequently used variables
        list_width = 256
        icon_width = 32
        # top or full sidebar
        _y = 32
        # middle sidebar
        if self.pos.find('middle') != -1:
            _y = 240 + 8
        # bottom sidebar
        elif self.pos.find('bottom') != -1:
            _y = 480

        # hidden
        if self.list_hidden == True:
            # right side
            if self.pos.find('right') != -1:
                self.move(1280 - list_width - icon_width, _y)
            # left side
            else:
                self.move(0, _y)
        # not hidden
        else:
            # right side
            if self.pos.find('right') != -1:
                self.move(1280 - icon_width, _y)
            # left side
            else:
                self.move(- list_width, _y)

        # update list status
        self.list_hidden = not self.list_hidden
        # update icons
        self.set_theme(self.theme)

class RotatedLabel(QtWidgets.QLabel):

    def __init__(self, text='List', pos='left'):
        super().__init__()
        self.text = text
        self.pos = pos

    def paintEvent(self, event):
        _painter = QtGui.QPainter(self)
        if self.pos.find('left') != -1:
            _painter.translate(self.width() / 2 - 4, 16)
            _painter.rotate(90)
        else:
            _painter.translate(self.width() / 2 + 4, self.height() - 16)
            _painter.rotate(-90)
        _painter.drawText(0, 0, self.text)
        _painter.end()