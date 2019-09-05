"""
 @copyright Copyright (C) 2019 Intel Corporation
 @copyright Copyright (C) 2019 IOTech Ltd

 @license SPDX-License-Identifier: Apache-2.0

 @file run.py

 @description
     This file should execute at edgex-taf root directory, it allows testers to execute set(s) of testCases/useCases based on the parameters passed. It will create
     a report based on the results that can be published in a web server or can sent through email.

"""
import argparse
import glob
import logging
import os
import shutil
import sys
from robot import run

WORK_DIR = os.getcwd()
SCENARIOS_DIR = WORK_DIR + "/TAF/testScenarios/"
ARTIFACTS_DIR = WORK_DIR + "/TAF/testArtifacts/"
CONFIG_DIR = WORK_DIR + "/TAF/config/"
OUTPUTDIR = ARTIFACTS_DIR + "/reports/edgex"
VERSION = "1.0"
RUNLEVEL = "INFO"

sys.path.append(WORK_DIR)
sys.path.append(WORK_DIR + "/edgex-taf-common")

from TUC.data.SettingsInfo import SettingsInfo

def error(msg):
    """
    This function logs an error message and end the execution.

    @param msg  Message to be displayed before stopping test execution.
    """
    sys.stderr.write(msg + "\r\n")
    sys.exit()


def configure_parser():
    """
    This method is the console log parser

    @retval t_parser  Returns TAF Parser
    """
    t_parser = argparse.ArgumentParser(description="TAF test Runner")
    t_parser.add_argument("-u", "--useCase", action="append", default=None, dest="useCase", help="specify UC")
    t_parser.add_argument("-t", "--testCase", action="append", default=None, dest="testCase", help="specify TestCase")
    t_parser.add_argument("-i", "--include", action="append", default=None, dest="include", help="Tags to include")
    t_parser.add_argument("-e", "--exclude", action="append", default=None, dest="exclude", help="Tags to exclude")
    t_parser.add_argument("-L", "--loglevel", choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "NONE"],
                          default=RUNLEVEL, dest="logLevel", help="Tags to exclude")
    t_parser.add_argument("--version", "-v", action="version", version="%(prog)s {0}".format(VERSION))
    t_parser.add_argument("-p", "--profile", default="default", dest="profile", help="profile to use")
    return t_parser


def validate_args():
    """
    Validate arguments received.
    """
    if args.useCase and args.testCase:
        error("Can only specify one useCase or testCase", 1)
    elif not (args.useCase or args.testCase):
        error("Need at least one useCase or testCase", 2)


def remove_old_logs():
    files = glob.glob(ARTIFACTS_DIR + "logs/*.log")
    for f in files:
        os.remove(f)


def remove_old_report_folder():
    if os.path.isdir(OUTPUTDIR):
        shutil.rmtree(OUTPUTDIR)


def setup_config():
    os.environ['WORK_DIR'] = WORK_DIR
    os.environ['PROFILE'] = args.profile

    # Read environment variable and store to SettingsInfo
    SettingsInfo().add_name('workDir', os.environ['WORK_DIR'])
    SettingsInfo().add_name('profile', os.environ['PROFILE'])

    # Read config file and store to SettingsInfo
    constant = __import__("TAF.config." + os.environ['PROFILE'] + ".configuration", fromlist=['configuration'])
    SettingsInfo().add_name('constant', constant)


def get_kwargs():
    variable_file = "{}/{}/configuration.py".format(CONFIG_DIR, args.profile)
    kwargs = {
                "name": "EdgeX", "loglevel": args.logLevel,
                "outputdir": OUTPUTDIR, "variablefile": variable_file,
                "variable": ["WORK_DIR:{}".format(WORK_DIR), "PROFILE:{}".format(args.profile)]
    }
    if args.include:
        kwargs["include"] = args.include
    if args.exclude:
        kwargs["exclude"] = args.exclude
    return kwargs


if __name__ == "__main__":
    remove_old_report_folder()
    remove_old_logs()

    logging.basicConfig(level=logging.DEBUG)

    args = configure_parser().parse_args()
    validate_args()
    setup_config()
    kwargs = get_kwargs()

    # Run testing
    os.chdir(SCENARIOS_DIR)
    if args.useCase and ('*' in args.useCase or '.' in args.useCase):
        logging.info("Running use case {0}".format(args.useCase))
        run('.', **kwargs)
    elif args.useCase:
        logging.info("Running use case {0}".format(args.testCase))
        run(*args.useCase, **kwargs)

    if args.testCase:
        logging.info("Running test case {0}".format(args.testCase))
        run(*args.testCase, **kwargs)
