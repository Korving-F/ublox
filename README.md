## UBX Packet Parser

### Introduction
This module is able to read from and configure ublox GPS modules
through their UBX binary protocol over a serial connection. It can be considered
a wrapper around the [pyserial](https://github.com/pyserial/pyserial) module.

A ublox 8 device was used to develop and test this library in combination with
the documentation provided by
[ublox](https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_%28UBX-13003221%29_Public.pdf).
Many of the messages specified in this document should also be compatible with
earlier versions of the device (4/5/6/7) but others might not be backwards
compatible.

### Test
Move to main directory and issue:
 ``` bash
$ python2 -m pytest
$ python3 -m pytest
 ```

### Supported Messages
*  #### Configuration
    - CFG-MSG  (0x06 0x01)
    - CFG-CFG  (0x06 0x09)
    - CFG-NAV5 (0x06 0x24)
    - ...

* #### GPS-Data
    - NAV-POSLLH  (0x01 0x02)
    - NAV-DOP     (0x01 0x04)
    - NAV-SOL     (0x01 0x06)
    - NAV-PVT     (0x01 0x07)
    - ...

* #### Other
    - ACK-NAK (0x05 0x00)
    - ACK-ACK (0x05 0x01)
    - ...

### Usage
One would usually create a serial connection to the GPS module and proceed to
create an instance of UbxStream through which one reads data and sends
configuration messages.
The UbxStream class comes with functions to save, load and reset configurations
as well as an automated way to disable all enabled-by-default NMEA messages.
Of course one can enable/disable specific messages by passing in the documented
message class and id.
One can auto detect serial ports and set the baudrate for the connection.
<br>
<img src="https://raw.githubusercontent.com/Korving-F/ublox/master/docs/usage.png" alt="UBX Parser at work" height="50%" width="50%">


### Future Improvements
At the moment only activated messages can be read and there is no support yet
for polling specific messages. If any desired messages are not included please
create an issue.
