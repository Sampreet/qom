#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the loopers."""

__name__    = 'qom.ui.widgets.LooperWidget'
__authors__ = ['Sampreet Kalita']
__created__ = '2021-08-19'
__updated__ = '2021-08-23'

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import os

# qom modules
from ...loopers import *
from ...utils.looper import *
from .BaseWidget import BaseWidget

# module logger
logger = logging.getLogger(__name__)

class LooperWidget(BaseWidget):
    """Class to create a widget for the loopers.
    
    Parameters
    ----------
    parent : :class:`qom.ui.GUI`
        Parent class for the widget.
    solver_widget : :class:`qom.ui.widgets.SolverWidget`
        Solver widget.
    system_widget : :class:`qom.ui.widgets.SystemWidget`
        System widget.
    plotter_widget : :class:`qom.ui.widgets.PlotterWidget`
        Plotter widget.
    """

    def __init__(self, parent, solver_widget, system_widget, plotter_widget):
        """Class constructor for LooperWidget."""

        # initialize super class
        super().__init__(parent)
        self.looper = None
        self.param_widgets = list()
        self.solver_widget = solver_widget
        self.system_widget = system_widget
        self.plotter_widget = plotter_widget

        # initialize layout
        self.__init_layout()

        # set loopers
        self.loopers = [XLooper, XYLooper, XYZLooper]

    def __init_layout(self):
        """Method to initialize layout."""
        
        # frequently used variables
        width = 640
        height = 240
        row_height = 32
        padding = 32

        # fix size
        self.setFixedWidth(width)
        # set as central widget on the right with margin
        self.move(width, height + 4)

        # initialize UI elements
        # looper label
        self.lbl_name = QtWidgets.QLabel('Select a looper to begin')
        self.lbl_name.setFixedSize(width, row_height)
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        # function combo box
        self.cmbx_func = QtWidgets.QComboBox()
        self.cmbx_func.setFixedSize(width / 2 - 1.5 * padding, row_height)
        self.cmbx_func.currentTextChanged.connect(self.set_curr_func)
        self.cmbx_func.setVisible(False)
        # wrap check box
        self.chbx_wrap = QtWidgets.QCheckBox('Wrap')
        self.chbx_wrap.setFixedSize(width / 4, row_height)
        self.chbx_wrap.setVisible(False)
        # plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot')
        self.chbx_plot.setFixedSize(width / 4, row_height)
        self.chbx_plot.setVisible(False)
        # file path line edit
        self.le_path = QtWidgets.QLineEdit('')
        self.le_path.setFixedSize(width / 2 - 1.5 * padding, row_height)
        self.le_path.setVisible(False)
        # mode combo box
        self.cmbx_mode = QtWidgets.QComboBox()
        self.cmbx_mode.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.cmbx_mode.addItems(['serial', 'multithread'])
        self.cmbx_mode.setVisible(False)
        # loop button
        self.btn_loop = QtWidgets.QPushButton('Loop')
        self.btn_loop.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.btn_loop.clicked.connect(self.loop)
        self.btn_loop.setVisible(False)
        # variable label
        self.lbl_var = QtWidgets.QLabel('var')
        self.lbl_var.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_var.setVisible(False)
        # minimum value label
        self.lbl_min = QtWidgets.QLabel('min')
        self.lbl_min.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_min.setVisible(False)
        # maximum value label
        self.lbl_max = QtWidgets.QLabel('max')
        self.lbl_max.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_max.setVisible(False)
        # dimension label
        self.lbl_dim = QtWidgets.QLabel('dim')
        self.lbl_dim.setFixedSize(width / 4 - 1.25 * padding, row_height)
        self.lbl_dim.setVisible(False)

        # update layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.lbl_name, 0, 0, 1, 4)
        self.layout.addWidget(self.cmbx_func, 1, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.chbx_wrap, 1, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.chbx_plot, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.le_path, 2, 0, 1, 2, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.cmbx_mode, 2, 2, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.btn_loop, 2, 3, 1, 1, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lbl_var, 3, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.lbl_min, 3, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.lbl_max, 3, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.lbl_dim, 3, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, padding, 0)
        self.setLayout(self.layout)

        # set theme
        self.theme = 'dark'
        self.set_theme()

    def get_list_items(self):
        """Method to obtain the names of available loopers.
        
        Returns
        -------
        codes : list
            Codenames of the loopers.
        """

        # initialize lists
        codes = ['x_looper', 'xy_looper', 'xyz_looper']

        return codes

    def loop(self):
        """Method to loop the variables."""

        # disable loop button
        self.btn_loop.setDisabled(True)

        # handle no function found
        if self.cmbx_func.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return
        
        # get function
        func = get_looper_func(self.system_widget.system, {}, self.cmbx_func.currentText())
        # extract axes parameters from widgets
        looper_params = dict()
        axes = ['X', 'Y', 'Z']
        keys = ['var', 'min', 'max', 'dim']
        for i in range(int(len(self.param_widgets) / 4)):
            looper_params[axes[i]] = {}
            for j in range(4):
                looper_params[axes[i]][keys[j]] = self.param_widgets[i * 4 + j].text()

        # get file path to save/load data
        path_text = self.le_path.text()
        file_path = path_text if path_text != '' else None

        # initialize looper
        looper = self.looper(func=func, params={
            'looper': looper_params,
            'solver': self.solver_widget.get_params(),
            'system': self.system_widget.get_params(),
            'plotter': self.plotter_widget.get_params()
        }, cb_update=self.parent.update)

        # run looper on main thread
        looper.wrap(file_path=file_path, plot=True)

        # enable loop button
        self.btn_loop.setDisabled(False)

    def set_curr_func(self, value):
        """Method to update the widget when combo box selection changes.
        
        Parameters
        ----------
        value : str
            New text of the combo box.
        """

        # frequently used variables
        axes = ['X', 'Y', 'Z']
        keys = ['var', 'min', 'max', 'dim']
        expr = ['v=' + value + '.py', 'x=', 'y=', 'z=']

        # enable button
        self.btn_loop.setDisabled(False)

        # handle no function found
        if self.cmbx_func.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return

        # set data file path
        system_code = self.system_widget.system({}).code if self.system_widget.system is not None else 'sys'
        self.le_path.setText('data/' + system_code + '/' + value)

        # update parameters
        params = {}
        # search script name by matching looper dimension
        found = lambda name, dim: sum([0 if name.find(e) == -1 else 1 for e in expr[:dim + 1]]) == dim + 1 and sum([0 if name.find(e) == -1 else 1 for e in expr]) == dim + 1
        # search scripts
        for script_name in os.listdir('scripts'):
            # if script found
            if found(script_name, self.loopers.index(self.looper) + 1):
                # read lines
                with open('scripts/' + script_name) as script_file:
                    lines = script_file.readlines()
                    line_start = 0
                    param_lines = ''
                    for i in range(len(lines)):
                        if lines[i].find('params = ') == 0:
                            line_start = i
                    for i in range(line_start, len(lines)):
                        param_lines += lines[i]
                        if lines[i].find('}') == 0:
                            break
                    # evaluate to dictionary
                    params = eval(param_lines[9:])
                    # close file
                    script_file.close()
                    
        # update looper parameters
        if 'looper' in params:
            for i in range(int(len(self.param_widgets) / 4)):
                for j in range(4):
                    if keys[j] in params['looper'][axes[i]]:
                        self.param_widgets[i * 4 + j].setText(str(params['looper'][axes[i]][keys[j]])) 
        # update system parameters
        if 'system' in params:
            self.system_widget.set_params(params=params['system'])
        # update plotter parameters
        if 'plotter' in params:
            self.plotter_widget.set_params(params=params['plotter'])

        # update footer
        self.parent.update(status='Ready', progress=None, reset=True)

    def set_curr_item(self, pos):
        """Method to set the current looper.
        
        Parameters
        ----------
        pos : int
            Position of the current looper.
        """

        # frequently used parameters
        width = 640
        row_height = 32
        pre_count = 4
        padding = 32
        base_height = pre_count * row_height

        # update parameter
        self.looper = self.loopers[pos]

        # clear widgets
        for widget in self.param_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
            
        # reset list
        self.param_widgets = list()

        # get combo box items
        cmbx_items = ['NA'] if self.system_widget.cmbx_func.count() == 0 or self.system_widget.cmbx_func.currentText() == 'NA' else [self.system_widget.cmbx_func.itemText(i) for i in range(self.system_widget.cmbx_func.count())]

        # # get wrapped functions
        # default_looper_func_names_dict = importlib.import_module('qom.utils.looper', '*').__dict__.get('default_looper_func_names_dict')
        # cmbx_items += [key for key in default_looper_func_names_dict]

        # update layout
        widget_col = pre_count * 4
        for _ in range(pos + 1):
            for j in range(4):
                widget = QtWidgets.QLineEdit('')
                widget.setFixedSize(width / 4 - 1.25 * padding, row_height)
                self.param_widgets.append(widget)
                self.layout.addWidget(widget, int(widget_col / 4), int(widget_col % 4) + j, 1, 1, alignment=QtCore.Qt.AlignRight)
            # update count
            widget_col += 4

        # update UI elements
        self.lbl_name.setText('Looper Function:')
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_items)
        self.cmbx_func.setVisible(True)
        self.chbx_wrap.setVisible(True)
        self.cmbx_mode.setVisible(True)
        self.le_path.setVisible(True)
        self.chbx_plot.setVisible(True)
        self.btn_loop.setVisible(True)
        self.lbl_var.setVisible(True)
        self.lbl_min.setVisible(True)
        self.lbl_max.setVisible(True)
        self.lbl_dim.setVisible(True)
        self.setFixedHeight(base_height + int((widget_col - pre_count * 4 + 1) / 4) * row_height)

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