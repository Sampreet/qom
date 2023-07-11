#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""Module for miscellaneous IO operations."""

__name__ = 'qom.io'
__authors__ = ["Sampreet Kalita"]
__created__ = "2023-05-28"
__updated__ = "2023-07-06"

# dependencies
import numpy as np
import os
import time

class Updater():
    r"""Class to update the logs and progress callbacks.

    Initializes `logger` and `cb_update`.

    Parameters
    ----------
    logger : :class:`logging.logger`
        Module logger.
    cb_update : callable, optional
        Callback function to update status and progress, formatted as `cb_update(status, progress, reset)`, where `status` is a string, `progress` is a float and `reset` is a boolean.
    parallel : bool, default=False
        Option to format outputs when running in parallel.
    p_index : int, default=0
        Index of the process.
    p_start : float, optional
        Time at which the process was started. If not provided, the value is initialized to current time.
    """

    def __init__(self, logger, cb_update, parallel:bool=False, p_index:int=0, p_start:float=None):
        """Class constructor for Updater."""

        # set constants
        self.logger = logger
        self.cb_update = cb_update
        self.parallel = parallel
        self.p_index = p_index
        self.p_start = p_start

        # timer
        self.time = time.time()

    def update_info(self, status:str):
        """Method to update status information.
        
        Parameters
        ----------
        status : str
            Status information.
        """

        if not self.parallel:
            # update console
            self.logger.info(status + "\t\n")
            # update callback
            if self.cb_update is not None:
                self.cb_update(status=status, progress=None, reset=True)

    def update_debug(self, message:str):
        """Method to update debug message.
        
        Parameters
        ----------
        message : str
            Debug message.
        """

        if not self.parallel:
            # update console
            self.logger.debug(message)

    def update_progress(self, pos:int, dim:int, status:str, reset:bool):
        """Method to update progress.
        
        Parameters
        ----------
        pos : int
            Index of current iteration.
        dim : int
            Total number of iterations.
        status : str
            Status information.
        reset : bool
            Option to reset the console or callback.
        """
        
        # calculate progress
        if dim > 1 and pos is not None:
            progress = float(pos) / float(dim - 1) * 100.0
        else:
            progress = float(pos) / float(dim) * 100.0 if pos is not None else 0.0

        # handle status
        status = status if status is not None else ""

        # current time
        _time = time.time() 

        # display progress
        _init_or_comp = reset or progress == 100.0
        if _time - self.time > 1.0 or _init_or_comp or pos is None:
            # update console if parallel
            if self.parallel:
                if not reset:
                    _time_elapsed = _time - self.p_start
                    self.logger.info("\r{:0.3f}s\t".format(_time_elapsed) + ("\t" if _time_elapsed < 100.0 else "") + "\t\t" * self.p_index + "{:0.2f}%".format(progress))
            # else update both console and callback
            else:
                _progress = ": Progress = " + (("  " if progress < 10.0 else " ") if progress < 100.0 else "")
                # update console
                self.logger.info((status + _progress + "{:3.2f}%\t".format(progress)) if pos is not None else (status + ("\t\n" if reset else "\t")))
                # update callback
                if self.cb_update is not None:
                    self.cb_update(status=status, progress=progress if pos is not None else None, reset=reset)

            # update time
            self.time = _time
        
    def create_directory(self, file_path:str):
        """Method to update the directory of the data file.
        
        Parameters
        ----------
        file_path : str
            Full path of the file.
        """

        # get directory
        file_dir = file_path[:len(file_path) - len(file_path.split('/')[-1])]
        # try to create
        try:
            os.makedirs(file_dir)
            # update log
            self.update_debug(
                message="Directory {dir_name} created\n".format(dir_name=file_dir)
            )  
        # if already exists
        except FileExistsError:
            # update log
            self.update_debug(
                message="Directory {dir_name} already exists\n".format(dir_name=file_dir)
            )
    
    def exists(self, file_path:str):
        """Function to validate the data file.

        If a file with an `'.npy'` extension is found, the same is converted to `'.npz'`.
        
        Parameters
        ----------
        file_path : str
            Full path of the file.

        Returns
        -------
        exists : bool
            Whether the file exists.
        """

        if os.path.isfile(file_path + '.npz'):
            return True
        elif os.path.isfile(file_path + '.npy'):
            # load data
            _temp = np.load(file_path + '.npy')
            # save to compressed file
            np.savez_compressed(file_path, _temp)
            return True
        return False    
        
    def load(self, file_path:str):
        """Function to load from a data file.
        
        Parameters
        ----------
        file_path : str
            Full path of the file.

        Returns
        -------
        array : numpy.ndarray
            Data loaded from the file.
        """

        return np.load(file_path + '.npz')['arr_0']
            
    def save(self, file_path:str, array):
        """Function to save to a data file.
        
        Parameters
        ----------
        file_path : str
            Full path of the file.
        array : numpy.ndarray
            Data to save to the file.
        """

        np.savez_compressed(file_path, array)