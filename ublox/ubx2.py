import binascii
import serial
from serial.tools import list_ports
import struct
import sys

class ubxStream():
    def __init__(self, dev=None):
        
        self.dev = dev


    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

        

class ubxMessage():
    def __init__(self, ubx_class=None, ubx_id=None):
        
