"""
 @copyright Copyright (C) 2019 Intel Corporation

 @license SPDX-License-Identifier: Apache-2.0

 @package TUC.setup

 @file setup_python.py

 @description
    This script sets up the python environment for TAF
"""

import os
import sys

"""
setup python environment

  *** IMPORTANT ***
  This module should be the first Library
    included in the robot file. Robot should
    be executed from testScenarios subdir.

  Given a toplevel directory, add all subdirs to the pythonpath.
  Note that sys.path.append is equivalent to specifying PYTHONPATH.

  When this file is executed from the robot script, the current
    directory is robot's current directory which is TAF/testScenarios.

  TOPLEVEL *MUST BE* <TAF-xxx>, which is two directory levels
    above robot's current directory which is TAF/testScenarios.
"""

# This is robot current working dir, so toplevel is three levels above
TOPLEVEL = "../../../"
''' We need to list the subdirs directly
    under the TOPLEVEL, so we can exclude
    any git dir, since the test code might
    reside in a git repo
'''

excludes = ['pycache', 'config', 'testScenarios', 'testArtifacts']

# The full path of the TOPLEVEL
ABS_TOP = os.path.abspath(TOPLEVEL)
# add TOPLEVEL to pythonpath
sys.path.append(ABS_TOP)
top_dirs = os.listdir(ABS_TOP)

# logger.console('setup py: top_subdirs: {0}'.format(top_dirs))
# EXCLUDE ANY GIT DIRS """
top_dirs_no_git = []
for sdir in top_dirs:
    if os.path.isdir(os.path.join(ABS_TOP, sdir)):
        if str(sdir) != '.git':
            top_dirs_no_git.append(ABS_TOP + os.path.sep + sdir)

# logger.console('setup py: top_subdirs no git: {0}'.format(top_dirs_no_git))
# walk each top level dir except .git
for tdir in top_dirs_no_git:
    for root, subdirs, files in os.walk(tdir, topdown=True):
        if root not in sys.path:
            if not any(x in str(root) for x in excludes):
                sys.path.append(root)


def TAF_dummy_keyword():
    """ This just avoids a robot WARN message.
        Without this, Robot WARNS this file
        contains no keywords.
    """
    pass
