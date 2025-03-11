#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to interface PyQt widgets."""

__name__    = 'qom.ui.widgets.BaseWidget'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-01-21"
__updated__ = "2025-03-08"

# dependencies
from PyQt5 import QtGui, QtWidgets
import logging
import pkgutil

# module logger
logger = logging.getLogger(__name__)

class BaseWidget(QtWidgets.QWidget):
    """Class to interface PyQt widgets.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the widget.
    """

    def __init__(self, parent):
        """Class constructor for BaseWidget."""

        # initialize super class
        super().__init__(parent)
        self.parent = parent

    def get_icon(self, filename):
        """Method to obtain icon from resource file.
        
        Parameters
        ----------
        filename : str
            Name of the resource file (without the extension).

        Returns
        -------
        icon : :class:`QtGui.QIcon`
            PyQt-compatible icon.
        """

        # initialize pixmap
        pmap = QtGui.QPixmap()
        # load file as bytes
        pmap.loadFromData(pkgutil.get_data(__name__, 'icons/' + filename + '.png'))

        # convert to icon
        icon = QtGui.QIcon(pmap)

        return icon

    def get_stylesheet(self, filename):
        """Method to obtain a stylesheet from resource file.
        
        Parameters
        ----------
        filename : str
            Name of the resource file without the extension.

        Returns
        -------
        ss : str
            Decoded stylesheet.
        """

        # get stylesheet as byte array
        _bytes = pkgutil.get_data(__name__, 'stylesheets/' + filename + '.ss')
        # decode stylesheet
        ss = _bytes.decode('utf-8')

        return ss