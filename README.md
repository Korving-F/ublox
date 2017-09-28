# UBX Packet Parser

#### UBX - u-blox's binary protocol messages
---
## Overview
This library is able to configure some elementary properties of  ublox GPS modules that operate using the UBX binary protocol as well as read periodic messages coming from the device (and verify their integrity) when a serial connection has been instantiated. It was created because ...

A ublox 8 device was used to develop and test this library in combination with the documentation provided by ublox.<sup>[1](https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_%28UBX-13003221%29_Public.pdf)</sup> Many of these messages should also be compatible with earlier versions of the device (4/5/6/7) but others might not be backwards compatible due to being more recently added to the UBX-protocol.

## Dependencies

## Usage

## Supported Messages
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

## Future Improvements
