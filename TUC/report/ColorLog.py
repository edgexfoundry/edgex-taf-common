"""
 @copyright Copyright (C) 2019 Intel Corporation

 @license SPDX-License-Identifier: Apache-2.0

 @package TUC.report

 @file ColorLog.py

 @description
    Log class that logs level by color
"""
import sys
import logging
import traceback


class ColorLog:

    """
    Log class that logs level by color

    @class ColorLog

    Uses ANSI defined color formatting codes
    """

    ##  Blue bold
    HEADER = '\033[95m'
    ##  Blue
    OKBLUE = '\033[94m'
    ## Green
    OKGREEN = '\033[92m'
    ## Light Red
    WARNING = '\033[93m'
    ## RED
    ERROR = '\033[91m'
    ## Ends previous coloring
    ENDC = '\033[0m'
    ## BOLD
    BOLD = '\033[1m'
    ## DEBUG
    DEBUG = '\33[30m\033[47m'
    ## UNDERLINE
    UNDERLINE = '\033[4m'

    ## python self._backgroundlogger object
    logger = None

    def __init__(self, filename="log.log", strfmt='[%(asctime)s] %(levelname)-8s: %(message)s', lvl=logging.INFO, logName=None, useBackGroundLogger=True):
        """
        class constructor

        @param    filename    the log filename

        @param    strfmt    the format to use

        @param    lvl    default log level

        @return    object    ColorLog object

        """
        if logName:
            self.logger = logging.getLogger(logName)
        else:
            self.logger = logging.getLogger()
        self.bgnLog = useBackGroundLogger
        if useBackGroundLogger:
            from robotbackgroundlogger import BackgroundLogger
            self._backgroundlogger = BackgroundLogger()

        if logName is None and self.logger.handlers:
            self.logger.handlers = []

        if logName is None:
            logging.basicConfig(format=strfmt, level=lvl, datefmt='%Y-%m-%d %I:%M:%S %p')
            self.lhStdout = self.logger.handlers[0]
            self.logger.removeHandler(self.lhStdout)
            if self.logger.handlers:
                self.logger.handlers = []

        self.fh = logging.FileHandler(filename)
        self.fh.setFormatter(logging.Formatter(fmt=strfmt, datefmt='%m/%d/%Y %H:%M:%S'))
        self.fh.setLevel(logging.DEBUG)
        self.logger.addHandler(self.fh)

        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.ERROR)
        self.logger.addHandler(self.ch)

    def debug(self, text):
        """
        log text at log level 'info'

        @param    text    the text to log

        """
        self.logger.debug(self.DEBUG+str(text)+self.ENDC)
        if self.bgnLog:
            self._backgroundlogger.debug(text)

    def info(self, text):
        # type: (object) -> object
        """
        log text at log level 'info'

        @param    text    the text to log

        """
        self.logger.info(text)
        if self.bgnLog:
            self._backgroundlogger.info(text)

    def warn(self, text):
        """
        log text at log level 'warn'

        @param    text    the text to log

        """
        self.logger.warning(self.WARNING + text + self.ENDC)
        if self.bgnLog:
            self._backgroundlogger.warn(text)

    def error(self, text):
        """
        log text at log level 'error'

        @param    text    the text to log

        """
        self.logger.error(self.ERROR + text + self.ENDC)
        if self.bgnLog:
            self._backgroundlogger.error(text)

    def log_exception(self, name):
        """
        log exception at log level error

        @param    name    the name to prepend

        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        self.error(name.join(' ' + line for line in lines))
        if self.bgnLog:
            self._backgroundlogger.error(name.join(' ' + line for line in lines))

    def PASS(self, text):
        """
        log text at log level 'PASS' meaning the test passed

        @param    text    the text to log

        """
        self.logger.info(self.OKGREEN + self.UNDERLINE + text + self.ENDC)
        if self.bgnLog:
            self._backgroundlogger.info(text)

    def FAIL(self, text):
        """
        log text at log level 'FAIL' meaning the test failed

        @param    text    the text to log

        """
        self.logger.error(self.ERROR + text + self.ENDC)
        if self.bgnLog:
            self._backgroundlogger.error(text)

    def HEADING(self, text):
        """
        log text at log level 'HEADING' meaning the text is blue

        @param    text    the text to log

        """
        self.logger.info(self.OKBLUE + text + self.ENDC)
        if self.bgnLog:
            self._backgroundlogger.info(text)

    def setConfig(self, fmt):
        """
        set the format configuration

        @param    fmt    the log format

        """
        self.logger.basicConfig(format=fmt)

    def close(self):
        """
        close the log

        """
        self.logger.removeHandler(self.fh)
        self.fh.close()
        self.logger.removeHandler(self.ch)
        self.ch.close()

    def log_background(self):
        """
        Write background log
        """
        if self.bgnLog:
            self._backgroundlogger.log_background_messages()

    def setLevel(self,lvl):
        """
        Set Level for logger
        @param   lvl   logging level
        """
        self.logger.setLevel(lvl)
