#-------------------------------------------------------------------------------
# Name:        crown.py
# Purpose:     Main module for Neptune Pool and Spa Automation
#
# Author:      alji
#
# Created:     03/04/2013
# Copyright:   (c) alji 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# On my mac, required libraries are not in my python path and must be inserted:
## (this is simply a convenience for my own benefit, this is not elegant code)
PLATFORM = "mac"
if PLATFORM == "mac":
    import sys
    sys.path.insert(0, '/Users/jisunstetson/bin')
# Now, the following imports will work
from modules.neptune.devices import DeviceManager
from modules.neptune.logger import NeptuneLogger

class NeptuneCrown(object):
    """
    This object is the entry point for a human interface (GUI, hardware, etc).

    It manipulates devices and responds in human-readable statements in cases of
    failure and success.
    """
    def __init__(self, test=True):
        """
        Loads device information and registers logger
        :param test: Optional argument that turns off Serial commands so that the object can be tested
        without connection to a serial device like Arduino.
        :type test: bool
        :return: None
        """
        # Load device information
        self.deviceManager = DeviceManager()
        self.devices = self.deviceManager.devices

        # Register Logger with core ID code
        self.logger = NeptuneLogger('0000')

    def setSwitchDevice(self, destId, newValue, author='0000'):
        """
        Given the ID of a switch device, sets a value
        :param destId: Device ID of the switch to be manipulated
        :type destId: str
        :param newValue: New value for the switch (typically 0 or 1)
        :type newValue: int
        :param author: Device ID of the object requesting the change
        :return: Either a serial command or failure code, and human readable text
        :rtype: tuple
        """
        self.logger.author = author
        commandStr = "Switch device %s to %s." % (destId, newValue)

        # Check for the device existence
        if not str(destId) in self.devices.keys():
            failure = (0, "No device exists with ID %s" % destId)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Process the device based on type:
        if self.devices[destId]['deviceType'] == "switch":
            typeCode = "s"
        else:
            failure = (0, "Device \"%s\" (%s) is not a switch type." % (self.devices[destId]['name'],destId))
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        if not newValue.isdigit():
            failure = (0, "New value %s is not a digit." % newValue)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Make sure new value is within rage
        minVal = self.devices[destId]['minValue']
        maxVal = self.devices[destId]['maxValue']
        if int(newValue) < int(minVal):
            failure = (0, "New value %s is below minimum %s." % (newValue, minVal))
            self.logger.logCommand(destId, commandStr, failure)
            return failure
        if int(newValue) > int(maxVal):
            failure = (0, "New value %s is above maximum %s." % (newValue, maxVal))
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Great! Format some pretty output
        prettyVal = newValue
        if int(newValue) == int(minVal):
            prettyVal = self.devices[destId]['minName']
        elif int(newValue) == int(maxVal):
            prettyVal = self.devices[destId]['maxName']
        prettyDescription = "Device %s has been switched to %s" % (self.devices[destId]['name'], prettyVal)

        # Make the change
        self.devices[destId]['currentValue'] = newValue
        self.deviceManager.saveState(self.devices)
        # Construct serial command
        success = (">%s%s%s" % (destId, typeCode, newValue), prettyDescription)
        # Log the change
        self.logger.logCommand(destId, commandStr, success)
        return success

    def setStepDevice(self, destId, newValue, author='0000'):
        """
        Given the ID of a step device, sets a value
        :param destId: Device ID of the step device to be manipulated
        :type destId: str
        :param newValue: New value for the step device
        :type newValue: int
        :param author: Device ID of the object requesting the change
        :return: Either a serial command or failure code, and human readable text
        :rtype: tuple
        """
        self.logger.author = author
        commandStr = "Set variable step device %s to %s." % (destId, newValue)

        # Check for the device existence
        if not str(destId) in self.devices.keys():
            failure = (0, "No device exists with ID %s" % destId)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Process the device based on type:
        if self.devices[destId]['deviceType'] == "step":
            typeCode = "t"
        else:
            failure = (0, "Device \"%s\" (%s) is not a step type." % (self.devices[destId]['name'],destId))
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        if not newValue.isdigit():
            failure = (0, "New value %s is not a digit." % newValue)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Make sure new value is within rage
        minVal = self.devices[destId]['minValue']
        maxVal = self.devices[destId]['maxValue']
        if int(newValue) < int(minVal):
            failure = (0, "New value %s is below minimum %s." % (newValue, minVal))
            self.logger.logCommand(destId, commandStr, failure)
            return failure
        if int(newValue) > int(maxVal):
            failure = (0, "New value %s is above maximum %s." % (newValue, maxVal))
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Great! Format some pretty output
        prettyVal = newValue
        if int(newValue) == int(minVal):
            prettyVal = self.devices[destId]['minName']
        elif int(newValue) == int(maxVal):
            prettyVal = self.devices[destId]['maxName']
        prettyExtra = ''
        if '&#37;' in self.devices[destId]['unitType']:
            prettyExtra = self.devices[destId]['unitType']
        elif self.devices[destId]['unitType'] == "%":
            multiplier = 100.0/float(self.devices[destId]['maxValue'])
            perc = multiplier*float(newValue)
            percMin = 100.0-perc
            prettyExtra = ", (%s%% %s, %s%% %s)" % (percMin, self.devices[destId]['minValue'], 
                                                        perc, self.devices[destId]['maxName'])

        prettyDescription = "Device %s has been set to %s%s" % (self.devices[destId]['name'], prettyVal, prettyExtra)

        # Make the change
        self.devices[destId]['currentValue'] = newValue
        self.deviceManager.saveState(self.devices)
        # Construct serial command
        success = (">%s%s%s" % (destId, typeCode, newValue), prettyDescription)
        # Log the change
        self.logger.logCommand(destId, commandStr, success)
        return success

    def updateSensorDevice(self, destId, newValue, author='0000'):
        """
        Given the ID of a sensor device, queries device for an update
        :param destId: Device ID of the sensor to be updated
        :type destId: str
        :param newValue: New value
        :type newValue: int
        :param author: Device ID of the object requesting the change
        :return: Either a serial command or failure code, and human readable text
        :rtype: tuple
        """
        self.logger.author = author
        commandStr = "Updating sensor device %s to %s." % (destId, newValue)

        # Check for the device existence
        if not str(destId) in self.devices.keys():
            failure = (0, "No device exists with ID %s" % destId)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Process the device based on type:
        if not self.devices[destId]['deviceType'] == "sensor":
            failure = (0, "Device \"%s\" (%s) is not a sensor type." % (self.devices[destId]['name'],destId))
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        if not newValue.isdigit():
            failure = (0, "New value %s is not a digit." % newValue)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Make sure new value is within rage
        minVal = self.devices[destId]['minValue']
        maxVal = self.devices[destId]['maxValue']
        if int(newValue) < int(minVal):
            failure = (0, "New value %s is below minimum %s." % (newValue, minVal))
            self.logger.logCommand(destId, commandStr, failure)
            return failure
        if int(newValue) > int(maxVal):
            failure = (0, "New value %s is above maximum %s." % (newValue, maxVal))
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Great! Format some pretty output
        prettyDescription = "Device %s has been updated to value %s." % (self.devices[destId]['name'], newValue)
        # Construct serial command
        success = (">%s%s%s" % (destId, typeCode, newValue), prettyDescription)
        self.logger.logCommand(destId, commandStr, success)
        return success

    def setDeviceAttribute(self, destId, attrName, newValue, author='0000'):
        """
        Given the ID of a device, sets a specified attribute to a given value
        :param destId: Device ID of the switch to be manipulated
        :type destId: str
        :param attrName: Name of the attribute to be set
        :type attrName: str
        :param newValue: New value for the step device
        :type newValue: int
        :param author: Device ID of the object requesting the change
        :return: Either a serial command or failure code, and human readable text
        :rtype: tuple
        """
        self.logger.author = author
        commandStr = "Set device %s attribute %s to %s." % (destId, attrName, newValue)

        # Check for the device existence
        if not str(destId) in self.devices.keys():
            failure = (0, "No device exists with ID %s" % destId)
            self.logger.logCommand(destId, commandStr, failure)
            return failure

        # Process the device based on type:
        if self.devices[destId]['deviceType'] == "switch":
            typeCode = "s"
        elif self.devices[destId]['deviceType'] == "step":
            typeCode = "t"
        elif self.devices[destId]['deviceType'] == "core":
            typeCode = "c"
        elif self.devices[destId]['deviceType'] == "sensor":
            typeCode = "n"
        else:
            typeCode = "u" 

        self.devices[destId][attrName] = newValue
        self.deviceManager.saveState(self.devices)
        success = (1, ">%s%s%s" % (destId, typeCode, newValue))
        self.logger.logCommand(destId, commandStr, success)
        return success
