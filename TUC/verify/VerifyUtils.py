"""
 @copyright Copyright (C) 2019 Intel Corporation

 @license SPDX-License-Identifier: Apache-2.0

 @package TUC.verify

 @file VerifyUtils.py

 @description
    Class that that contains verification functions.
"""
import time


class VerifyUtils(object):
    """
    Class that provides functions to verify if time lapsed has exceeded certain amount of time.
    """
    def __init__(self):
        pass

    def time_exceeded(self, tstart, tmax):
        """
        Build a closure that tests whether a given
        time exceeds a start time and a max time duration
        @param    self   represents the instance of the class.
        @param tstart start time
        @param tmax maximum time
        @retval t_exceed Pointer to function that will return False if time hasn't exceed maximum time or
        True if it has.
        """
        def t_exceed(t=None):
            t_taken = int(time.time()) - tstart
            if t_taken > tmax:
                return True
            else:
                return False

        return t_exceed

    def time_exceeded_extend(self, tstart, tmax):
        """
        Build a closure that tests whether a given
        time exceeds a start time and a max time duration
        @param    self   represents the instance of the class.
        @param tstart start time
        @param tmax maximum time
        @retval t_exceed Pointer to function that will return False if time hasn't exceed maximum time or
        True if it has and time remaining.
        """
        def t_exceed(t=None):
            t_taken = int(time.time()) - tstart
            if t_taken > tmax:
                return True, 0
            else:
                return False, tmax - t_taken

        return t_exceed
