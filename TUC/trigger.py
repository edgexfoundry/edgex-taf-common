"""
@copyright Copyright (C) 2019 Intel Corporation
@copyright Copyright (C) 2019-2025 IOTech Ltd

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
SCENARIOS_DIR = WORK_DIR + "/TAF/testScenarios"
CONFIG_DIR = WORK_DIR + "/TAF/config"
DEFAULT_CONFIG_SUBDIR = "default"
ARTIFACTS_DIR = WORK_DIR + "/TAF/testArtifacts"
ARTIFACTS_LOGS_DIR = ARTIFACTS_DIR + "/logs"
ARTIFACTS_REPORTS_DIR = ARTIFACTS_DIR + "/reports"
LOG_LEVEL = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "NONE"]
INFO_LOG_LEVEL = "INFO"

sys.path.append(WORK_DIR)
sys.path.append(WORK_DIR + "/edgex-taf-common")

from TUC.data.SettingsInfo import SettingsInfo


def start():
    logging.basicConfig(level=logging.DEBUG)

    args = configure_parser().parse_args()

    if not args.sub_cmd:
        run_robot(args)

    if args.sub_cmd and args.sub_cmd == "rebot":
        run_rebot(args)


def configure_parser():
    """
    This method is the console log parser

    @retval t_parser  Returns TAF Parser
    """
    t_parser = argparse.ArgumentParser(description="TAF test Runner")
    t_parser.add_argument(
        "-t",
        "--testPath",
        action="append",
        metavar="<dir_or_file>",
        default=None,
        dest="testPath",
        help="Specify test files or directories [default:{}].".format(SCENARIOS_DIR),
    )
    t_parser.add_argument(
        "-i",
        "--include",
        action="append",
        metavar="<tag>",
        default=None,
        dest="include",
        help="Include tests with this tag.",
    )
    t_parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        metavar="<tag>",
        default=None,
        dest="exclude",
        help="Exclude tests with this tag.",
    )
    t_parser.add_argument(
        "-cd",
        "--configDir",
        metavar="<dir>",
        default=DEFAULT_CONFIG_SUBDIR,
        dest="configDir",
        help="Specify a configuration directory to use (relative to the config directory:{}) [default:{}].".format(
            CONFIG_DIR, DEFAULT_CONFIG_SUBDIR
        ),
    )
    t_parser.add_argument(
        "-d",
        "--outputDir",
        metavar="<dir>",
        default=None,
        dest="outputDir",
        help="Specify output directory (relative to the report directory:{}).".format(
            ARTIFACTS_REPORTS_DIR
        ),
    )
    t_parser.add_argument(
        "-o",
        "--output",
        metavar="<name>",
        default=None,
        dest="outputName",
        help="Specify the base name for the outputs (relative to the output directory) By default, the outputs will be 'report.xml', 'log.html' and 'report.html'.",
    )
    t_parser.add_argument(
        "-l",
        "--logLevel",
        metavar="<log_level>",
        choices=LOG_LEVEL,
        default=INFO_LOG_LEVEL,
        dest="logLevel",
        help="Specify log level (valid log level:{}) [default:{}].".format(
            LOG_LEVEL, INFO_LOG_LEVEL
        ),
    )
    t_parser.add_argument(
        "-n",
        "--name",
        metavar="<name>",
        default=None,
        dest="name",
        help="Override the name of the top level test suite.",
    )
    t_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable cleanup of previous log and report files. By default, cleanup is performed unless this flag is set.",
    )

    sub_cmd = t_parser.add_subparsers(title="subcommands", dest="sub_cmd")
    rebot_sub_cmd = sub_cmd.add_parser("rebot")
    rebot_sub_cmd.add_argument(
        "inputdir", default=None, help="Where to fetch report files"
    )
    rebot_sub_cmd.add_argument(
        "outputdir", default=None, help="Where to create output files"
    )
    rebot_sub_cmd.add_argument(
        "--title", metavar="<title>", default="edgex", help="Report and log titles"
    )

    return t_parser


def run_robot(args):
    if not args.testPath:
        args.testPath = ["*"]

    logging.info("Running tests {}".format(args.testPath))

    if not args.no_cleanup:
        remove_old_report_folder(args.outputDir)
        remove_old_logs()

    logging.info("Run testing with config dir '{}'".format(args.configDir))
    setup_config(args)

    # Prepare **options for robot.run()
    kwargs = get_kwargs(args)
    os.chdir(SCENARIOS_DIR)
    logging.debug("Executing tests with arguments: {}".format(kwargs))
    if "*" in args.testPath or "." in args.testPath:
        run(".", **kwargs)
    else:
        run(*args.testPath, **kwargs)


def run_rebot(args):
    logging.info("Run rebot for the '{}' folder".format(args.inputdir))
    #  Aggregate testing reports
    files = glob.glob(args.inputdir + "/*.xml")
    rebot(*files, name=args.title, outputdir=args.outputdir, xunit="result.xml")


def remove_old_logs():
    logging.debug("Delete obsolete log files under '{}'".format(ARTIFACTS_LOGS_DIR))
    remove_files(ARTIFACTS_LOGS_DIR, "*.log")


def remove_old_report_folder(dir):
    full_dir = "{}/{}".format(ARTIFACTS_REPORTS_DIR, dir)
    if dir == None:
        logging.debug(
            "Delete obsolete report files under '{}'".format(ARTIFACTS_REPORTS_DIR)
        )
        remove_files(ARTIFACTS_REPORTS_DIR)
    elif os.path.isdir(full_dir):
        logging.debug("Delete obsolete report folder: {}".format(dir))
        shutil.rmtree(full_dir)


def remove_files(path, pattern="*"):
    files = glob.glob(path + "/" + pattern)
    for f in files:
        if os.path.isfile(f):
            os.remove(f)


def setup_config(args):
    os.environ["WORK_DIR"] = WORK_DIR
    os.environ["TAF_CONFIG"] = args.configDir

    # Read environment variable and store to SettingsInfo
    SettingsInfo().add_name("workDir", os.environ["WORK_DIR"])
    SettingsInfo().add_name("tafConfig", os.environ["TAF_CONFIG"])

    # Read config file and store to SettingsInfo
    constant = __import__("TAF.config.global_variables", fromlist=["global_variables"])
    SettingsInfo().add_name("constant", constant)

    config_constant = __import__(
        "TAF.config." + os.environ["TAF_CONFIG"] + ".configuration",
        fromlist=["configuration"],
    )
    SettingsInfo().add_name("config_constant", config_constant)


def get_kwargs(args):
    global_variables_file = "{}/global_variables.py".format(CONFIG_DIR)
    kwargs = {
        "loglevel": args.logLevel,
        "outputdir": ARTIFACTS_REPORTS_DIR,
        "variable": [
            "WORK_DIR:{}".format(WORK_DIR),
            "TEST_CONFIG:{}".format(args.configDir),
        ],
        "variablefile": [global_variables_file],
    }

    if args.name:
        kwargs["name"] = args.name
    elif args.configDir:
        kwargs["name"] = args.configDir

    if args.include:
        kwargs["include"] = args.include

    if args.exclude:
        kwargs["exclude"] = args.exclude

    if args.configDir:
        variable_file = "{}/{}/configuration.py".format(CONFIG_DIR, args.configDir)
        kwargs["variablefile"].append(variable_file)

    if args.outputDir:
        kwargs["outputdir"] = "{}/{}".format(ARTIFACTS_REPORTS_DIR, args.outputDir)

    if args.outputName:
        kwargs["output"] = "{}-report.xml".format(args.outputName)
        kwargs["log"] = "{}-log.html".format(args.outputName)
        kwargs["report"] = "{}-report.html".format(args.outputName)

    return kwargs
