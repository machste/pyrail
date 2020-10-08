import logging
import serial

from pyrail.exc.error import Error as BaseError

_log = logging.getLogger(__name__)


class DCCpp(object):
    """Implementaion of the Arduino DCC++ Base Station

    See also: https://github.com/DccPlusPlus/BaseStation/wiki

    """

    DEFAULT_PORT = "auto"
    DEFAULT_BAUDRATE = 115200

    def __init__(self, port=None, baudrate=None):
        self.port = port or DCCpp.DEFAULT_PORT
        self.baudrate = baudrate or DCCpp.DEFAULT_BAUDRATE
        self._com = None

    @property
    def connected(self):
        return self._com is not None

    def connect(self):
        if not self.connected:
            # Open serial port
            try:
                _log.debug("Connecting to '%s' at %s baud ..." % (self.port,
                        self.baudrate))
                self._com = serial.Serial(self.port, self.baudrate)
            except serial.SerialException as ex:
                self._com = None
                raise DCCpp.Error("Unable to connect %s: %s" % (self, ex))
        else:
            _log.warn("%s already connected!" % self)
        return self.connected

    def disconnect(self):
        if self.connected:
            _log.debug("Disconnecting from '%s' ..." % self.port)
            self._com.close()
        self._com = None
        return not self.connected

    def send_command(self, name, *args):
        if self.connected:
            if (len(args) == 0):
                cmd = "<%s>" % name
            else:
                cmd = "<%s %s>" % (name, " ".join(map(str, args)))
            _log.debug("Send command: '%s'" % cmd)
            self._com.write(cmd.encode("ascii", "ignore"))
            return True
        raise DCCpp.Error("DCC++ Station is not connected!")

    def status(self):
        self.send_command("s")

    def power_on(self):
        self.send_command("1")

    def power_off(self):
        self.send_command("0")

    def power(self, state):
        self.power_on() if state else self.power_off()

    def throttle(self, register, cab, speed):
        if speed < 0:
            direction = 0
            speed = -speed
        else:
            direction = 1
        self.send_command("t", register, cab, speed, direction)

    def function(self, cab, fn):
        self.send_command("f", cab, fn)

    def turnout(self, addr, state):
        self.send_command("a", addr, 0, state)

    def write(self, cv, value, addr=0):
        if addr == 0:
            self.send_command("W", cv, value, 0, 0)
        else:
            self.send_command("w", addr, cv, value)

    def __repr__(self):
        return "<DCCpp<connected=%s>(port='%s', baudrate='%s')>" % (
                self.connected, self.port, self.baudrate)


    class Error(BaseError):
        pass
