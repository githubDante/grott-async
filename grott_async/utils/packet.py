"""
Grott - packet utilities
"""

from itertools import cycle
from libscrc import modbus
import struct
from typing import List, Union
import enum
from .protocol_enums import Fault1, Fault8, Warn8


__DEBUG__ = True


class GrottConstants:

    MASK = b'Growatt'
    """ Encryption mask """
    HEADER_PLAIN = 8
    """ Unencrypted part of the packet """
    HEADER_MAX_LEN = 158
    """ Length for packet in HEX format """
    PACKET_CRC = -2  # Last 2 bytes


class RegType:

    TEXT = 'text'
    FLOAT = 'float'
    INT = 'num'
    BIT = 'bit'
    FAULT_1 = 'fault_code'  # Inverter fault code Bit (&*1)  Page 58/65
    """ Fault codes as described in &*1 """
    FAULT_8 = 'fault_bitcode'  # Inverter fault code and warning code (&*8) Page 60/65
    """ Fault codes as described in &*8 """
    WARN_8 = 'warn_bitcode'
    """ Warn codes as described in &*8 """


class GrottRegister:
    """
    Class for register entries. Each register is with length of 2 bytes.
    Several registers can be combined for values > 65535 or ASCII strings

    """
    def __init__(self, reg_id: int, type_: str, descr: str, length=1, divide=10):
        """

        :param reg_id: Index of the register
        :type reg_id:
        :param type_: Field [num, float, text]
        :type type_: str
        :param length: Positions occupied by this register (default: 1, will expand )
        :param descr: Field description
        :type descr: str
        :type length:
        :param divide: Divisor for the value
        :type divide:
        """

        self.id = reg_id
        self.length = length
        self.type = type_
        self.divide = divide
        self.description = descr

    def extract(self, val):
        if self.type == RegType.INT:
            return int(val, 16)
        elif self.type == RegType.FLOAT:
            return int(val, 16) / self.divide

    def format(self, val: Union[int, str]):
        if self.type == RegType.FLOAT:
            return round(val / self.divide, 3)
        if self.type == RegType.INT or self.type == RegType.TEXT:
            return val
        if self.type == RegType.FAULT_1:
            return Fault1(val).name
        if self.type == RegType.FAULT_8:
            return Fault8(val).name
        if self.type == RegType.WARN_8:
            return Warn8(val).name
        if self.type == RegType.BIT:
            return '{:016b}'.format(val) if isinstance(val, int) else '{:016b}'.format(0xdead)


def grott_crc_ok(packet: bytes) -> bool:
    """
    CRC verification of a Grott packet

    :param packet: Decrypted Grott packet
    :type packet: bytes
    :return:
    :rtype:
    """
    crc = modbus(packet[:-2])
    return int(packet[-2:].hex(), 16) == crc


def decrypt(packet: bytes) -> bytes:
    """

    :param packet:
    :type packet:
    :return: Decrypted packet
    :rtype: bytes
    """

    packet = bytearray(packet)
    unmask = cycle(GrottConstants.MASK)

    decrypted = bytearray([x ^ next(unmask) for x in packet[GrottConstants.HEADER_PLAIN:GrottConstants.PACKET_CRC]])
    dec_pack = packet[:GrottConstants.HEADER_PLAIN] + \
        decrypted + \
        packet[GrottConstants.PACKET_CRC:]

    dec_pack = bytes(dec_pack)
    return dec_pack


class GrottPacketType(bytes, enum.Enum):

    """ Bytes [6:8] in the packet header """

    INVERTER_REPORT = struct.pack('>h', 259)  # HEX: 0103
    LIVE_DATA = struct.pack('>h', 260)  # HEX: 0104
    REGISTER_READ = struct.pack('>h', 261)  # HEX: 0105
    REGISTER_SET = struct.pack('>h', 262)  # HEX: 0106

    SET_TIME = struct.pack('>h', 272)  # HEX: 0110
    KEEP_ALIVE = struct.pack('>h', 278)  # HEX: 0116
    DATALOGGER_CONFIG = struct.pack('>h', 280)  # HEX: 0118
    DATALOGGER_REPORT = struct.pack('>h', 281)  # HEX: 0119
    BUFFERED_DATA = struct.pack('>h', 336)  # HEX: 0150

    UNKNOWN = struct.pack('>h', 0)

    @classmethod
    def _missing_(cls, value: object):
        return GrottPacketType.UNKNOWN

    def __format__(self, format_spec):
        return 'GrottPacket.' + self.name

    def __str__(self):
        return 'GrottPacket.' + self.name


class GrottRawPacket:

    def __init__(self, packet: bytes):
        """
        :param packet: Raw packet as received on the socket
        :type packet: bytes
        """
        self.packet = packet
        self.seq_no = int(self.packet[:2].hex(), 16)
        self.data_length = int(self.packet[4:6].hex(), 16)
        self.protocol_version = int(self.packet[2:4].hex(), 16)
        self.packet_crc = int(self.packet[-2:].hex(), 16)
        self.packet_type_num = int(self.packet[6:8].hex(), 16)  # Packet type as integer
        self.packet_type = GrottPacketType(self.packet[6:8])
        self._decrypted = None

    @property
    def valid_crc(self) -> bool:
        """ Packet CRC """
        return grott_crc_ok(self.packet)

    @property
    def valid_length(self) -> bool:
        """ Length validation """
        return len(self.packet[6:-2]) == self.data_length

    @property
    def needs_decryption(self) -> bool:
        return self.protocol_version in [5, 6]

    @property
    def datalogger_serial(self) -> bytes:
        """ Datalogger serial from the header
        """
        if len(self.packet) < 18:
            return b''
        return self.decrypted_packet()[8:18]

    @property
    def inverter_serial(self) -> bytes:
        """ Inverter serial from the header
        """
        if len(self.packet) < 28:
            return b''
        if self.packet_type in [GrottPacketType.INVERTER_REPORT,
                                GrottPacketType.BUFFERED_DATA,
                                GrottPacketType.LIVE_DATA
                                ]:

            if self.protocol_version == 5:
                return self.decrypted_packet()[18:28]
            elif self.protocol_version == 6:
                return self.decrypted_packet()[38:48]

        return b''

    def decrypted_packet(self) -> bytes:
        """
        Get a decrypted version of the packet

        :return:
        :rtype:
        """
        if self.needs_decryption:
            if self._decrypted:
                return self._decrypted
            else:
                self._decrypted = decrypt(self.packet)
                return self._decrypted
        else:
            return self.packet

    def __str__(self):
        return f'''
        *** {self.__class__.__name__} ***
        Sequence No:    {self.seq_no}
        Protocol ver:   {self.protocol_version}
        Encrypted:      {self.needs_decryption}
        CRC:            {self.packet_crc}
        CRC Valid:      {self.valid_crc}
        Packet Type#:   {self.packet_type_num}
        Packet Type:    {self.packet_type}
        Data length:    {self.data_length}
        Packet length:  {len(self.packet)}
        Datalogger:     {self.datalogger_serial}
        Inverter:       {self.inverter_serial}
        ----------------------------------------
        {self.packet}
        
        ----
        
        '''

