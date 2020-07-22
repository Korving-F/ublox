## UBX Packet Parser

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub contributors](https://img.shields.io/github/contributors-anon/Korving-F/ublox)

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
    - CFG-RATE (0x06 0x08)
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

### Basic Usage
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

### Other Issues / Examples
* When using the default .read() method the internal message buffer gets cleared, taking in some fresh data first.
This seems to have the effect that certain messages are never read while they are activated.
One way around this is to read from a loop and check for the message you're interested in:

```python
        >>> while(True):
        ...     y = x.read()
        ...     if(y.ubx_id == '04'):
        ...         break
        ...
        Receiving
        01 02
        Receiving
        01 04
        >>> y
        <ubx.UbxMessage object at 0x7f7a9dcf7be0>
```

* Alternatively one can disable the flushed read as in the following example. NB! since you're reading from a stale buffer you're data will be old unless you read often and/or throw in an occasional flushed .read(). 

```python
        >>> x.read(reset=False)
        Receiving
        01 07
        <ubx.UbxMessage object at 0x7f7a9dc69438>
```

* For low power consumption use-cases one can increase the time between GNSS measurements. Value given is in milliseconds resulting in a calculated frequency. E.g. 1000ms == 1Hz (This is indicated by u-blox as a good default). Thanks @hankedan000 :) 

```python
        >>> x.cfg_rate(1000)
        Receiving
        05 01
        Acknowledged. CLS:0x6 ID:0x8
        <ubx.UbxMessage object at 0x7f8d895ea518
```

### Future Improvements
At the moment only activated messages can be read and there is no support yet
for polling specific messages. If any desired messages are not included please
create an issue.
