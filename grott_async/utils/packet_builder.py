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
    def __init__(self, logger_sn: Union[str, bytes], address: int, reg_length: int = 1):
        self.seq_no = random.randint(1, 255)  #
        self.datalen = 0  # Calculated on call to struct
        self.proto_ver = 0  # Override this in a subclass
        self.packet_type: GrottPacketType = GrottPacketType.UNKNOWN  # Override in subclass
        self.logger_sn = logger_sn
        self.address = address
        self.reg_len = reg_length
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
        registers_requested = struct.pack('>H', self.reg_len)
        packet_len = len(serial) + len(datasep) + len(address) + len(registers_requested) + 2
        packet_len = struct.pack('>H', packet_len)

        if self.proto_ver in [5, 6]:
            """ Protocol versions 5 & 6 needs to be encrypted / masked """
            packet = seq_no + proto + packet_len + packet_t + encrypt(serial + datasep + address + registers_requested)
        else:
            packet = seq_no + proto + packet_len + packet_t + serial + datasep + address + registers_requested

        crc = struct.pack('>H', modbus(packet))
        return packet + crc


class SetHoldingV5(RegisterReq):
    """ Set a value to a _single_ holding register protocol version 5 """

    def __init__(self, logger_sn, address, value):
        super(SetHoldingV5, self).__init__(logger_sn, address, reg_length=value)
        self.proto_ver = 5
        self.packet_type = GrottPacketType.REGISTER_SET
        self.data_sep = 1


class ReadHoldingV5(RegisterReq):

    def __init__(self, logger_sn, address, reg_len):
        super(ReadHoldingV5, self).__init__(logger_sn, address, reg_length=reg_len)
        self.proto_ver = 5
        self.packet_type = GrottPacketType.REGISTER_READ
        self.data_sep = 1


class SetHoldingV6(RegisterReq):
    """ Set a value to a _single_ holding register """
    def __init__(self, logger_sn, address, value):
        super(SetHoldingV6, self).__init__(logger_sn, address, reg_length=value)
        self.proto_ver = 6
        self.packet_type = GrottPacketType.REGISTER_SET
        self.data_sep = 20


class ReadHoldingV6(RegisterReq):
    def __init__(self, logger_sn, address, reg_len):
        super(ReadHoldingV6, self).__init__(logger_sn, address, reg_length=reg_len)
        self.proto_ver = 6
        self.packet_type = GrottPacketType.REGISTER_READ
        self.data_sep = 20



