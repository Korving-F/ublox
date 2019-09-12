import struct
import sys
import time
import binascii
import serial
from serial.tools import list_ports

class UbxStream(object):
    def __init__(self, dev=None):
        # pyserial 3.x has min requirement python2.7
        # read() returns string in 2.7, bytes object otherwise
        if sys.version_info[0] < 3:
            if sys.version_info[1] < 7:
                raise ValueError('This library is based on pyserial v3.x. Python 2.7 or higher is required.')
            self._version = 2
            self._ubox_synch = '\xb5b'
        else:
            self._version = 3
            self._ubox_synch = ['b5', '62']

        if(dev):
            self.dev = dev
        else:
            self.dev = serial.Serial(timeout=1)

        try:
            if(self._dev.open):
                self.baudrate = dev.baudrate
        except AttributeError:
            print("Serial Port is closed; open before using.")


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
            else:
                print("Port is closed.")
        except AttributeError:
            print("Serial connection has not been initialized or assigned a baudrate yet.")


    @baudrate.setter
    def baudrate(self,baudrate):
        y = UbxMessage('06','00', msg_type="tx", rate=baudrate, version=self._version)
        try:
            if(self.dev.writable):
                if(self.dev.write(y.msg)):
                    time.sleep(1)  # Sleep to make sure buffer gets written!
                    self._baudrate = baudrate
                    self._dev.baudrate = baudrate

        except AttributeError:
            print("Serial connection has not been initialized or assigned a port yet.")


    def detect_ports(self):
        ports = list(serial.tools.list_ports.comports())
        if(len(ports) == 0):
            print("No ports detected")
        else:
            for i in ports:
                print(i.device)


    def read(self, timeout=3, reset=True):
        if(reset):
            self.dev.reset_input_buffer()

        now = time.time()
        counter = 0
        while(time.time() - now) < timeout:
            if self._dev.in_waiting > 0:
                if counter < 2:
                    try:
                        s = self.dev.read()
                        if self._version == 3:
                            s = binascii.hexlify(s).decode('utf-8')

                        if s == self._ubox_synch[counter]:
                            counter += 1
                        elif s == self._ubox_synch[0]:
                            counter = 1
                        else:
                            counter = 0
                    except serial.serialutil.SerialException:
                        print("Somethig went wrong")

                else:
                    if self._version == 3:
                        ubx_class = binascii.hexlify(self.dev.read()).decode('utf-8')
                        ubx_id = binascii.hexlify(self.dev.read()).decode('utf-8')
                    else:
                        ubx_class = binascii.hexlify(self.dev.read())
                        ubx_id = binascii.hexlify(self.dev.read())

                    return UbxMessage(ubx_class, ubx_id, dev=self.dev, version=self._version)

        print("Connection timed out..")


    def enable_message(self, msgClass, msgId):
        msg = UbxMessage('06', '01', msg_type="tx", msgClass=msgClass, msgId=msgId, ioPorts=[0, 1, 0, 0, 0, 0])
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg


    def disable_message(self, msgClass, msgId):
        #msg = UbxMessage('06', '01', msg_type="tx", msgClass=msgClass, msgId=msgId, ioPorts=[0, 0, 0, 0, 0, 0])
        msg = UbxMessage('06', '01', msg_type="tx", msgClass=msgClass, msgId=msgId, ioPorts=[0, 0, 0, 0, 0, 0])
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg

    def cfg_rate(self,rate):
        msg = UbxMessage('06','08', msg_type="tx", rate=rate, timeRef=0)
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg

    def reset_config(self):
        clearMask, saveMask, loadMask, deviceMask = [255, 255, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [3]
        msg = UbxMessage('06','09', msg_type="tx", clearMask=clearMask, saveMask=saveMask, loadMask=loadMask, deviceMask=deviceMask)
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg


    def save_config(self):
        clearMask, saveMask, loadMask, deviceMask = [0, 0, 0, 0], [255, 255, 0, 0], [0, 0, 0, 0], [19]
        #clearMask, saveMask, loadMask, deviceMask = [0, 0, 0, 0], [255, 255, 0, 0], [0, 0, 0, 0], [255]
        msg = UbxMessage('06','09', msg_type="tx", clearMask=clearMask, saveMask=saveMask, loadMask=loadMask, deviceMask=deviceMask)
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg


    def load_config(self):
        clearMask, saveMask, loadMask, deviceMask = [0, 0, 0, 0], [0, 0, 0, 0], [255, 255, 0, 0], [19]
        msg = UbxMessage('06','09', msg_type="tx", clearMask=clearMask, saveMask=saveMask, loadMask=loadMask, deviceMask=deviceMask)
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg


    def nav_config(self, dynModel):
        msg = UbxMessage('06', '24', msg_type="tx", dynModel=dynModel)
        self.dev.write(msg.msg)
        if(self.__confirmation()):
            return msg


    # diables all NMEA messages by default using ubx class / ids
    # 0xF0 = 240 / 0xF1 = 241
    # NMEA Messages:
    # class 0xF0: 0A, 09, 00, 01, 0D, 06, 02, 07, 03, 04, 41, 0F, 05, 08
    # class 0xF1: 00, 03, 04
    def disable_NMEA(self):
        classes = [240, 241]
        ids1 = [10, 9, 0, 1, 13, 6, 2, 7, 3, 4, 65, 15, 5, 8]
        ids2 = [0, 3, 4]
        counter = 0
        string = ""

        for i in ids1:
            val = False
            while(val == False):
                val = self.disable_message(classes[0], i)
                if(val):
                    string += "Class: {} ID: {} // ".format(classes[0], i)
                    counter += 1
                    break

        for i in ids2:
            val = False
            while(val == False):
                val = self.disable_message(classes[1], i)
                if(val):
                    string += "Class: {} ID: {} // ".format(classes[1], i)
                    counter += 1
                    break

        print("Counter: {}".format(counter))
        print(string)


    def __confirmation(self):
        now = time.time()
        while(time.time() - now < 5):
            answer = self.read(reset=False)
            try:
                if(answer):
                    if(answer.ubx_class=='05' and answer.ubx_id=='01'):
                        print("Acknowledged. CLS:{} ID:{}".format(answer.clsID, answer.msgID))
                        return True
                    elif(answer.ubx_class=='05' and answer.ubx_id=='00'):
                        print("Not acknowledged. CLS:{} ID:{}".format(answer.clsID, answer.msgID))
                        return False
            except AttributeError:
                pass

        print("Message not received")
        return False


class UbxMessage(object):
    def __init__(self, ubx_class, ubx_id, msg_type="rx", **kwargs):
        if(msg_type == "rx"):
            self._version = kwargs["version"]
            print("Receiving")
            print("{} {}".format(ubx_class, ubx_id))
            #NAV
            if(ubx_class == '01'):
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
                message = {'01': lambda: self.__ubx_ACK_ACK(kwargs["dev"]),
                           '00': lambda: self.__ubx_ACK_NAK(kwargs["dev"])}
                message[ubx_id]()

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

                message = {'00': lambda: self.__ubx_CFG_PRT(kwargs["rate"]),
                           '01': lambda: self.__ubx_CFG_MSG(kwargs["msgClass"], kwargs["msgId"], kwargs["ioPorts"]),
                           '08': lambda: self.__ubx_CFG_RATE(kwargs["rate"], kwargs["timeRef"]),
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
        payload_cpy = payload

        if self.__validate_checksum(1, 2, payload, dev):
            try:
                payload_cpy = payload_cpy[2:]
                # Remove padding (=) introduced by struct for processor optimization
                self.iTOW, self.lon, self.lat, self.height, self.hMSL, self.hAcc, self.vAcc = struct.unpack('=LllllLL', payload_cpy)
                self.ubx_class = '01'
                self.ubx_id = '02'

            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))



    # time_of_week in ms / Dilution of Precision
    # DOP is Dimensionless / scaled by factor 100
    # Geometric / Position / Time / Vertical / Horizontal / Northing / Easting
    def __ubx_NAV_DOP(self, dev):
        payload = dev.read(size=20)
        payload_cpy = payload

        if self.__validate_checksum(1, 4, payload, dev):
            try:
                payload_cpy = payload_cpy[2:]
                self.iTOW, self.gDOP, self.pDOP, self.tDOP, self.vDOP, self.hDOP, self.nDOP, self.eDOP = struct.unpack('=L7H', payload_cpy)
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
        payload_cpy = payload

        if(self.__validate_checksum(1, 6, payload, dev)):
            try:
                payload_cpy = payload_cpy[2:]
                self.iTOW, self.fTOW, self.week, self.gpsFix, self.flags, self.ecefX, self.ecefY, self.ecefZ, self.pAcc, self.ecefVX, self.ecefVY, self.ecefVZ, self.sAcc, self.pDOP, reserved1, self.numSV, reserved21, reserved22, reserved23, reserved24 = struct.unpack('=LlhBB3lL3lLH6B', payload_cpy)
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
        payload_cpy = payload

        if(self.__validate_checksum(1, 7, payload, dev)):
            try:
                payload_cpy = payload[2:]
                self.iTOW, self.year, self.month, self.day, self.hour, self.minute, self.second, self.valid, self.tAcc, self.nano, self.fixType, self.flags, self.flags2, self.numSV, self.lon, self.lat, self.height, self.hMSL, self.hAcc, self.vAcc, self.velN, self.velE, self.velD, self.gSpeed, self.headMot, self.sAcc, self.headAcc, self.pDOP, reserved11, reserved12, reserved13, reserved14, reserved15, reserved16,  self.headVeh, self.magDec, self.magAcc = struct.unpack('=LH5BBLlB2BB4l2L5lLLH6BlhH', payload_cpy)

                self.ubx_class = '01'
                self.ubx_id = '07'
            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    ## UBX-ACK 0x05 ##

    # UBX-ACK-ACK (0x05 0x01)
    def __ubx_ACK_ACK(self, dev):
        payload = dev.read(size=4)
        payload_cpy = payload

        if(self.__validate_checksum(5, 1, payload, dev)):
            try:
                payload_cpy = payload_cpy[2:]
                self.clsID, self.msgID = struct.unpack('=BB', payload_cpy)
                self.clsID, self.msgID = hex(self.clsID), hex(self.msgID)
                self.ubx_class = '05'
                self.ubx_id = '01'

            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    # UBX-ACK-NAK (0x05 0x00)
    def __ubx_ACK_NAK(self, dev):
        payload = dev.read(size=4)
        payload_cpy = payload

        if(self.__validate_checksum(5, 0, payload, dev)):
            try:
                payload_cpy = payload_cpy[2:]
                self.clsID, self.msgID = struct.unpack('=BB', payload_cpy)
                self.clsID, self.msgID = hex(self.clsID), hex(self.msgID)
                self.ubx_class = '05'
                self.ubx_id = '00'

            except struct.error:
                print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))



    ## UBX-CFG 0x06 ##

    # UBX-CFG-PRT (0x06 0x00)
    # Only support for UART atm -> alter input to cover DDC(I2C) / USB / SPI
    def __ubx_CFG_PRT(self, rate):
        header, ubx_class, ubx_id, length, uart_port = 46434, 6, 0, 20, 1

        rate = hex(rate)
        rate = rate[2:]
        while(len(rate) < 8):
            rate = '0' + rate

        rate1, rate2, rate3, rate4 = int(rate[-2:], 16), int(rate[-4:-2], 16), int(rate[2:4], 16), int(rate[:2], 16)

        payload = [length, 0, uart_port, 0, 0, 0, 208, 8, 0, 0, rate1, rate2, rate3, rate4, 7, 0, 3, 0, 0, 0, 0, 0]
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload)
        payload = payload + checksum
        try:
            self.msg = struct.pack('>H26B', header, ubx_class, ubx_id, *payload)
            self.ubx_class = '06'
            self.ubx_id = '00'
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    # UBX-CFG-MSG (0x06 0x01)
    def __ubx_CFG_MSG(self,  msgClass, msgId, ioPorts):
        header, ubx_class, ubx_id, length = 46434, 6, 1, 8
        payload = [length, 0, msgClass, msgId] + ioPorts
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload)
        try:
            self.msg = struct.pack('>H14B', header, ubx_class, ubx_id, length, 0,  msgClass, msgId, ioPorts[0], ioPorts[1], ioPorts[2], ioPorts[3], ioPorts[4], ioPorts[5], checksum[0], checksum[1])
            self.ubx_class = '06'
            self.ubx_id = '01'

        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    # UBX-CFG-RATE (0x06 0x08)
    def __ubx_CFG_RATE(self, rate, timeRef):
        header, ubx_class, ubx_id, length = 46434, 6, 8, 6

        rate = hex(rate)
        rate = rate[2:]
        while(len(rate) < 4):
            rate = '0' + rate

        rate1, rate2 = int(rate[2:4], 16), int(rate[:2], 16)

        navRate = 1 # according to ublox ICD this value is a don't care
        payload = [length, 0, rate1, rate2, navRate, 0, 0, timeRef]
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload)
        payload = payload + checksum
        try:
            self.msg = struct.pack('>H12B', header, ubx_class, ubx_id, *payload)
            self.ubx_class = '06'
            self.ubx_id = '08'
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    ## UBX-CFG-CFG (0x06 0x09)
    def __ubx_CFG_CFG(self, clearMask, saveMask, loadMask, deviceMask):
        header, ubx_class, ubx_id, length = 46434, 6, 9, 13
        payload = [length, 0] + clearMask + saveMask + loadMask + deviceMask
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload)
        payload = payload + checksum
        try:
            self.msg = struct.pack('>H19B', header, ubx_class, ubx_id, *payload)
            self.ubx_class = '06'
            self.ubx_id = '09'
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    ## UBX-CFG-NAV5 (0x06 0x24)
    #  ! only currently configures dynModel ! <- Dynmodel = 6/7/8  Needed for high altitude 50km
    def __ubx_CFG_NAV5(self, dynModel):
        header, ubx_class, ubx_id, length = 46434, 6, 36, 36
        body = [3, 0, 0, 0, 0, 16, 39, 0, 0, 5, 0, 250, 0, 250, 0, 100, 0, 44, 1, 0, 60, 0, 0, 0, 0, 200, 0, 0, 0, 0, 0, 0, 0]
        payload = [length, 0] + [255, 255] + [dynModel] + body
        checksum = self.__calc_checksum(ubx_class, ubx_id, payload)
        payload = payload + checksum
        try:
            self.msg = struct.pack('>H42B', header, ubx_class, ubx_id, *payload)
            self.ubx_class = '06'
            self.ubx_id = '24'
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    def __calc_checksum(self, ubx_class, ubx_id, payload):
        check1 = (ubx_class + ubx_id) % 256
        check2 = ((2*ubx_class) + ubx_id) % 256

        for i in range(0, len(payload)):
            check1 = (check1 + payload[i]) % 256
            check2 = (check1 + check2) % 256

        result = [check1, check2]
        return result


    def __validate_checksum(self, ubx_class, ubx_id, payload, dev):
        check1 = (ubx_class + ubx_id) % 256
        check2 = ((2*ubx_class) + ubx_id) % 256

        if self._version == 3:
            chk1 = dev.read()[0]
            chk2 = dev.read()[0]

            for i in range(0, len(payload)):
                check1 = (check1 + payload[i]) % 256
                check2 = (check1 + check2) % 256

        else:
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
