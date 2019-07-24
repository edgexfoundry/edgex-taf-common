"""

 @copyright Copyright (C) 2019 Intel Corporation

 @license SPDX-License-Identifier: Apache-2.0

 @package TUC.data

 @file TestSettings.py

 @description
    Contains  a class that helps to parse a configuration file.
"""

import configparser


class TestSettings:
    """
    @class TestSettings A class to parse a configuration file
    consisting of one or more sections
    instantiate the class with a config file,
    then call get_section with the name of a section that *should*
    be in the file.

    Example:
        ** test.cfg **
        [MySection]
        MyKey1=MyValue1
        MyKey2=MyValie2
        ** end of test.cfg **
        ** testsuite_setup.py **
        cfg_parser = TestSettings(test.cfg)
        mysection = cfg_parser.get_section('MySection')
        myvalue1 = mysection['MyValue1']
        ** end of testsuite_setup.py example **
    """

    def __init__(self, config):
        """
        class constructor
        @param    config    config file to parse
        @return   none
        @exception   none
        """
        self.cfgFile = config
        self.cfg = configparser.ConfigParser()
        self.cfg.optionxform = str
        self.cfg.read(self.cfgFile)

    def get_section(self, section_name):

        """
        function : get_section populates section_dict with key/value pairs for the requested section_name
        @param     section_name name of the section
        @retval    section_dict list of key/value pairs for the requested section.
        @exception  raise
        """

        try:
            section_dict = {}
            entries = self.cfg.options(section_name)
            if not entries:
                raise Exception('TAF TestSettings: {0} information could not be retrieved from {1}'.format(section_name, self.cfgFile))
            else:
                for entry in entries:
                    section_dict[entry] = self.cfg.get(section_name, entry)

            return section_dict
        except:
            raise

    def sections(self):
        """
        function : sections returns the sections
        @return   list of sections in the cfg file from self.cfg.sections()
        @exception   none
        """
        return self.cfg.sections()
