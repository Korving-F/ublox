import binascii
import serial
from serial.tools import list_ports
import struct
import sys

# Connect gps module to rasppi / ssh to it to configure

# UBox proprietary software -> wine ~/.wine/DriveC/ProgramFiles/x86/ucenter v8.16/ucenter.exe or smt..
# Create symbolic link between serial device and .wine/dosdevices/com[number]

# class connection? x = ubox.connection() -> x.configure(protocol/baudrate) -> x.last_message
# x.configure(messages=reset/mask/inverted_mask)

# print(u'\xb5b')
# Checkout multi-threading
# autodetecting of device file here
# print(y.decode("iso8859"))

# Suitable for HAB Usage Max Altitude 50,000 meters / 164041 feet  in Flight Mode.
# How to configure for flight mode? / Hab usage?

#59.4 / 24.6 <- lat lon

def main():
    dev = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
    ubox_synch = '\xb5b'
    counter = 0
    enable_message(dev, 1, 6)
    #disable_message(dev, 1, 7)
    # Run this loop for a while and occasionally flush the file? in case reading is slower than writing from device
    while(True):    
        if dev.in_waiting > 0:
            if counter < 2:
                try:
                    s = dev.read()
                    if s == ubox_synch[counter]:
                        counter += 1
                    elif s == ubox_synch[0]:
                        counter = 1
                    else:
                        counter = 0
                except serial.serialutil.SerialException:
                    print("Somethig went wrong")
                    
            else:
                ubx_class = binascii.hexlify(dev.read())
                ubx_id = binascii.hexlify(dev.read())
                print("UBX Class: {} / UBX ID: {}".format(ubx_class, ubx_id))
                
                try:
                    # package = ubxMessage(ubx_class, ubx_id)
                    # package.formattedContent
                    # 
                    result = {'02': lambda: ubx_NAV_POSLLH(dev),
                              '04': lambda: ubx_NAV_DOP(dev),
                              '06': lambda: ubx_NAV_SOL(dev),
                              '07': lambda: ubx_NAV_PVT(dev)
                    }
                    result[ubx_id]()
                except KeyError:
                    print("Invalid packet id")

                counter = 0

                
# UBX-CFG-CFG Message should go here (x06 x09)
def save_configuration(dev):
    header, ubx_class, ubx_id, length = 46434, 6, 9, 8
    # See appropriate masking

    
# Creates UBX-CFG-MSG
def enable_message(dev,  msgClass, msgId):
    header, ubx_class, ubx_id, length = 46434, 6, 1, 8
    
    #six values stand for i2c uart1 uart2 etc.. Expand later?
    payload = [length, 0, msgClass, msgId, 0, 1, 0, 0, 0, 0]
    
    checksum = calc_checksum(ubx_class, ubx_id, payload, returnval=True)
    msg = struct.pack('>H14B', header, ubx_class, ubx_id, length, 0,  msgClass, msgId, 0, 1, 0, 0, 0, 0, checksum[0], checksum[1])
    dev.write(msg)
    
    
# Same UBX-CFG-MSG as enable_message() <- should refer to that but with all chanels at zero
def disable_message(dev, msgClass, msgId):
    header, ubx_class, ubx_id, length = 46434, 6, 1, 8
    payload = [length, 0, msgClass, msgId, 0, 0, 0, 0, 0, 0]
    checksum = calc_checksum(ubx_class, ubx_id, payload, returnval=True)
    msg = struct.pack('>H14B', header, ubx_class, ubx_id, length, 0,  msgClass, msgId, 0, 0, 0, 0, 0, 0, checksum[0], checksum[1])
    print(binascii.hexlify(msg))
    dev.write(msg)
    exit()

    

def list_enabled_messages():
    print("yo!")


def detect_ports():
    ports = list(serial.tools.list_ports.comports())
    for i in ports:
        print(i.device)

def configure_port(serial, baudrate, port=None):
    if(port==None):
         ports = list(serial.tools.list_ports.comports())
         port = ports[0].device

    try:
        serial.port = port
    except SerialException:
        print("woops")
    

# time_of_week in ms / longitude in deg / latitude in deg
# height ellipsoid in mm / height mean sea level mm
# horizontal accuracy in mm / vertical accuracy in mm
def ubx_NAV_POSLLH(dev):
    payload = dev.read(size=30)
    if calc_checksum(1, 2, payload, dev):
        try:
            payload = payload[2:]
            # Remove padding (=) introduced by struct for processor optimization
            iTOW, lon, lat, height, hMSL, hAcc, vAcc = struct.unpack('=LllllLL', payload)
            print("NAV_POSLLH - Time:{0} Longitude:{1} Lattitude:{2} HeightEllips:{3} Height_Sea:{4} Accuracy:{5} / {6}".format(
                iTOW, lon, lat, height, hMSL, hAcc, vAcc))
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    exit()
    return True


# time_of_week in ms / Dilution of Precision
# DOP is Dimensionless / scaled by factor 100
# Geometric / Position / Time / Vertical / Horizontal / Northing / Easting
def ubx_NAV_DOP(dev):
    payload = dev.read(size=20)
    if calc_checksum(1, 4, payload, dev):
        try:
            payload = payload[2:]
            iTOW, gDOP, pDOP, tDOP, vDOP, hDOP, nDOP, eDOP = struct.unpack('=L7H', payload)
            print("NAV_DOP - Time:{0} DOP Geometric:{1} Position:{2} Time:{3} Vert:{4} Hor:{5} North:{6} East:{7}".format(
                  iTOW, gDOP, pDOP, tDOP, vDOP, hDOP, nDOP, eDOP))
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    return True


# Time_of_week in ms / Fractional time_of_week ns / Week number
# GPS Fix (6 valid types depending on status) / Fix status flags (4 types)
# ECEF X cm / ECEF Y cm / ECEF Z cm / Position Accuracy cm
# ECEF-Velocity X cm/s / ECEF-Velocity Y cm/s / ECEF-Velocity Z cm/s
# Speed Accuracy cm/s / Position DOP (scale 0.01)
# reserved / number of SV's used / reserved
def ubx_NAV_SOL(dev):
    payload = dev.read(size=54)
    if calc_checksum(1, 6, payload, dev):
        try:
            payload = payload[2:]
            iTOW, fTOW, week, gpsFix, flags, ecefX, ecefY, ecefZ, pAcc, ecefVX, ecefVY, ecefVZ, sAcc, pDOP, reserved1, numSV, reserved21, reserved22, reserved23, reserved24 = struct.unpack('=LlhBx3lL3lLH6B', payload)
            print("NAV_SOL - iTOW:{0} fTOW:{1} week:{2} gpsFix:{3} flags:{4} ecefX:{5} ecefY:{6} ecefZ:{7} pAcc:{8} ecefVX:{9} ecefVY:{10} ecefVZ:{11} sAcc:{12} pDOP:{13} numSV:{14}".format(iTOW, fTOW, week, gpsFix, flags, ecefX, ecefY, ecefZ, pAcc, ecefVX, ecefVY, ecefVZ, sAcc, pDOP, numSV))
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    exit()
    return True



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
def ubx_NAV_PVT(dev):
    payload = dev.read(size=94)
    if calc_checksum(1, 7, payload, dev):
        try:
            payload = payload[2:]
            iTOW, year, month, day, hour, minute, second, valid, tAcc, nano, fixType, flags, flags2, numSV, lon, lat, height, hMSL, hAcc, vAcc, velN, velE, velD, gSpeed, headMot, sAcc, headAcc, pDOP, reserved11, reserved12, reserved13, reserved14, reserved15, reserved16,  headVeh, magDec, magAcc = struct.unpack('=LH5BBLlB2BB4l2L5lLLH6BlhH', payload)
            print("NAV_PVT - iTOW:{0} year:{1} month:{2} day:{3} hour:{4} min:{5} second:{6} valid:{7} tAcc:{8} nano:{9} fixType:{10} flags:{11} flags2:{12} numSV:{13} lon:{14} lat:{15} height:{16} hMSL:{17} hAcc:{18} vAcc:{19} velN:{20} velE:{21} velD:{22} gSpeed:{23} headMot:{24} sAcc:{25} headAcc:{26} pDOP:{27} reserved1:{28} headVeh:{29} magDec:{30} magAc:{31}".format(
                iTOW, year, month, day, hour, minute, second, valid, tAcc, nano, fixType, flags, flags2, numSV, lon, lat, height, hMSL, hAcc, vAcc, velN, velE, velD, gSpeed, headMot, sAcc, headAcc, pDOP, reserved11, headVeh, magDec, magAcc))
        except struct.error:
            print("{} {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    exit()


#def ubx_CFG_PRT():   <- set baudrate here for example



# Checksum is calculated over class/id/length/payload of packet
# using 8-bit Fletcher Algorithm (also used in TCP) RFC 1145
# bitmask 0xFF == modulus 256
# It might be that the modulo needs to be calculated after full operations
# This might become relavant when overflow occurs in check1 <- NMEA messages like CFG use class/id (xF1 x41)
def calc_checksum(ubx_class, ubx_id, payload, dev=None, returnval=False):

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


if __name__ == "__main__":
    main()
