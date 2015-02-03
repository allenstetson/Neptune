#!/usr/bin/python

#-------------------------------------------------------------------------------
# Name:    	main.py
# Purpose:      Main application for Neptune Pool and Spa Automation
#
# Author:  	alji
#
# Created: 	14/11/2012
# Copyright:   (c) alji 2012
# Licence: 	<your licence>
#-------------------------------------------------------------------------------
import os
import datetime as dt

#---Twisted Serial / HTTP---
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.protocols.basic import LineReceiver
from twisted.internet.serialport import SerialPort

import xml.etree.ElementTree as xmlEtree

#---Neptune---
IS_TEST = True
#PLATFORM = "mac"
PLATFORM = "windows"
# On my mac, required libraries are not in my python path and must be inserted:
## (this is simply a convenience for my own benefit, this is not elegant code)
if PLATFORM == "mac":
  print("mac")
  import sys
  sys.path.insert(0, '/Users/jisunstetson/bin')
# Now, the following imports will work
from modules.neptune.crown import NeptuneCrown
from modules.neptune.logger import NeptuneLogger

###################################
## GLOBALS
###################################
NPASASC = "111576" # Authorization code
# Define COM ports for serial communication with Arduino
if PLATFORM == "windows":
    COM_PORT = 'COM3'
elif PLATFORM == "mac":
    COM_PORT = '/dev/ttys0'

###################################
## SERIAL
###################################
class SerialResource(LineReceiver):
    """
    This object processes incoming serial requests and sends outgoing serial commands.
    """
    def processData(self, data):
        """
        Processes any incoming serial data
        :param data: serial data to be decoded
        :type data: str
        :return: None
        """
        # Alert user to incoming serial data
        print("<--%s--: %s" % (COM_PORT, data))
        # Decode the data according to Neptune protocol
        devId    = data[0:4]
        devType  = data[4]
        newValue = data[5:]

        crown = NeptuneCrown()
        author = '1000'  # Arduino device ID

        # Currently, Arduino only ever sends signals regarding Sensors
        if devType == "n":
            (success, pretty) = crown.updateSensorDevice(devId, newValue, author=author)
        # Alert user to success or failure
        if success:
            print(pretty)
        else:
            print("ERROR: %s" % pretty)

    def connectionMade(self):
        """
        This method is built in to the LineReceiver object, and tells the Receiver
        what to do in the case of a successful connection. We only wish to alert the user.
        :return: None
        """
        print('Serial connection made!')

    def lineReceived(self, line):
        """
        This method is built in to the LineReceiver object, and tells the Receiver
        what to do in the case of a successful receipt of serial data.
        :param line: Incoming serial bytes
        :return: None
        """
        data = str(line)
        try:
            self.processData(data)
        except ValueError:
            print('Unable to parse data %s' % line)

    def serialWrite(self, data):
        """
        This method writes any requested data to the serial connection.
        :param data: Requested data to be sent
        :type data: str
        :return: True
        :rtype: bool
        """
        # Alert the user to outgoing serial data
        print(" --%s-->: %s" % (COM_PORT, data))
        # Append return and newline expected by Arduino
        data += "/r/n"
        # Send data
        self.sendLine(data)
        return True

#    def sendLine(self):
#         pass

###################################
## WEB
###################################
class WebResource(resource.Resource):
    """
    This base class for all http protocol resources just provides a serial property
    which these resources will use to execute any commands specified over http.
    """
    def setSerial(self, serialProcess):
        self.serialProcess = serialProcess

class HttpResource(WebResource):
    """
    This object functions as our root http resource, being called to display by default
    if no child resources are requested.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        # Send anything, just to test the serial connection
        success = self.serialProcess.serialWrite("I like you.")

        request.setHeader("content-type", "html")
        #request.setHeader("content-type", "text/plain")
        if success:
            # So here, because we were successful in connecting to our arduino, we can
            # serve up the web app version of Neptune.
            return "<html><head><title>Neptune Pool and Spa Automation</title></head>"\
                   "<body>Hello <b>friend</b> and welcome to Neptune Pool and Spa Automation!"\
                   "</body></html>"
        else:
            return "<html><head><title>Neptune Pool and Spa Automation</title></head>"\
                   "<body>There was an error while attempting to contact your Neptune "\
                   "Pool and Spa Automation device.<br><br>Please make sure that your device "\
                   "is on and connected to the internet.</body></html>"

    def getChild(self, name, request):
        """
        Built-in method to resource.Resource defining how to associate incoming requests
        with child objects or itself.
        :param name: name of the child object to be called
        :type name: str
        :param request: incoming http request
        :return: self or appropriate child
        :rtype: resource.Resource
        """
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

class WebFetch(WebResource):
    """
    This object defines the Fetch child resource. Its job is simply to dump device
    information into the browser in the form of an XML etree for the user to read.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        request.setHeader('Content-Type', 'text/xml')
        # Load the device info
        ## I keep the device info in different places depending on the platform. This is a hacky
        ##  convenience and is not elegant code.
        if PLATFORM == "mac":
            tree = xmlEtree.parse('/Users/jisunstetson/allen/code/webpy/deviceInfo.xml')
        elif PLATFORM == "windows":
            tree = xmlEtree.parse('/Users/alji/Documents/neptune/main/deviceState.xml')

        # Parse the XML file and serve it as-is.
        root = tree.getroot()
        return(xmlEtree.tostring(root))

class WebSwitch(WebResource):
    """
    This object defines the Switch child resource. Its job is to manipulate switch-type devices
    based on incoming http requests.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        self.crown = NeptuneCrown()
        request.setHeader("content-type", "text/plain")
        data = request.args

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "0:Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "0:Authentication failed. Access denied."

        # Collect requested device ID and new value
        devId = data['dev'][0]
        value = data['to'][0]

        # Perform the device update
        (code, pretty) = self.crown.setSwitchDevice(devId, value, author='0001')
        if code:
            report = "1:%s\n  %s" % (pretty, code)
            self.serialProcess.serialWrite(code)
        else:
            report = "0:Serial Write failed. %s" % pretty
        return str(report)

class WebStep(WebResource):
    """
    This object defines the Step child resource. Its job is to manipulate step-type devices
    based on incoming http requests.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        self.crown = NeptuneCrown()
        request.setHeader("content-type", "text/plain")
        data = request.args

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "0:Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "0:Authentication failed. Access denied."

        # Collect requested device ID and new value
        devId = data['dev'][0]
        value = data['to'][0]

        # Perform the device update
        (code, pretty) = self.crown.setStepDevice(devId, value, author='0001')
        if code:
            report = "1:%s\n  %s" % (pretty, code)
        else:
            report = "0:Serial Write failed. %s" % pretty
        return str(report)

class WebSet(WebResource):
    """
    This object defines the Set child resource. Its job is to manipulate any type of
    device by setting a given attribute to a value provided through incoming http requests.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        self.crown = NeptuneCrown()
        request.setHeader("content-type", "text/plain")
        data = request.args

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "0:Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "0:Authentication failed. Access denied."

        # Collect requested device ID, attribute name, and new value
        devId = data['dev'][0]
        attrib = data['set'][0]
        value = data['to'][0]

        # Perform the device update
        (success,code) = self.crown.setDeviceAttribute(devId, attrib, value, author='0001')
        if success:
            return "1: Device %s, %s set to %s\n  %s" % (devId, attrib, value, code)
        else:
            return "0:Serial Write failed. %s" % code

class WebAdd(WebResource):
    """
    This object defines the Add child resource. Its job is to add new devices to the Neptune
    which will then receive default values.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        data = request.args

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "Authentication failed. Access denied."

        # Add configuration entry
        name = data['name']
        entryType = data['entryType'][0]
        # ALLEN - THIS CODE IS UNFINISHED
        # Add call to device addition in crown here.
        return "Adding config %s of type %s" % (name, entryType)

class WebRemove(WebResource):
    """
    This object defines the Remove child resource. Its job is to remove devices from the Neptune
    configuration.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        data = request.args

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "Authentication failed. Access denied."

        # Add configuration entry
        idno = data['idno'][0]
        # ALLEN - THIS CODE IS UNFINISHED
        # Add call to device removal in crown here.
        return "Removing config with id %s" % idno

class WebLog(WebResource):
    """
    This object defines the Log Entry child resource. Its job is to add an entry to the Neptune log.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        data = request.args

        print(data)

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "Authentication failed. Access denied. %s vs %s" % (securityCode, NPASASC)

        # Add configuration entry
        entry = data['entry'][0]
        now = dt.datetime.now()
        # ALLEN - THIS CODE IS UNFINISHED
        # Add call to add log entry here.
        return "Adding entry at %s to log: %s" % (now, entry)

class WebReadLog(WebResource):
    """
    ! UNFINISHED ! This object will provide users with a way to read through a whole log file
    in their browser.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        data = request.args

        if not data:
            return ''

        return "Not yet implemented."

class WebMap(WebResource):
    """
    This object defines the Map child resource. Initially intended to map out successful
    sensor updates in a graph, it can actually be used to fetch a log record of successful
    updates to any device.
    """
    def render_GET(self, request):
        """
        Built-in method to resource.Resource which defines what to do when asked to display
        via http.
        :param request: incoming http request
        :return: html markup
        :rtype: str
        """
        data = request.args
        request.setHeader("content-type", "text/plain")

        if not data:
            return ''

        # Verify authorized connection
        if not data.has_key("npasasc"):
            return "Authentication required. Access denied."
        securityCode = data['npasasc'][0]
        if securityCode != NPASASC:
            return "Authentication failed. Access denied."

        # Collect device ID
        devId = data['dev'][0]

        # Load the log
        ## ALLEN - this whole mess should be off-loaded to a method in a module
        logger = NeptuneLogger('0001')
        log = logger.getOrCreateLog()
        values = []
        for entry in log:
            if log[entry]['destination'] == devId:
                values.append((entry,log[entry]['success'][1].split()[-1]))
        return str(values)

###################################
## main
###################################
if __name__ == '__main__':
    # Serial
    ## Define our serial resource and spin up a connection to the Arduino
    print('About to open port %s' % COM_PORT)
    serialProcess = SerialResource()
    s = SerialPort(serialProcess, COM_PORT, reactor, baudrate=9600)


    # HTTP
    ## Define Web Resources and give them access to the serial process
    root = HttpResource()
    root.setSerial(serialProcess)
    webFetch = WebFetch()
    webFetch.setSerial(serialProcess)
    webSet = WebSet()
    webSet.setSerial(serialProcess)
    webSwitch = WebSwitch()
    webSwitch.setSerial(serialProcess)
    webStep = WebStep()
    webStep.setSerial(serialProcess)
    webAdd = WebAdd()
    webAdd.setSerial(serialProcess)
    webRemove = WebRemove()
    webRemove.setSerial(serialProcess)
    webLog = WebLog()
    webLog.setSerial(serialProcess)
    webReadLog = WebReadLog()
    webReadLog.setSerial(serialProcess)
    webMap = WebMap()
    webMap.setSerial(serialProcess)

    ## Add Web Resources to root
    root.putChild('fetch', webFetch)
    root.putChild('set', webSet)
    root.putChild('switch', webSwitch)
    root.putChild('step', webStep)
    root.putChild('add', webAdd)
    root.putChild('remove', webRemove)
    root.putChild('log', webLog)
    root.putChild('readlog', webReadLog)
    root.putChild('map', webMap)

    ## Add root to Site factory and add factory to reactor
    factory = server.Site(root)
    reactor.listenTCP(8080, factory)

    # Fire it up, Herb
    print("Running Neptune Serial service at: %s" % COM_PORT)
    if PLATFORM == "windows":
        address = "http://alji-hp610:8080/"
    if PLATFORM == "mac":
        address = "http://ji-sun-stetsons-computer.local:8080/"
    print("Running Neptune HTTP service at:\n\t%s" % address)

    reactor.run()
