import binascii
import serial
from serial.tools import list_ports
import struct
import sys
import time

class UbxStream(object):
    def __init__(self, dev=None):
        
        self._ubox_synch = '\xb5b'
        
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

    def detect_ports(self):
        ports = list(serial.tools.list_ports.comports())
        if(len(ports) == 0):
            print("No ports detected")
        else:
            for i in ports:
                print(i.device)


    def read(self, timeout=5):
        self.dev.reset_input_buffer()
        now = time.time()
        counter = 0        
        while((time.time() - now) < timeout):    
            if self._dev.in_waiting > 0:
                if counter < 2:
                    try:
                        s = self.dev.read()
                        if s == self._ubox_synch[counter]:
                            counter += 1
                        elif s == self._ubox_synch[0]:
                            counter = 1
                        else:
                            counter = 0
                    except serial.serialutil.SerialException:
                        print("Somethig went wrong")
                    
                else:
                    ubx_class = binascii.hexlify(self.dev.read())
                    ubx_id = binascii.hexlify(self.dev.read())
                    return UbxMessage(ubx_class, ubx_id, dev=self.dev)

        print("Connection timed out..")

    
    def enable_message(self, msgClass, msgId):
        msg = UbxMessage('06', '01', msg_type="tx", msgClass=msgClass, msgId=msgId, ioPorts=[0, 1, 0, 0, 0, 0])
        self.dev.write(msg.msg)
        return msg

    def disable_message(self, msgClass, msgId):
        msg = UbxMessage('06', '01', msg_type="tx", msgClass=msgClass, msgId=msgId, ioPorts=[0, 0, 0, 0, 0, 0])
        self.dev.write(msg.msg)
        return msg

    def reset_config(self):
        clearMask, saveMask, loadMask, deviceMask = [255, 255, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [3]
        msg = UbxMessage('06','09', msg_type="tx", clearMask=clearMask, saveMask=saveMask, loadMask=loadMask, deviceMask=deviceMask)
        self.dev.write(msg.msg)
        return msg
    
    def save_config(self):
        clearMask, saveMask, loadMask, deviceMask = [0, 0, 0, 0], [255, 255, 0, 0], [0, 0, 0, 0], [19]
        msg = UbxMessage('06','09', msg_type="tx", clearMask=clearMask, saveMask=saveMask, loadMask=loadMask, deviceMask=deviceMask)
        self.dev.write(msg.msg)
        return msg
        
    def load_config(self):
        clearMask, saveMask, loadMask, deviceMask = [0, 0, 0, 0], [0, 0, 0, 0], [255, 255, 0, 0], [19]
        msg = UbxMessage('06','09', msg_type="tx", clearMask=clearMask, saveMask=saveMask, loadMask=loadMask, deviceMask=deviceMask)
        self.dev.write(msg.msg)
        return msg

    def nav_config(self, dynModel):
        msg = UbxMessage('06', '24', msg_type="tx", dynModel=dynModel)
        self.dev.write(msg.msg)
        return msg

            
class UbxMessage(object):
    def __init__(self, ubx_class, ubx_id, msg_type="rx", **kwargs):
        if(msg_type == "rx"):
            print("Receiving")
            #NAV
            if(ubx_class == '01'):
                print("{} {}".format(ubx_class, ubx_id))
                
                message = {'02': lambda: self.__ubx_NAV_POSLLH(kwargs["dev"]),
                           '04': lambda: self.__ubx_NAV_DOP(kwargs["dev"]),
                           '06': lambda: self.__ubx_NAV_SOL(kwargs["dev"]),
                           '07': lambda: self.__ubx_NAV_PVT(kwargs["dev"])}
                message[ubx_id]()

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
                
           
        elif(msg_type == "tx"):
            print("Transmitting")
            #NAV
            if(ubx_class == '01'):
                print("")
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
                print("{} {}".format(ubx_class, ubx_id))
                
                message = {'01': lambda: self.__ubx_CFG_MSG(kwargs["msgClass"], kwargs["msgId"], kwargs["ioPorts"]),
                           '09': lambda: self.__ubx_CFG_CFG(kwargs["clearMask"], kwargs["saveMask"], kwargs["loadMask"], kwargs["deviceMask"]),
                           '24': lambda: self.__ubx_CFG_NAV5(kwargs["dynModel"])
                }
                message[ubx_id]()
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
            print("Message type not supported.")
            

    ## UBX-NAV 0x01 ##

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
                self.ubx_class = '01'
                self.ubx_id = '02'

            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    
    # time_of_week in ms / Dilution of Precision
    # DOP is Dimensionless / scaled by factor 100
    # Geometric / Position / Time / Vertical / Horizontal / Northing / Easting
    def __ubx_NAV_DOP(self, dev):
        payload = dev.read(size=20)
        if self.__calc_checksum(1, 4, payload, dev):
            try:
                payload = payload[2:]
                self.iTOW, self.gDOP, self.pDOP, self.tDOP, self.vDOP, self.hDOP, self.nDOP, self.eDOP = struct.unpack('=L7H', payload)
                self.ubx_class = '01'
                self.ubx_id = '04'
                
            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

                
    # Time_of_week in ms / Fractional time_of_week ns / Week number
    # GPS Fix (6 valid types depending on status) / Fix status flags (4 types)
    # ECEF X cm / ECEF Y cm / ECEF Z cm / Position Accuracy cm
    # ECEF-Velocity X cm/s / ECEF-Velocity Y cm/s / ECEF-Velocity Z cm/s
    # Speed Accuracy cm/s / Position DOP (scale 0.01)
    # reserved / number of SV's used / reserved
    def __ubx_NAV_SOL(self, dev):
        payload = dev.read(size=54)
        if(self.__calc_checksum(1, 6, payload, dev)):
            try:
                payload = payload[2:]
                self.iTOW, self.fTOW, self.week, self.gpsFix, self.flags, self.ecefX, self.ecefY, self.ecefZ, self.pAcc, self.ecefVX, self.ecefVY, self.ecefVZ, self.sAcc, self.pDOP, reserved1, self.numSV, reserved21, reserved22, reserved23, reserved24 = struct.unpack('=LlhBB3lL3lLH6B', payload)
                self.ubx_class = '01'
                self.ubx_id = '06'
                
            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))



    # Time of week in ms / Year(UTC) / Month (UTC 1..12) / Day (1..31)
    # Hour (0..23) / Minute (0..59) / Seconds (0..60) / Validity Flags
    # Time Accuracy Estimate in ns / Fraction of second (-1e9..1e9)
    # GNSS Fix Type / Fix Status Flags / Other Flags / Number of Sattelites
    # Longitude in deg (1e-7) / Latitude in deg (1e-7) / Height Ellipsoid in mm
    # Height Sea Level in mm / Horizontal Accuracy in mm / Vertical Accuracy in mm
    # North Velocity mm s^-1 / East Velocity mm s^-1 / Down Velocity mm s^-1
    # Ground speed in mm s^-1 / Heading of Motion in deg (1e-5) / Speed accuracy mm s^-1
    # Heading accuracy estimate deg (1e-5) / Position DOP (0.01) / Reserved space
    # Heading of Vehicle in deg (1e-5) / Magnetic Declination in deg (1e-2) <-+ Accuracy in deg
    def __ubx_NAV_PVT(self, dev):
        payload = dev.read(size=94)
        if(self.__calc_checksum(1, 7, payload, dev)):
            try:
                payload = payload[2:]
                self.iTOW, self.year, self.month, self.day, self.hour, self.minute, self.second, self.valid, self.tAcc, self.nano, self.fixType, self.flags, self.flags2, self.numSV, self.lon, self.lat, self.height, self.hMSL, self.hAcc, self.vAcc, self.velN, self.velE, self.velD, self.gSpeed, self.headMot, self.sAcc, self.headAcc, self.pDOP, reserved11, reserved12, reserved13, reserved14, reserved15, reserved16,  self.headVeh, self.magDec, self.magAcc = struct.unpack('=LH5BBLlB2BB4l2L5lLLH6BlhH', payload)

                self.ubx_class = '01'
                self.ubx_id = '07'
            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

            

                
    ## UBX-CFG 0x06 ##
    
    # UBX-CFG-MSG (0x06 0x01)
    def __ubx_CFG_MSG(self,  msgClass, msgId, ioPorts):
        header, ubx_class, ubx_id, length = 46434, 6, 1, 8
        payload = [length, 0, msgClass, msgId] + ioPorts
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload, returnval=True)
        try:
            self.msg = struct.pack('>H14B', header, ubx_class, ubx_id, length, 0,  msgClass, msgId, ioPorts[0], ioPorts[1], ioPorts[2], ioPorts[3], ioPorts[4], ioPorts[5], checksum[0], checksum[1])
            self.ubx_class = '06'
            self.ubx_id = '01'
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))



    ## UBX-CFG-CFG (0x06 0x09)
    def __ubx_CFG_CFG(self, clearMask, saveMask, loadMask, deviceMask):
        header, ubx_class, ubx_id, length = 46434, 6, 9, 13
        payload = [length, 0] + clearMask + saveMask + loadMask + deviceMask
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload, returnval=True)
        payload = payload + checksum
        try:
            self.msg = struct.pack('>H19B', header, ubx_class, ubx_id, *payload)
            self.ubx_class = '06'
            self.ubx_id = '09'
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    ## UBX-CFG-NAV5 (0x06 0x24)
    #  ! only currently configures dynModel ! <- Needed for high altitude
    def __ubx_CFG_NAV5(self, dynModel):
        header, ubx_class, ubx_id, length = 46434, 6, 36, 36
        body = [3, 0, 0, 0, 0, 16, 39, 0, 0, 5, 0, 250, 0, 250, 0, 100, 0, 44, 1, 0, 60, 0, 0, 0, 0, 200, 0, 0, 0, 0, 0, 0, 0]
        payload = [length, 0] + [255, 255] + [dynModel] + body
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload, returnval=True)
        payload = payload + checksum
        try:
            self.msg = struct.pack('>H42B', header, ubx_class, ubx_id, *payload)
            self.ubx_class = '06'
            self.ubx_id = '24'
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
        
