#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a custom sidebar."""

__name__    = 'qom.ui.widgets.SidebarWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-01-21'
__updated__ = '2021-08-25'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

# qom modules
from . import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class SidebarWidget(BaseWidget):
    """Class to create a custom sidebar.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the sidebar.
    widget : :class:`qom.ui.widgets.*`
        Widget connected to the sidebar list.
    pos : str, optional
        Position of the sidebar:
            ==============  ==================
            value           meaning
            ==============  ==================
            "bottom-left"   bottom-left side.
            "bottom-right"  bottom-right side.
            "center-left"   center-left side.
            "center-right"  center-right side.
            "left"          left side.
            "right"         right side.
            "top-left"      top-left side.
            "top-right"     top-right side.
            ==============  ==================
    name : str, optional
        Name of the list.
    """

    def __init__(self, parent, widget, pos='left', name='Sidebar List'):
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
        # top, center or bottom sidebar
        if self.pos.find('-') != -1:
            if self.pos.find('center') != -1:
                sidebar_height = 240 - 16
            else:
                sidebar_height = 240 - 32
            icon_height = 96

        # fix size
        self.setFixedSize(list_width + icon_width, sidebar_height)
        # top or full sidebar
        _y = 32
        # center sidebar
        if self.pos.find('center') != -1:
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

    def toggle_list(self):

        # frequently used variables
        list_width = 256
        icon_width = 32
        # top or full sidebar
        _y = 32
        # center sidebar
        if self.pos.find('center') != -1:
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
    """Class to paint a label rotated by 90 degrees.
    
    Parameters
    ----------
    text : str, optional
        Text to paint.
    pos : str, optional
        Position of the sidebar:
            ==============  ==================
            value           meaning
            ==============  ==================
            "bottom-left"   bottom-left side.
            "bottom-right"  bottom-right side.
            "center-left"   center-left side.
            "center-right"  center-right side.
            "left"          left side.
            "right"         right side.
            "top-left"      top-left side.
            "top-right"     top-right side.
            ==============  ==================

    """

    def __init__(self, text='List', pos='left'):
        """Class constructor for RotatedLabel."""

        # initialize super class
        super().__init__()

        # update attributes
        self.text = text
        self.pos = pos

    def paintEvent(self, event):
        """Method to paint the rotated label.
        
        event : :class:`QGui.QPaintEvent`
            Paint event.
        """

        # initialize painter
        _painter = QtGui.QPainter(self)

        # if sidebar is on the left side
        if self.pos.find('left') != -1:
            # rotate counter-clockwise
            _painter.translate(self.width() / 2 - 4, 16)
            _painter.rotate(90)
        else:
            # rotate clockwise
            _painter.translate(self.width() / 2 + 4, self.height() - 16)
            _painter.rotate(-90)
        
        # draw text
        _painter.drawText(0, 0, self.text)
        _painter.end()