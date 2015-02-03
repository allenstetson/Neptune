#-------------------------------------------------------------------------------
# Name:        devices.py
# Purpose:     Module for Neptune Pool and Spa Automation containing devices 
#              and device manager
#
# Author:      alji
#
# Created:     03/04/2013
# Copyright:   (c) alji 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import json

# On my Mac, required modules are not in the Python Path and must be inserted.
PLATFORM = "mac"
if PLATFORM == "mac":
    import sys
    sys.path.insert(0, '/Users/jisunstetson/bin')
# Now this line will work on all platforms:
from modules.neptune.logger import NeptuneLogger

class NeptuneDevice(object):
    """
    A base class for all Neptune devices which holds properties for the given device.

    Attributes:
        name (str): The common human name of the device
        deviceId (str): The device ID (unique)
        deviceType (str): Type of device (switch, step, sensor, core, etc)
        deviceFamily (str): Family group of this device (pool, spa, core, etc)
        minValue (int): Minimum value of this device
        maxValue (int): Maximum value of this device
        currentValue (int): Current value of this device
        minName (str): Human readable name for minValue ("off", "spa", etc)
        maxName (str): Human readable name for maxValue ("on", "pool", etc)
        unitType (str): Unit type of this device (degrees, cm, inches, percent, etc)
        custom (str): Any custom attributes for this device
    """
    def __init__(self):
        """
        Initialize attrs and pack each attribute with default values
        :return: None
        """
        self.attrs = {}
        self.attrs['name'] = None
        self.attrs['deviceId'] = None
        self.attrs['deviceType'] = None
        self.attrs['deviceFamily'] = None
        self.attrs['minValue'] = None
        self.attrs['maxValue'] = None
        self.attrs['currentValue'] = None
        self.attrs['minName'] = None
        self.attrs['maxName'] = None
        self.attrs['unitType'] = None
        self.attrs['custom'] = {}

    @property
    def name(self):
        return self.attrs['name']
    @name.setter
    def name(self, value):
        self.attrs['name'] = value

    @property
    def deviceId(self):
        return self.attrs['deviceId']
    @deviceId.setter
    def deviceId(self, value):
        self.attrs['deviceId'] = value

    @property
    def deviceType(self):
        return self.attrs['deviceType']
    @deviceType.setter
    def deviceType(self, value):
        self.attrs['deviceType'] = value

    @property
    def deviceFamily(self):
        return self.attrs['deviceFamily']
    @deviceFamily.setter
    def deviceFamily(self, value):
        self.attrs['deviceFamily'] = value

    @property
    def minValue(self):
        return self.attrs['minValue']
    @minValue.setter
    def minValue(self, value):
        self.attrs['minValue'] = value

    @property
    def maxValue(self):
        return self.attrs['maxValue']
    @maxValue.setter
    def maxValue(self, value):
        self.attrs['maxValue'] = value

    @property
    def currentValue(self):
        return self.attrs['currentValue']
    @currentValue.setter
    def currentValue(self, value):
        self.attrs['currentValue'] = value

    @property
    def minName(self):
        return self.attrs['minName']
    @minName.setter
    def minName(self, value):
        self.attrs['minName'] = value

    @property
    def maxName(self):
        return self.attrs['maxName']
    @maxName.setter
    def maxName(self, value):
        self.attrs['maxName'] = value

    @property
    def unitType(self):
        return self.attrs['unitType']
    @unitType.setter
    def unitType(self, value):
        self.attrs['unitType'] = value

    @property
    def custom(self):
        return self.attrs['custom']
    @custom.setter
    def custom(self, value):
        self.attrs['custom'] = value

class DefaultDeviceMapper(object):
    """
    Neptune comes pre-packaged with a number of default devices.
    This object initializes each of them.
    """
    def __init__(self):
        """
        Initializes all default devices, one by one, storing them in a list.
        :return: None
        """
        devices = []
        #degree = unichr(176)
        degree = '&#37;'

        # Device ID codes:
        ## core:     0000
        ## http:     0001
        ## arduino:  1000
        ## physical: 1100-1199
        ## radio:    2000-2999
        ## custom:   3000+

        # Initialize Devices:
        ## CORE
        device = NeptuneDevice()
        device.name = "Crown"
        device.deviceId = '0000'
        device.deviceType = "core"
        device.deviceFamily = "core"
        device.minValue = None
        device.maxValue = None
        device.currentValue = None
        device.minName = None
        device.maxName = None
        device.unitType = None
        devices.append(device)

        ## HTTP
        device = NeptuneDevice()
        device.name = "HTTP"
        device.deviceId = '0001'
        device.deviceType = "core"
        device.deviceFamily = "core"
        device.minValue = None
        device.maxValue = None
        device.currentValue = None
        device.minName = None
        device.maxName = None
        device.unitType = None
        devices.append(device)

        ## Arduino
        device = NeptuneDevice()
        device.name = "Arduino"
        device.deviceId = '1000'
        device.deviceType = "core"
        device.deviceFamily = "core"
        device.minValue = None
        device.maxValue = None
        device.currentValue = None
        device.minName = None
        device.maxName = None
        device.unitType = None
        devices.append(device)

        ## Physical Devices
        ### pool light
        device = NeptuneDevice()
        device.name = "Pool Light"
        device.deviceId = '1100'
        device.deviceType = "switch"
        device.deviceFamily = "Pool"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Off"
        device.maxName = "On"
        device.unitType = None
        devices.append(device)

        ### spa blower
        device = NeptuneDevice()
        device.name = "Spa Blower"
        device.deviceId = '1101'
        device.deviceType = "switch"
        device.deviceFamily = "Spa"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Off"
        device.maxName = "On"
        device.unitType = None
        devices.append(device)

        ### fill valve
        device = NeptuneDevice()
        device.name = "Fill Valve"
        device.deviceId = '1102'
        device.deviceType = "switch"
        device.deviceFamily = "Pool and Spa"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Off"
        device.maxName = "On"
        device.unitType = None
        devices.append(device)

        ## Radio Devices
        ### pump intake
        device = NeptuneDevice()
        device.name = "Pump Intake"
        device.deviceId = '2000'
        device.deviceType = "step"
        device.deviceFamily = "Pool and Spa"
        device.minValue = 0
        device.maxValue = 180
        device.currentValue = 90
        device.minName = "Pool"
        device.maxName = "Spa"
        device.unitType = degree
        devices.append(device)

        ### pump return
        device = NeptuneDevice()
        device.name = "Pump Return"
        device.deviceId = '2001'
        device.deviceType = "step"
        device.deviceFamily = "Pool and Spa"
        device.minValue = 0
        device.maxValue = 180
        device.currentValue = 90
        device.minName = "Pool"
        device.maxName = "Spa"
        device.unitType = degree
        devices.append(device)

        ### pump
        device = NeptuneDevice()
        device.name = "Pump"
        device.deviceId = '2002'
        device.deviceType = "switch"
        device.deviceFamily = "Pool and Spa"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Off"
        device.maxName = "On"
        device.unitType = None
        devices.append(device)

        ### spa heater temp
        device = NeptuneDevice()
        device.name = "Heater (Spa)"
        device.deviceId = '2003'
        device.deviceType = "step"
        device.deviceFamily = "Spa"
        device.minValue = 55
        device.maxValue = 110
        device.currentValue = 98
        device.minName = "Cold"
        device.maxName = "Hot"
        device.unitType = degree+"F"
        devices.append(device)

        ### pool heater temp
        device = NeptuneDevice()
        device.name = "Heater (Pool)"
        device.deviceId = '2004'
        device.deviceType = "step"
        device.deviceFamily = "Pool"
        device.minValue = 55
        device.maxValue = 90
        device.currentValue = 78
        device.minName = "Cold"
        device.maxName = "Hot"
        device.unitType = degree+"F"
        devices.append(device)

        ### spa heater
        device = NeptuneDevice()
        device.name = "Heater (Spa)"
        device.deviceId = '2005'
        device.deviceType = "switch"
        device.deviceFamily = "Spa"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Off"
        device.maxName = "On"
        device.unitType = None
        devices.append(device)

        ### pool heater
        device = NeptuneDevice()
        device.name = "Heater (Pool)"
        device.deviceId = '2006'
        device.deviceType = "switch"
        device.deviceFamily = "Pool"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Off"
        device.maxName = "On"
        device.unitType = None
        devices.append(device)

        ### pool thermistor
        device = NeptuneDevice()
        device.name = "Pool Temperature"
        device.deviceId = '2007'
        device.deviceType = "sensor"
        device.deviceFamily = "Pool"
        device.minValue = -100
        device.maxValue = 250
        device.currentValue = 68
        device.minName = "Cold"
        device.maxName = "Hot"
        device.unitType = degree+"F"
        devices.append(device)

        ### pool water level
        device = NeptuneDevice()
        device.name = "Pool Water Level"
        device.deviceId = '2008'
        device.deviceType = "sensor"
        device.deviceFamily = "Pool and Spa"
        device.minValue = 0
        device.maxValue = 100
        device.currentValue = 50
        device.minName = "Low"
        device.maxName = "High"
        device.unitType = "%"
        devices.append(device)

        ## Auxillery
        ### aux 1
        device = NeptuneDevice()
        device.name = "Aux 1"
        device.deviceId = '3000'
        device.deviceType = "switch"
        device.deviceFamily = "Aux"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Min"
        device.maxName = "Max"
        device.unitType = None
        devices.append(device)

        ### aux 2
        device = NeptuneDevice()
        device.name = "Aux 2"
        device.deviceId = '3001'
        device.deviceType = "switch"
        device.deviceFamily = "Aux"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Min"
        device.maxName = "Max"
        device.unitType = None
        devices.append(device)

        ### aux 3
        device = NeptuneDevice()
        device.name = "Aux 3"
        device.deviceId = '3002'
        device.deviceType = "switch"
        device.deviceFamily = "Aux"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Min"
        device.maxName = "Max"
        device.unitType = None
        device.custom = {'voltage':24}
        devices.append(device)

        ### aux 4
        device = NeptuneDevice()
        device.name = "Aux 4"
        device.deviceId = '3003'
        device.deviceType = "switch"
        device.deviceFamily = "Aux"
        device.minValue = 0
        device.maxValue = 1
        device.currentValue = 0
        device.minName = "Min"
        device.maxName = "Max"
        device.unitType = None
        device.custom = {'voltage':24}
        devices.append(device)

        self.devices = devices

    def getDefaults(self):
        """
        This method simply returns the list of default devices.
        :return: List of default devices.
        :rtype: list
        """
        return self.devices

class DeviceManager(object):
    """
    This object saves and loads the state of all devices on the Neptune.
    """
    def __init__(self):
        """
        Load device state from disk or from default, store in memory.
        :return: None
        """
        # Register Logger with ID matching that of the core device.
        self.logger = NeptuneLogger('0000')
        
        # Define filepath of device state
        ## This works on multiple platforms with different env variables for home
        if os.environ.has_key('HOMEPATH'):
            self.deviceInfoFilePath = "%s/.neptuneDeviceInfo.json" % os.environ['HOMEPATH']
        else:
            self.deviceInfoFilePath = "%s/.neptuneDeviceInfo.json" % os.environ['HOME']
        # Load device info
        if os.path.exists(self.deviceInfoFilePath):
            self.devices = self._loadDevicesFromFile()
        else:
            self.logger.logComment("Creating new Device Info file at %s" % self.deviceInfoFilePath)
            self.devices = self._loadDevicesFromDefaults()
        
    def _loadDevicesFromFile(self):
        """
        Reads the device info file off of disk and load it into memory.
        :return: device data as a dict of device ids and attributes
        :rtype: dict
        """
        with open(self.deviceInfoFilePath) as deviceInfoFile:
            data = json.load(deviceInfoFile)
        return data

    def _loadDevicesFromDefaults(self):
        """
        Loads default devices and stores them in memory & on disk.
        :return: device data as a dict of device ids and attributes
        :rtype: dict
        """
        # Load defaults
        mapper = DefaultDeviceMapper()
        defaults = mapper.getDefaults()
        # Store them into memory
        devices = {}
        for device in defaults:
            devices[device.attrs['deviceId']] = device.attrs
        # Write them to disk
        with open(self.deviceInfoFilePath, 'w') as deviceInfoFile:
            json.dump(devices, deviceInfoFile)
        return devices

    def saveState(self, devices):
        """
        Saves the current state of all devices to disk.
        :param devices: device data as a dict of device ids and attributes
        :type devices: dict
        :return: None
        """
        with open(self.deviceInfoFilePath, 'w') as deviceInfoFile:
            json.dump(devices, deviceInfoFile)
        
