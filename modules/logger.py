#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     This module contains objects used by the Neptune Pool Automation
#              system which are used to log activity in the system. It includes
#              two object types: a logger and a log entry, and is capable of
#              logging a variety of entry types.
#
# Author:      alji
#
# Created:     03/04/2013
# Copyright:   (c) alji 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import json
import serial
from time import sleep
from random import randint
from datetime import datetime

class NeptuneLogger(object):
    """
    This object manipulates the Neptune Log, clearing or filling it with entries.

    Attributes:
        last (str): Returns the last log entry, commonly used to check for success
        by client after a new log entry.
    """
    def __init__(self, author):
        """
        :param author: Every entry requires an author; the device ID of the requester.
        :type author: str or int
        :return: None
        """
        self.author = author
        # This software can be run on multiple platforms, each with its own env
        #  variable for the home dir. The following ensures compatibility.
        if os.environ.has_key('HOMEPATH'):
            self.logFilePath = "%s/.neptuneLog.json" % os.environ['HOMEPATH']
        else:
            self.logFilePath = "%s/.neptuneLog.json" % os.environ['HOME']
        # Load log into memory, or create it if it does not exist.
        self.log = self.getOrCreateLog()

    def getOrCreateLog(self):
        """
        This method simply checks for the existence of a log file, and creates one
        if required.
        :return: log in the form of nested dicts from json
        """
        if os.path.exists(self.logFilePath):
            logFile = open(self.logFilePath, 'r')
            log = json.loads(logFile.read())
            logFile.close()
        else:
            print("No device log found. Creating.")
            log = {}
        return log

    def clearLog(self):
        """
        This method simply clears the device log, leaving it on disk.
        :return: None
        """
        self.log = {} # Clear log in memory
        logJson = json.dumps(self.log)

        # Write empty log to file.
        logFile = open(self.logFilePath, 'w')
        logFile.write(logJson)
        logFile.close()

    def logCommand(self, deviceId, command, success):
        """
        Logs an attempt to execute a command issued from one device to another.
        :param deviceId: Device ID of the device receiving the command from the author.
        :type deviceId: str or int
        :param command: The actual command issued from author to device.
        :type command: str
        :param success: Whether or not the command was successfully executed.
        :type success: bool
        :return: None
        """
        nowDt = datetime.now()
        now = nowDt.strftime("%Y:%m:%d:%A:%H:%M:%S")

        entry = NeptuneLogEntry(entryType="command",
                                author=self.author,
                                destination=deviceId,
                                logTime=now,
                                entryBody=command,
                                success=success)
        self._addEntry(entry)

    def logComment(self, comment):
        """
        Logs a comment from the author.
        :param comment: The comment to be logged.
        :type comment: str
        :return: None
        """
        nowDt = datetime.now()
        now = nowDt.strftime("%Y:%m:%d:%A:%H:%M:%S")

        entry = NeptuneLogEntry(entryType="comment",
                                author=self.author,
                                logTime=now,
                                entryBody=comment)
        self._addEntry(entry)

    def logHandshake(self, dest, success):
        """
        Logs an attempt at a device handshake, just to confirm a connection
        between two devices.
        :param dest: Device ID of the device to which the author is attempting to connect.
        :type dest: str or int
        :param success: Whether or not the handshake was returned from the destination.
        :type success: bool
        :return: None
        """
        nowDt = datetime.now()
        now = nowDt.strftime("%Y:%m:%d:%A:%H:%M:%S")

        entry = NeptuneLogEntry(entryType="handshake",
                                author=self.author,
                                logTime=now,
                                destination=dest,
                                success=success)
        self._addEntry(entry)

    def _addEntry(self, entry):
        """
        Internal method which just writes the requested entry to the log.
        :param entry: The log entry to be written to the log.
        :type entry: NeptuneLogEntry
        :return: None
        """
        # Add the entry to the log in memory, by date/time
        self.log[entry.logTime] = entry.data
        # Encode as JSON
        logJson = json.dumps(self.log)

        # Write device state json to file.
        logFile = open(self.logFilePath, 'w')
        logFile.write(logJson)
        logFile.close()

    def _getType(self, type):
        """
        Internal method which searches device log for entries by type.
        :param type: The type of entry to fetch (Command, Comment, Handshake)
        :return: Entries matching the type requested.
        :rtype: dict
        """
        matches = {}
        for entry in self.log:
            if self.log[entry]['entryType'] == type:
                matches[entry] = self.log[entry]
        return matches

    def getComments(self):
        """
        Fetches Comments from the log.
        :return: Log entries of type Comment.
        :rtype: dict
        """
        return self._getType("comment")

    def getHandshakes(self):
        """
        Fetches Handshakes from the log.
        :return: Log entries of type Comment.
        :rtype: dict
        """
        return self._getType("handshake")

    @property
    def last(self):
        """The last log entry logged"""
        lastDate = self.log.keys()[-1]
        lastEntry = self.log[lastDate]
        return {lastDate:lastEntry}

class NeptuneLogEntry(object):
    """
    This object serves as a single log entry and can be of multiple types
    depending on what is passed in via kwargs.

    Attributes:
        data (dict): A JSON-compatible dict containing all pertinent data for
        this log entry.
    """
    def __init__(self, **kwargs):
        """
        Initialize the object by assigning data to appropriate properties.
        :param kwargs: entryType, author, destination, entryBody, success, logTime
        :return:
        """
        # -- Entry Type --
        # (str) - category of entry:
        # comment
        # communication
        # command
        # deviceData
        # handshake
        # query
        self.entryType = kwargs.get('entryType', "comment")

        # -- Author --
        # str(####) - device id of entity logging this entry
        self.author = kwargs.get('author', "0000")

        # -- Destination --
        # str(####) - device id of entity on the receiving
        # end of this event
        self.destination = kwargs.get('destination', None)

        # -- Entry Body --
        # (str) - the meat of the entry
        self.entryBody = kwargs.get('entryBody', "")

        # -- Success --
        # (bool) - Succinct way to indicate whether or not
        # this is a happy entry or a sad one
        self.success = kwargs.get('success', True)

        # -- Log Time --
        # timestamp - when this entry was written into the log
        self.logTime = kwargs.get('logTime', None)

    @property
    def data(self):
        """All data associated with this log entry"""
        data = {'entryType':self.entryType,
                'author':self.author,
                'destination':self.destination,
                'entryBody':self.entryBody,
                'success':self.success
                }
        return data

