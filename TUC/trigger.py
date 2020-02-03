"""
 @copyright Copyright (C) 2019 Intel Corporation
 @copyright Copyright (C) 2019 IOTech Ltd

 @license SPDX-License-Identifier: Apache-2.0

 @file trigger.py

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
from robot import rebot

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
    t_parser.add_argument("-p", "--profile", default=None, dest="profile", help="profile to use")
    t_parser.add_argument("--name", default=None, dest="name", help="Override the name of the top level test suite")

    sub_cmd = t_parser.add_subparsers(dest="sub_cmd")

    rebot_sub_cmd = sub_cmd.add_parser('rebot')
    rebot_sub_cmd.add_argument("--inputdir", default=None, dest="inputdir", help="where to fetch report files")
    rebot_sub_cmd.add_argument("--outputdir", default=None, dest="outputdir", help="where to create output files")

    return t_parser


def validate_args(args):
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


def setup_config(args):
    os.environ['WORK_DIR'] = WORK_DIR
    os.environ['PROFILE'] = args.profile

    # Read environment variable and store to SettingsInfo
    SettingsInfo().add_name('workDir', os.environ['WORK_DIR'])
    SettingsInfo().add_name('profile', os.environ['PROFILE'])

    # Read config file and store to SettingsInfo
    constant = __import__("TAF.config." + os.environ['PROFILE'] + ".configuration", fromlist=['configuration'])
    SettingsInfo().add_name('constant', constant)


def get_kwargs(args):
    kwargs = {
                "loglevel": args.logLevel,
                "outputdir": OUTPUTDIR,
                "output": OUTPUTDIR+"/"+"report.xml",
                "variable": ["WORK_DIR:{}".format(WORK_DIR), "PROFILE:{}".format(args.profile)]
    }

    if args.name:
        kwargs["name"] = args.name
    elif args.profile:
        kwargs["name"] = args.profile

    if args.profile:
        variable_file = "{}/{}/configuration.py".format(CONFIG_DIR, args.profile)
        kwargs["variablefile"] = variable_file

    if args.include:
        kwargs["include"] = args.include
    if args.exclude:
        kwargs["exclude"] = args.exclude
    return kwargs


def start():
    logging.basicConfig(level=logging.DEBUG)

    args = configure_parser().parse_args()

    if not args.sub_cmd:
        run_robot(args)

    if args.sub_cmd and args.sub_cmd == "rebot":
        run_rebot(args)


def run_robot(args):
    remove_old_report_folder()
    remove_old_logs()

    validate_args(args)

    logging.info("Run testing for profile '{0}'".format(args.profile))
    setup_config(args)
    kwargs = get_kwargs(args)

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


def run_rebot(args):
    logging.info("Run rebot for the '{0}' folder".format(args.inputdir))
    #  Aggregate testing reports
    files = glob.glob(args.inputdir+"/*.xml")
    rebot(*files, name="edgex", outputdir=args.outputdir, xunit="result.xml")
