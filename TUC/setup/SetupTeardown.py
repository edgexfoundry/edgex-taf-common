"""
@copyright Copyright (C) 2025 IOTech Ltd
@license SPDX-License-Identifier: Apache-2.0

@package TUC.setup

@file SetupTeardown.py

@description
    This file includes default setup and teardown routines called by robot to setup and teardown
    the test suite.
"""

import sys
import logging

from TUC.report.ColorLog import ColorLog
from TUC.trigger import ARTIFACTS_LOGS_DIR
from TUC.data.SettingsInfo import SettingsInfo

_STANZA = "*" * 50
_SML_STANZA = "*" * 12


def suite_setup(suite_name, logfile=None, loglevel="DEBUG"):
    """
    Suite_Setup sets up the test cases

    Gets the log and config and puts them in the SettingsInfo object

    The API between Robot and this script is that this script
    return True or False.  The policy here is catch exceptions,
    log them, and return False to Robot.

    @param suite_name:   required suite name
    @param logfile:   sets logfile, if empty, sets to {ARTIFACTS_LOGS_DIR}/{suite_name}.log
    @param loglevel:  sets loglevel
    @return: True if all code was executed successfully.
    """
    tc_name = "Suite Setup:"

    # Setup logger
    logging.getLogger().setLevel(loglevel)
    if not logfile:
        logfile = f"{ARTIFACTS_LOGS_DIR}/{suite_name}.log"
    test_log = ColorLog(
        filename=logfile, lvl=loglevel, logName=suite_name, useBackGroundLogger=False
    )

    loglvl = logging.getLogger().getEffectiveLevel()
    _print_log_header(test_log)
    test_log.info(
        "{} Logging started, level: {}".format(tc_name, logging.getLevelName(loglvl))
    )
    test_log.info("{} python version: {}".format(tc_name, sys.version))
    test_log.info("Suite Name: {}".format(suite_name))
    SettingsInfo().add_name("TestLog", test_log)
    return True


def suite_teardown():
    """
    Teardown the suite:
        print footer
        close the log file

    @retval True returned to robot
    """
    testLog = SettingsInfo().TestLog
    testLog.info("Suite Teardown")

    _print_log_footer(testLog)
    testLog.close()

    return True


def _print_log_header(log):
    """
    print log header
    @param     log     Logger object
    """
    log.info("{}".format(_STANZA))
    log.info("{}".format(_STANZA))
    log.info("{}{}{}".format(_SML_STANZA, "  TEST RUN START  ", _SML_STANZA))


def _print_log_footer(log):
    """
    print log footer
    @param     log     Logger object
    """
    log.info("{}{}{}".format(_SML_STANZA, "    TEST RUN END  ", _SML_STANZA))
    log.info("{}".format(_STANZA))
    log.info("{}".format(_STANZA))
