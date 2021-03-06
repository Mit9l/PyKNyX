# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pyknyx.org}) is Copyright:
  - (C) 2013-2015 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Device (process) management.

Implements
==========

 - B{AdminUtilityValueError}
 - B{AdminUtility}

Documentation
=============

The main goal of this utility is to start/stop a device, and to create a fresh device from a template.
Ths usage of this utility is not mandatory, but handles some annoying logger init suffs.

Usage
=====

Should be used from an executable script. See scripts/pyknyx-admin.py.

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""


import sys
import os.path
import argparse

from pyknyx.common import config
from pyknyx.common.exception import PKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.tools.deviceRunner import DeviceRunner
from pyknyx.tools.templateGenerator import TemplateGenerator
from pyknyx.tools.templates.deviceTemplate import ADMIN, INIT, SETTINGS, DEVICE, FB


class AdminUtilityValueError(PKNyXValueError):
    """
    """


class AdminUtility(object):
    """
    """
    def __init__(self):
        """
        """
        super(AdminUtility, self).__init__()

    def _createDevice(self, args):
        """
        """
        print("Generate '%s' structure from template..." % args.name)  # must be a simple name, not a path

        topDir = args.name
        deviceDir = os.path.join(topDir, args.name)
        pluginsDir = os.path.join(deviceDir, "plugins")

        if args.className is None:
            deviceClass = args.name.capitalize()
        else:
            deviceClass = args.className
        deviceName = args.name
        replace = dict(deviceName=deviceName, deviceClass=deviceClass)

        # Top dir
        TemplateGenerator.createDir(topDir)
        print("'%s' dir created" % topDir)

        adminGen = TemplateGenerator(ADMIN)
        dest = os.path.join(topDir, "admin.py")
        adminGen.generateToFile(dest, replaceDict=replace, script=True)
        print("'%s' file generated" % dest)

        # Device dir
        TemplateGenerator.createDir(deviceDir)
        print("'%s' dir created" % deviceDir)

        initGen = TemplateGenerator(INIT)
        dest = os.path.join(deviceDir, "__init__.py")
        initGen.generateToFile(dest, {}, script=False)
        print("'%s' file generated" % dest)

        configGen = TemplateGenerator(SETTINGS)
        dest = os.path.join(deviceDir, "settings.py")
        configGen.generateToFile(dest, replaceDict=replace, script=False)
        print("'%s' file generated" % dest)

        deviceGen = TemplateGenerator(DEVICE)
        dest = os.path.join(deviceDir, "device.py")
        deviceGen.generateToFile(dest, replaceDict=replace, script=False)
        print("'%s' file generated" % dest)

        fbGen = TemplateGenerator(FB)
        dest = os.path.join(deviceDir, "%sFB.py" % deviceName)
        fbGen.generateToFile(dest, replaceDict=replace, script=False)
        print("'%s' file generated" % dest)

        print("'%s' structure done" % deviceName)

    def _checkConfig(self, args):
        """
        """
        PKNYX_DEVICE_PATH = args.devicePath
        if PKNYX_DEVICE_PATH == "$PKNYX_DEVICE_PATH":
            print("$PKNYX_DEVICE_PATH not set")
            sys.exit(1)

    def _checkDevice(self, args):
        """
        """
        self._checkConfig(args)
        runner = DeviceRunner(args.loggerLevel, args.devicePath, args.gadMapPath)
        runner.check(args.printGroat)

    def _runDevice(self, args):
        """
        """
        self._checkConfig(args)
        runner = DeviceRunner(args.loggerLevel, args.devicePath, args.gadMapPath)
        runner.run(args.daemon)

    def execute(self):

        # Main parser
        mainParser = argparse.ArgumentParser(prog="pyknyx-admin.py",
                                             description="This tool is used to manage pKNyX devices.",
                                             epilog="Under developement...")

        # Create sub-parsers
        subparsers = mainParser.add_subparsers(title="subcommands", description="valid subcommands",
                                               help="sub-command help")

        # Create device parser
        createDeviceParser = subparsers.add_parser("createdevice",
                                                   help="create device from template")
        createDeviceParser.add_argument("-c", "--class", type=str, dest="className",
                                        help="name of the device class")
        createDeviceParser.add_argument("name", type=str,
                                        help="name of the device")
        createDeviceParser.set_defaults(func=self._createDevice)

        # Check/run device parent parser
        loadDeviceParser = argparse.ArgumentParser(add_help=False)
        loadDeviceParser.add_argument("-l", "--logger",
                                      choices=["trace", "debug", "info", "warning", "error", "exception", "critical"],
                                      action="store", dest="loggerLevel", metavar="LEVEL",
                                      help="override logger level")
        loadDeviceParser.add_argument("-p", "--path", action="store", type=str, dest="devicePath", default=os.path.expandvars("$PKNYX_DEVICE_PATH"),
                                      help="set/override $PKNYX_DEVICE_PATH var")
        loadDeviceParser.add_argument("-m", "--map", action="store", type=str, dest="gadMapPath", default=os.path.expandvars("$PKNYX_GAD_MAP_PATH"),
                                      help="set/override $PKNYX_GAD_MAP_PATH var")

        # Check device parser
        checkDeviceParser = subparsers.add_parser("checkdevice",
                                                  parents=[loadDeviceParser],
                                                  help="check device (does not launch the stack main loop)")
        checkDeviceParser.add_argument("-g", "--groat", action="store_true", dest="printGroat", default=False,
                                       help="print group object association table")
        checkDeviceParser.set_defaults(func=self._checkDevice)

        # Run device parser
        runDeviceParser = subparsers.add_parser("rundevice",
                                                parents=[loadDeviceParser],
                                                help="run device")
        runDeviceParser.add_argument("-d", "--daemon", action="store_true", default=False,
                                     help="run process as daemon")
        runDeviceParser.set_defaults(func=self._runDevice)

        # Parse args
        args = mainParser.parse_args()
        args.func(args)

