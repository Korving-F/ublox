import binascii
import serial
from serial.tools import list_ports
import struct
import sys
import time

# Extend from object to make it a new-style class -> enables descriptors
class UbxStream(object):
    def __init__(self, dev=None):
        
        self.ubox_synch = '\xb5b'
        
        if(dev==None):
            self.dev = serial.Serial(timeout=1)
        else:
            self.dev = dev
            
        try:
            if(self._dev.open):
                self.baudrate = dev.baudrate
        except AttributeError:
            print("Serial connection has not been properly initialized yet.")
    
    @property
    def dev(self):
        return self._dev

    @dev.setter
    def dev(self, dev):
        x = dev.__class__.__module__ + "." + dev.__class__.__name__
        supported = ["serial.serialcli.Serial", "serial.serialwin32.Serial",
                     "serial.serialposix.Serial", "serial.serialjava.Serial"]
        if(x in supported):
            self._dev = dev
        else:
            print("This connection is not supported")

    @property
    def baudrate(self):
        try:
            if(self._dev.open):
                return self._baudrate
        except AttributeError:
            print("Serial connection has not been initialized or assigned a baudrate yet.")
            
    @baudrate.setter
    def baudrate(self, rate):
        try:
            if(self._dev.isOpen()):
                old_baudrate = self._dev.baudrate
                self._dev.baudrate = rate
                self._baudrate = rate
                # Send ubx-Message here
            else:
                print("Serial connection has not been opened yet")
                
        except AttributeError:
            print("Serial connection has not been initialized or assigned a port yet.")


    def read(self, timeout=5):
        #flush device first
        self.dev.reset_input_buffer()
        now = time.time()
        counter = 0        
        while((time.time() - now) < timeout):    
            if self._dev.in_waiting > 0:
                if counter < 2:
                    try:
                        s = self.dev.read()
                        if s == self.ubox_synch[counter]:
                            counter += 1
                        elif s == self.ubox_synch[0]:
                            counter = 1
                        else:
                            counter = 0
                    except serial.serialutil.SerialException:
                        print("Somethig went wrong")
                    
                else:
                    ubx_class = binascii.hexlify(self.dev.read())
                    ubx_id = binascii.hexlify(self.dev.read())
                    return UbxMessage(ubx_class, ubx_id, dev=self.dev)

            
class UbxMessage(object):
    def __init__(self, ubx_class, ubx_id, msg_type="rx", **kwargs):
        if(msg_type == "rx"):
            print("Receiving")

            #NAV
            if(ubx_class == '01'):
                print("{} {}".format(ubx_class, ubx_id))
                #try:
                message = {'02': lambda: self.__ubx_NAV_POSLLH(kwargs["dev"]),
                           '04': lambda: self.__ubx_NAV_DOP(kwargs["dev"]),
                           '06': lambda: self.__ubx_NAV_SOL(kwargs["dev"]),
                           '07': lambda: self.__ubx_NAV_PVT(kwargs["dev"])}
                message[ubx_id]()
               # except NameError:
                #    print("Serial device was not passed through.")
            #RXM
            elif(ubx_class == '02'):
                print("")
            #INF
            elif(ubx_class == '04'):
                print("")
            #ACK
            elif(ubx_class == '05'):
                print("")
            #CFG
            elif(ubx_class == '06'):
                print("")
            #UPD
            elif(ubx_class == '09'):
                print("")
            #MON
            elif(ubx_class == '0A'):
                print("")
            #AID
            elif(ubx_class == '0B'):
                print("")
            #TIM
            elif(ubx_class == '0D'):
                print("")
            #ESF
            elif(ubx_class == '10'):
                print("")
            #MGA
            elif(ubx_class == '13'):
                print("")
            #LOG
            elif(ubx_class == '21'):
                print("")
            #SEC
            elif(ubx_class == '27'):
                print("")
            #HNR
            elif(ubx_class == '28'):
                print("")
            else:
                print("Unsuported message class")
                raise TypeError
                
           
        else:
            print("Transmitting")
            


    # time_of_week in ms / longitude in deg / latitude in deg
    # height ellipsoid in mm / height mean sea level mm
    # horizontal accuracy in mm / vertical accuracy in mm

    def __ubx_NAV_POSLLH(self, dev):
        payload = dev.read(size=30)
        if self.__calc_checksum(1, 2, payload, dev):
            try:
                payload = payload[2:]
                # Remove padding (=) introduced by struct for processor optimization
                self.iTOW, self.lon, self.lat, self.height, self.hMSL, self.hAcc, self.vAcc = struct.unpack('=LllllLL', payload)

            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    
    
    # Checksum is calculated over class/id/length/payload of packet
    # using 8-bit Fletcher Algorithm (also used in TCP) RFC 1145
    # bitmask 0xFF == modulus 256
    # It might be that the modulo needs to be calculated after full operations
    # This might become relavant when overflow occurs in check1 <- NMEA messages like CFG use class/id (xF1 x41)
    def __calc_checksum(self, ubx_class, ubx_id, payload, dev=None, returnval=False):
        
        check1 = (ubx_class + ubx_id) % 256
        check2 = ((2*ubx_class) + ubx_id) % 256
        
        if(returnval==False):
            chk1 = int(dev.read().encode('hex'), 16)
            chk2 = int(dev.read().encode('hex'), 16)
            
            for i in range(0, len(payload)):
                check1 = (check1 + int(payload[i].encode('hex'), 16)) % 256
                check2 = (check1 + check2) % 256
                
            if chk1==check1 and chk2==check2:
                return True
            else:
                print("Checksum is incorrect")
                return False
        else:
            for i in range(0, len(payload)):
                check1 = (check1 + payload[i]) % 256
                check2 = (check1 + check2) % 256
                
            result = [check1, check2]
            return result
        
