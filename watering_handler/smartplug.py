import time
import logging
from pyHS100 import SmartPlug
from pyHS100.smartdevice import SmartDeviceException

class SmartPlugHandler:
    _plug = None
    _ipAddress = ""

    @property
    def isOn(self):
        return self._plug.state == "ON"

    def __init__(self, ipAddress):
        logging.info('Configure smart plug with ip address %s.' % ipAddress)
        self._ipAddress = ipAddress

    def connect(self):
        try:
            self._plug = SmartPlug(self._ipAddress)
        except SmartDeviceException:
            logging.warning("Can not connect with smart plug.")

    def disconnect(self):
        logging.info("Disconnect smart plug with ip address %s." % (self._ipAddress))
        if (self._plug.state == "ON"):
            self.turnOff()
        self._plug = None
    
    def repeat(self, amountOfRepeat, wateringDuration, delayBetweenWatering):
        try:
            self.connect()
            if self.isOn:
                self.turnOff()

            logging.info('Start repeating interval with smart plug %s.' % self._ipAddress)
            for i in range(0, amountOfRepeat):
                logging.info('Run in interval %s.' % (i))
                self.handleInterval(wateringDuration, delayBetweenWatering)
                
            logging.info('Finish repeating interval with smart plug %s.' % self._ipAddress)

            self.turnOff()
            self.disconnect()
        except:
            logging.info('Error while repeating interval with smart plug %s.' % self._ipAddress)

    def handleInterval(self, wateringDuration, delayBetweenWatering):
        self.turnOn()
        time.sleep(wateringDuration)
        
        self.turnOff()
        time.sleep(delayBetweenWatering)

    def turnOn(self):
        logging.info('Turn on smart plug with ip address %s.' % self._ipAddress)
        try:
            self._plug.turn_on()
        except SmartDeviceException:
            logging.error('Communication error with smart plug ip address %s. Maybe it is not connected anymore.' % self._ipAddress)

    def turnOff(self):
        logging.info('Turn off smart plug with ip address %s.' % self._ipAddress)
        try:
            self._plug.turn_off()
        except SmartDeviceException:
            logging.error('Communication error with smart plug ip address %s. Maybe it is not connected anymore.' % self._ipAddress)
