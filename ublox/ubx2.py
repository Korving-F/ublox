import binascii
import serial
from serial.tools import list_ports
import struct
import sys

# Extend from object to make it a new-style class -> enables descriptors
class UbxStream(object):
    def __init__(self, serial=None):
        self._serial = serial
        try:
            if(serial.open):
                self._baudrate = serial.baudrate
        except AttributeError:
            print("Serial connection has not been properly initialized yet.")
            


    @property
    def serial(self):
        print("Hello")
        return self._serial

    @serial.setter
    def serial(self, serial):
        self._serial = serial

    @property
    def baudrate(self):
        try:
            return self._baudrate
        except AttributeError:
            print("Serial connection has not been initialized or assigned a baudrate yet.")
            
    @baudrate.setter
    def baudrate(self, rate):
        print("meh")
        try:
            self._baudrate = rate
        # add code to update serial.baudrate / send ubx-cfg message
        except AttributeError:
            print("Serial connection has not been initialized or assigned a baudrate yet.")


class UbxMessage(object):
    def __init__(self, ubx_class=None, ubx_id=None):
        print("Yeah!")
