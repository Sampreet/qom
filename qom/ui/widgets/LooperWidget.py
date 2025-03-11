#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Class to create a widget for the loopers."""

__name__    = 'qom.ui.widgets.LooperWidget'
__authors__ = ["Sampreet Kalita"]
__created__ = "2021-08-19"
__updated__ = "2025-03-08"

# dependencies
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

# qom modules
from ...loopers import XLooper, XYLooper, XYZLooper
from ...utils.loopers import wrap_looper, run_loopers_in_parallel
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

        # set attributes
        self.LooperClass = None
        self.LooperClasses = [XLooper, XYLooper, XYZLooper]
        self.solver_widget = solver_widget
        self.system_widget = system_widget
        self.plotter_widget = plotter_widget
        self.param_widgets = list()

        # initialize layout
        self.__init_layout()

    def __init_layout(self):
        """Method to initialize main layout."""
        
        # frequently used variables
        width = 640
        offset = 240
        row_height = 32
        padding = 32
        base_rows = 4
        axes_rows = 3

        # initialize grid layout 
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, padding, 0)

        # initialize function label
        self.lbl_name = QtWidgets.QLabel('Select Looper')
        self.lbl_name.setFixedSize(int(width / 4), row_height) 
        self.lbl_name.setFont(QtGui.QFont('Segoe UI', pointSize=12, italic=True))
        self.lbl_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.layout.addWidget(self.lbl_name, 0, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize type label
        self.lbl_func = QtWidgets.QLabel('Function:')
        self.lbl_func.setFixedSize(int(width / 2), row_height) 
        self.lbl_func.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_func, 0, 1, 1, 2, alignment=QtCore.Qt.AlignLeft)
        # initialize wrap check box
        self.chbx_parallel = QtWidgets.QCheckBox('Multiprocess')
        self.chbx_parallel.setFixedSize(int(width / 4), row_height)
        self.chbx_parallel.setDisabled(True)
        self.layout.addWidget(self.chbx_parallel, 0, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize wrap check box
        self.chbx_solver = QtWidgets.QCheckBox('Use Solver')
        self.chbx_solver.setFixedSize(int(width / 4), row_height)
        self.chbx_solver.stateChanged.connect(self.toggle_solver)
        self.chbx_solver.setDisabled(True)
        self.layout.addWidget(self.chbx_solver, 1, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize function combo box
        self.cmbx_func = QtWidgets.QComboBox()
        self.cmbx_func.setFixedSize(int(width / 2 - 1.5 * padding), row_height)
        self.cmbx_func.currentTextChanged.connect(self.set_curr_func)
        self.cmbx_func.setDisabled(True)
        self.layout.addWidget(self.cmbx_func, 1, 1, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize plot check box
        self.chbx_plot = QtWidgets.QCheckBox('Plot')
        self.chbx_plot.setFixedSize(int(width / 4), row_height)
        self.chbx_plot.setDisabled(True)
        self.layout.addWidget(self.chbx_plot, 1, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize wrap check box
        self.chbx_save = QtWidgets.QCheckBox('Save Data')
        self.chbx_save.setFixedSize(int(width / 4), row_height)
        self.chbx_save.stateChanged.connect(self.toggle_save)
        self.chbx_save.setDisabled(True)
        self.layout.addWidget(self.chbx_save, 2, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize cache path line edit
        self.le_path = QtWidgets.QLineEdit('')
        self.le_path.setPlaceholderText('file_path_prefix')
        self.le_path.setFixedSize(int(width / 2 - 1.5 * padding), row_height)
        self.le_path.setDisabled(True)
        self.layout.addWidget(self.le_path, 2, 1, 1, 2, alignment=QtCore.Qt.AlignRight)
        # initialize loop button
        self.btn_loop = QtWidgets.QPushButton('Loop')
        self.btn_loop.setFixedSize(int(width / 4 - 1.25 * padding), row_height)
        self.btn_loop.clicked.connect(self.loop)
        self.btn_loop.setDisabled(True)
        self.layout.addWidget(self.btn_loop, 2, 3, 1, 1, alignment=QtCore.Qt.AlignRight)
        # initialize variable label
        self.lbl_var = QtWidgets.QLabel('var')
        self.lbl_var.setFixedSize(int(width / 4), row_height)
        self.lbl_var.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_var, 3, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize minimum value label
        self.lbl_min = QtWidgets.QLabel('min')
        self.lbl_min.setFixedSize(int(width / 4), row_height)
        self.lbl_min.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_min, 3, 1, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize maximum value label
        self.lbl_max = QtWidgets.QLabel('max')
        self.lbl_max.setFixedSize(int(width / 4), row_height)
        self.lbl_max.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_max, 3, 2, 1, 1, alignment=QtCore.Qt.AlignLeft)
        # initialize dimension label
        self.lbl_dim = QtWidgets.QLabel('dim')
        self.lbl_dim.setFixedSize(int(width / 4), row_height)
        self.lbl_dim.setFont(QtGui.QFont('Segoe UI', pointSize=10, italic=False))
        self.layout.addWidget(self.lbl_dim, 3, 3, 1, 1, alignment=QtCore.Qt.AlignLeft)

        # initialize most useful parameters
        prefixes = ['x_', 'y_', 'z_']
        suffixes = ['var', 'min', 'max', 'dim']
        for row in range(axes_rows):
            for col in range(4):
                # initialize each widget
                widget = QtWidgets.QLineEdit('')
                widget.setPlaceholderText(str(prefixes[row]) + str(suffixes[col]))
                widget.setFixedSize(int(width / 4 - 1.25 * padding), row_height)
                widget.setDisabled(True)
                # update widget list
                self.param_widgets.append(widget)
                self.layout.addWidget(widget, base_rows + row, col, 1, 1, alignment=QtCore.Qt.AlignRight)

        # update main layout
        self.move(width, offset + 4)
        self.setFixedWidth(width)
        self.setFixedHeight((base_rows + axes_rows) * row_height)
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
        codes = list()

        # iterate through available loopers
        for LooperClass in self.LooperClasses:
            codes.append(LooperClass.name)

        return codes

    def loop(self):
        """Method to loop the variables."""

        # disable loop button
        self.btn_loop.setDisabled(True)

        # handle no system found
        if self.system_widget.SystemClass is None:
            # update status
            self.parent.update(status='No system found')
            return

        # handle no function found
        if self.cmbx_func.currentText() == 'NA':
            # update status
            self.parent.update(status='No function found')
            return
        
        # looper parameters
        params = dict()
        params['show_progress'] = True
        params['file_path_prefix'] = self.le_path.text() if self.chbx_save.isChecked() and self.le_path.text() != '' else None
        # extract axes parameters from widgets
        axes = ['X', 'Y', 'Z']
        keys = ['var', 'min', 'max', 'dim']
        for i in range(self.LooperClasses.index(self.LooperClass) + 1):
            params[axes[i]] = {}
            for j in range(4):
                params[axes[i]][keys[j]] = self.param_widgets[i * 4 + j].text()

        # function to loop
        global func
        if self.chbx_solver.isChecked():
            def func(system_params):
                system = self.system_widget.SystemClass(
                    params=system_params
                )
                solver = self.solver_widget.SolverClass(
                    params=self.solver_widget.get_params(),
                    system=system
                )
                return solver.solve()
        else:
            def func(system_params):
                system = self.system_widget.SystemClass(
                    params=system_params
                )
                _, _, c = system.get_ivc()
                return getattr(system, 'get_' + self.cmbx_func.currentText())(
                    c=c
                )

        # wrap looper
        looper_func = run_loopers_in_parallel if self.chbx_parallel.isChecked() else wrap_looper
        looper = looper_func(
            looper_name=self.LooperClass.name,
            func=func,
            params=params,
            params_system=self.system_widget.get_params(),
            plot=self.chbx_plot.isChecked(),
            params_plotter=self.plotter_widget.get_params() if self.chbx_plot.isChecked() else None,
            cb_update=self.parent.update
        )

        # enable loop button
        self.btn_loop.setEnabled(True)

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

        # enable loop button
        self.btn_loop.setEnabled(True)
        
        # if system is selected
        if self.system_widget.SystemClass is not None:
            # set data path
            data_dir = 'data/' + self.system_widget.SystemClass.__name__
            self.le_path.setText(data_dir + '/'+ (value if value != 'NA' else 'V'))

        # update footer
        self.parent.update(status='Ready', progress=None, reset=True)

    def set_curr_item(self, pos):
        """Method to set the current looper.
        
        Parameters
        ----------
        pos : int
            Position of the current looper.
        """

        # enable all widgets
        for idx in range(self.layout.count()):
            self.layout.itemAt(idx).widget().setEnabled(True)
        self.chbx_parallel.setDisabled(True)    # not supported on GUI
        self.toggle_save()
        self.toggle_solver()

        # update looper
        self.LooperClass = self.LooperClasses[pos]

        # update parameter widgets
        axes = ['x', 'y', 'z']
        for idx in range(len(self.param_widgets)):
            vals = [axes[int(idx / 4)], 0.0, 100.0, 1001]
            self.param_widgets[idx].setText('' if int(idx / 4) > pos else str(vals[idx % 4]))
            self.param_widgets[idx].setDisabled(True if int(idx / 4) > pos else False)

        # get combo box items
        cmbx_items = ['NA'] if self.system_widget.cmbx_func.count() == 0 or self.system_widget.cmbx_func.currentText() == 'NA' else [self.system_widget.cmbx_func.itemText(i) for i in range(self.system_widget.cmbx_func.count())]

        # update widget
        self.lbl_name.setText(self.LooperClass.desc)
        self.cmbx_func.clear()
        self.cmbx_func.addItems(cmbx_items)

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

    def toggle_solver(self):
        """Method to toggle solver functions."""
        self.cmbx_func.setDisabled(True if self.chbx_solver.isChecked() else False)

    def toggle_save(self):
        """Method to toggle save."""
        self.le_path.setDisabled(False if self.chbx_save.isChecked() else True)