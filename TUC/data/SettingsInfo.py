"""
 @copyright Copyright (C) 2019 Intel Corporation

 @license SPDX-License-Identifier: Apache-2.0

 @package TUC.data

 @file SettingsInfo.py

 @description
   A singleton class to hold object pairs read from config files.
"""
from TUC.data.TestSettings import TestSettings


class SettingsInfo(object):

    """
    class to hold setup objects
      so there is only one instance
      throughout a test suite

    @class SettingsInfo

    @param Object   Base object class
    """
    class __SettingsInfo(object):
        """
           Inner class represents the real object
           @param    self   represents the instance of the class.
        """
        def __init__(self):
            """
            __init__ need to do nothing but return object
            @param    self   represents the instance of the class.
            """
            pass

        def __add_name(self, name, obj):
            """
            __add_name    adds an object with the specified name
            @param    self   represents the instance of the class.
            @param    name  key that will let access to specific object.
            @param    obj   Object that will be added in pair with a name.
            """
            setattr(self, name, obj)

        def __has_name(self,name):
            """
            __has_name    check if attribute is with this object
            @param    self   represents the instance of the class.
            @param   name   name to check
            @retval bool   hasattr returns true if attribute is with this object
            """
            return hasattr(self,name)

        def __delete(self,name):
            """
            __delete  Delete name
            @param    self   represents the instance of the class.
            @param   name   name to delete
            """
            if self.__has_name(name):
                __delete__(self, name)
    instance = None

    def __init__(self):
        """
        __init__    instantiates new object or return existing object
        @param    self   represents the instance of the class.
        """
        if not SettingsInfo.instance:
            SettingsInfo.instance = SettingsInfo.__SettingsInfo()

    def __getattr__(self, name):
        """
        __getattr__    returns the specified object if it exists
        @param    self   represents the instance of the class.
        @param  name  name of the object
        @retval bool  getattr returns bool if the object exists
        """
        return getattr(self.instance, name)

    def add_name(self, name, obj):
        """
        add_name    wrapper for adding a name to the inner object
        @param    self   represents the instance of the class.
        @param  name  name of the object
        """
        self.instance.__add_name(name, obj)

    def has_name(self,name):
        """
        has_name    wrapper to check if name is in the inner object
        @param name name of the object
        @retval bool  __has_name returns bool if the object exists
        """
        return self.instance.__has_name(name)

    def del_name(self,name):
        """
        del_nam     wrapper to remove name to object. It is not implemented yet.
        @param name name of the object
        @retval TBD
        """

    def parseConfigFile(self, cfgFile = None):
        """
        parseConfigFile parses the config file that is passed as the parameter to the function and updates the self Object.
        @param cfgFile name of the cfgFile
        @retval True
        """

        if cfgFile is None:
            return False
        else:
            config_parser = TestSettings(cfgFile)
        for eachCfg in config_parser.sections():
            self.add_name(eachCfg, config_parser.get_section(eachCfg))
        return True
