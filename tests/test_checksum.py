import sys, os
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__) + '/../'))
from ublox import ubx
import struct
import binascii

# Setting up a mock serial device needed for checksum function
class dummySerial(object):
    def __init__(self, msg_cls=None, msg_id=None, confirm=True):
        assert not msg_cls == None, "Message class needs to be defined"
        assert not msg_id == None, "Message id needs to be defined"
        self.msg_cls = msg_cls
        self.confirm = confirm
        self.msg_id = msg_id
        self.counter = 0
        if sys.version_info[0] < 3:
            self._version = 2
        else:
            self._version = 3

    # two hard-coded NAV-POSLLH messages pulled from u-center +
    # same messages 1bit mangled to test negative
    def read(self, size=None):
        if size == None:
            if self.msg_cls == 1 and self.msg_id == 2:
                if self.counter == 0:
                    v2 = '\x86'
                    v3 = bytes([223])
                    self.counter += 1
                else:
                    v2 = '\x9c'
                    v3 = bytes([204])
                    self.counter = 0

        else:
            if self.msg_cls == 1 and self.msg_id == 2:
                if self.confirm:
                    v2 = '\x1c\x00\xd8\x99\x13\x02\xec\xd6\\\xe6\xa4\xb3\x97\x15xWq\x00\xdd\x17q\x00\xff\xff\xff\xff\x00\xd4\x86\xdf'
                    v3 = b"\x1c\x00\xe0>\x1b\x0276\xb4\x0ep\xc2g#\x9b5\x02\x00\x08\xed\x01\x008\x1c\x01\x00U'\x01\x00"
                else:
                    v2 = '\x1c\x00\xd8\x99\x13\x01\xec\xd6\\\xe6\xa4\xb3\x97\x15xWq\x00\xdd\x17q\x00\xff\xff\xff\xff\x00\xd4\x86\xdf'
                    v3 = b"\x1c\x00\xe0>\x1b\x0276\xb3\x0ep\xc2g#\x9b5\x02\x00\x08\xed\x01\x008\x1c\x01\x00U'\x01\x00"


        if self._version == 2:
            return v2
        else:
            return v3



# UbxMessage with invalid checksum doesnt contain anything
def test_validate_checksum():
    x = dummySerial(msg_cls=1,msg_id=2)
    y = ubx.UbxMessage('01','02',version=sys.version_info[0],dev=x)
    assert hasattr(y, 'lat')
    assert hasattr(y, 'lon')

    z = dummySerial(msg_cls=1,msg_id=2, confirm=False)
    q = ubx.UbxMessage('01','02',version=sys.version_info[0],dev=z)
    assert not hasattr(q, 'lat')
    assert not hasattr(q, 'lon')


def test_calculate_checksum():
    v2 = '\x1c\x00\xd8\x99\x13\x02\xec\xd6\\\xe6\xa4\xb3\x97\x15xWq\x00\xdd\x17q\x00\xff\xff\xff\xff\x00\xd4\x86\xdf'
    v3 = b"\x1c\x00\xe0>\x1b\x0276\xb4\x0ep\xc2g#\x9b5\x02\x00\x08\xed\x01\x008\x1c\x01\x00U'\x01\x00"

    # Create UbxMessage object to gain access to calculate_checksum function
    x = dummySerial(msg_cls=1,msg_id=2)
    y = ubx.UbxMessage('01','02',version=sys.version_info[0],dev=x)

    if sys.version_info[0] < 3:
        result = y._UbxMessage__calc_checksum(1,2,list(map(lambda i: ord(i), list(v2))))
        assert result == [134, 156]
    else:
        result = y._UbxMessage__calc_checksum(1,2,list(v3))
        assert result == [223,204]


if __name__ == "__main__":
    test_validate_checksum()
    test_calculate_checksum()
