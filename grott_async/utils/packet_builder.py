import random
import struct
from .packet import GrottConstants, GrottPacketType
from libscrc import modbus
from itertools import cycle
from typing import Union


def encrypt(packet: bytes) -> bytes:
    """
    Encrypt/Mask the provided bytes needed for protocol versions 5 & 6

    :param packet:
    :return: Encrypted bytes
    """

    packet = bytearray(packet)
    mask = cycle(GrottConstants.MASK)

    encrypted = bytearray([x ^ next(mask) for x in packet])
    pack = bytes(encrypted)
    return pack


class RegisterReq:
    """
    Base
    """
    def __init__(self, logger_sn: Union[str, bytes], address: int, data: int = None):
        #self.seq_no = random.randint(1, 255)  #
        self.seq_no = 1  # Always one seems OK
        self.datalen = 0  # Calculated on call to struct
        self.proto_ver = 0  # Override this in a subclass
        self.packet_type: GrottPacketType = GrottPacketType.UNKNOWN  # Override in subclass
        self.logger_sn = logger_sn
        self.address = address
        self.reg_data = data  # When generating REGISTER_SET request
        self.data_sep = 1

    def struct(self) -> bytes:
        """
        Prepare the packet for sending over the socket
        """
        seq_no = struct.pack('>H', self.seq_no)
        proto = struct.pack('>H', self.proto_ver)
        packet_t = self.packet_type
        serial = self.logger_sn if isinstance(self.logger_sn, bytes) else self.logger_sn.encode()
        datasep = struct.pack(f'>{self.data_sep*"B"}', *[0 for x in range(0, self.data_sep)])
        address = struct.pack('>H', self.address)
        #registers_requested = struct.pack('>H', self.reg_len)
        data = struct.pack('>H', self.reg_data) if self.reg_data else None
        """ The format of requests generated through server.growatt.com is starting address:end address """
        if data:
            packet_len = len(serial) + len(datasep) + len(address) + len(data) + 2
        else:
            packet_len = len(serial) + len(datasep) + len(address) * 2 + 2
        packet_len = struct.pack('>H', packet_len)

        if self.proto_ver in [5, 6]:
            """ Protocol versions 5 & 6 needs to be encrypted / masked """
            if data:
                packet = seq_no + proto + packet_len + packet_t + encrypt(serial + datasep + address + data)
            else:
                packet = seq_no + proto + packet_len + packet_t + encrypt(serial + datasep + address + address)
        else:
            if data:
                packet = seq_no + proto + packet_len + packet_t + serial + datasep + address + data
            else:
                packet = seq_no + proto + packet_len + packet_t + serial + datasep + address + address

        crc = struct.pack('>H', modbus(packet))
        return packet + crc


class SetHoldingV5(RegisterReq):
    """ Set a value to a _single_ holding register protocol version 5 """

    def __init__(self, logger_sn, address, value):
        super(SetHoldingV5, self).__init__(logger_sn, address, data=value)
        self.proto_ver = 5
        self.packet_type = GrottPacketType.REGISTER_SET
        self.data_sep = 0  # No idea why, but there is no offset in V5 when setting a register


class ReadHoldingV5(RegisterReq):

    def __init__(self, logger_sn, address):
        super(ReadHoldingV5, self).__init__(logger_sn, address, data=None)
        self.proto_ver = 5
        self.packet_type = GrottPacketType.REGISTER_READ
        self.data_sep = 1


class SetHoldingV6(RegisterReq):
    """ Set a value to a _single_ holding register """
    def __init__(self, logger_sn, address, value):
        super(SetHoldingV6, self).__init__(logger_sn, address, data=value)
        self.proto_ver = 6
        self.packet_type = GrottPacketType.REGISTER_SET
        self.data_sep = 20


class ReadHoldingV6(RegisterReq):
    def __init__(self, logger_sn, address):
        super(ReadHoldingV6, self).__init__(logger_sn, address, data=None)
        self.proto_ver = 6
        self.packet_type = GrottPacketType.REGISTER_READ
        self.data_sep = 20



