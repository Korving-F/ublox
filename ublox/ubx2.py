import binascii
import serial
from serial.tools import list_ports
import struct
import sys

class ubxStream():
    def __init__(self, serial=None):
        
        self.serial = serial


    @property
    def serial(self):
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

        

class ubxMessage():
    def __init__(self, ubx_class=None, ubx_id=None):
        
