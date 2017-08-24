import binascii
import serial
from serial.tools import list_ports
import struct
import sys

# UBox proprietary software -> wine ~/.wine/DriveC/ProgramFiles/x86/ucenter v8.16/ucenter.exe or smt..
# Create symbolic link between serial device and .wine/dosdevices/com[number]

# class connection? x = ubox.connection() -> x.configure(protocol/baudrate) -> x.last_message
# x.configure(messages=reset/mask/inverted_mask)

#print(u'\xb5b')
#Checkout multi-threading
#autodetecting of device file here
#print(y.decode("iso8859"))

#Suitable for HAB Usage Max Altitude 50,000 meters / 164041 feet  in Flight Mode.
# How to configure for flight mode? / Hab usage?

def main():
    dev = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    ubox_synch = '\xb5b'
    counter = 0
    enable_message(dev, 1, 2)
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
                ubx_class = dev.read()
                ubx_id = dev.read()
                print(int(binascii.hexlify(ubx_class),16))
                print(int(binascii.hexlify(ubx_id),16))
                print(ubx_id) #identify test strings for dictionary and replace keys
                
                try:
                    # package = ubxMessage(ubx_class, ubx_id)
                    # package.formattedContent
                    # 
                    result = {'02': lambda x: ubx_NAV_POSLLH(),
                              '04': lambda x: ubx_NAV_DOP(),
                              '06': lambda x: ubx_NAV_SOL()
                    }
                    result[ubx_id]()
                except KeyError:
                    print("Invalid packet id")
                    return True
                counter = 0


def enable_message(serial,  msgClass, msgId):
    # b562 aka message header integer <- can thus be casted as one into binary
    serial.baudrate = 9600
    header = 46434
    ubx_class = 6
    ubx_id = 1
    length = 8
    payload = [length, 0, msgClass, msgId,0, 1, 0, 0, 0, 0]
    checksum = calc_checksum(ubx_class, ubx_id, payload, returnval=True)
    msg = struct.pack('>HBBBBBBBBBBBBBB', header, ubx_class, ubx_id, length, 0,  msgClass, msgId, 0, 1, 0, 0, 0, 0, checksum[0], checksum[1])
    print(binascii.hexlify(msg))
    serial.write(msg)
    exit()
    
    
def disable_message(serial, msgClass, msgId, protocol="UBX"):
    print("Disable: {0} {1} {2}".format(protocol, msgClass, msgId))

def alter_message_rate():
    print("Hi!")

def list_enabled_messages():
    print("yo!")


def detect_ports():
    ports = list(serial.tools.list_ports.comports())
    for i in ports:
        print(i.device)

def configure_port(serial, port=None):
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
def ubx_NAV_POSLLH():
    payload = dev.read(size=30)
    if calc_checksum(1, 2, payload):
        try:
            payload = payload[2:]
            time_of_week, lon, lat, h_ellips, h_sea, hor, vert = struct.unpack('LllllLL', payload)
            print("NAV_POSLLH - Time:{0} Longitude:{1} Lattitude:{2} HeightEllips:{3} Height_Sea:{4} Accuracy:{5} / {6}".format(
                  time_of_week, lon, lat, h_ellips, h_sea, hor, vert))
        except Error:
            print(sys.exc_info()[0])
        
    return True


# time_of_week in ms / Dilution of Precision
# DOP is Dimensionless / scaled by factor 100
# Geometric / Position / Time / Vertical / Horizontal / Northing / Easting
def ubx_NAV_DOP():
    payload = dev.read(size=20)
    if calc_checksum(1, 4, payload):
        try:
            payload = payload[2:]
            time_of_week, geo, pos, time, vert, hor, north, east = struct.unpack('LHHHHHHH', payload)
            print("NAV_DOP - Time:{0} DOP Geometric:{1} Position:{2} Time:{3} Vert:{4} Hor:{5} North:{6} East:{7}".format(
                  time_of_week, geo, pos, time, vert, hor, north, east))
        except Error:
            print(sys.exc_info()[0])
    
    return True


# time_of_week in ms / fractional time_of_week ns / week number
# GPS Fix (6 valid types depending on status) / Fix status flags (4 types)
# ECEF X cm / ECEF Y cm / ECEF Z cm / Position Accuracy cm
# ECEF-Velocity X cm/s / ECEF-Velocity Y cm/s / ECEF-Velocity Z cm/s
# Speed Accuracy cm/s / Position DOP (scale 0.01)
# reserved / number of SV's used / reserved
def ubx_NAV_SOL():
    payload = dev.read(size=54)
    if calc_checksum(1, 4, payload):
        try:
            payload = payload[2:]
            iTOW, fTOW, week, gpsFix, flags, ecefX, ecefY, ecefZ, pAcc, ecefVX, ecefVY, ecefVZ, sAcc, pDOP, reserved1, numSV, reserved2 = struct.unpack('LlhBxlllLlllLHBBBBBB', payload)
            print("NAV_SOL - iTOW:{0} fTOW:{1} week:{2} gpsFix:{3} flags:{4} ecefX:{5} ecefY:{6} ecefZ:{7} pAcc:{8} ecefVX:{9} ecefVY:{10} ecefVZ:{11} sAcc:{12} pDOP:{13} numSV:{14}".format(iTOW, fTOW, week, gpsFix, flags, ecefX, ecefY, ecefZ, pAcc, ecefVX, ecefVY, ecefVZ, sAcc, pDOP, numSV))
        except Error:
            print(sys.exc_info()[0])
    

    return True


#def ubx_NAV_PVT():

#def ubx_CFG_PRT():   <- set baudrate here for example



# Checksum is calculated over class/id/length/payload of packet
# using 8-bit Fletcher Algorithm (also used in TCP) RFC 1145
# bitmask 0xFF == modulus 256
def calc_checksum(ubx_class, ubx_id, payload, returnval=False):

    check1 = ubx_class + ubx_id
    check2 = (2*ubx_class) + ubx_id
    
    if(returnval==False):
        chk1 = int(dev.read().encode('hex'), 16)
        chk2 = int(dev.read().encode('hex'), 16)
        
        for i in range(0, len(payload)):
            check1 = (check1 + int(payload[i].encode('hex'), 16)) % 256
            check2 = (check1 + check2) % 256
            
            if chk1==check1 and chk2==check2:
                return True
            else:
                print("something went wrong")
                return False
    else:
        for i in range(0, len(payload)):
            check1 = (check1 + payload[i]) % 256
            check2 = (check1 + check2) % 256

        result = [check1, check2]
        return result


if __name__ == "__main__":
    main()
