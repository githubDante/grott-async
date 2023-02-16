"""
Grott proxy - async implementation
"""

import asyncio
import logging
import signal
import os
try:
    import orjson as json
except ImportError:
    import json
from time import perf_counter
from asyncio.streams import StreamReader, StreamWriter
from asyncio.base_events import Server
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from .utils.logger import GrottLogger
from .utils import (GrottProxyConfig, GrottDataExtractor, GrottPacketType, GrottRawPacket, RegType,
                    map_03_125, map_03_45, map_04_45, map_04_125)
from .extras.mqtt import send_to_mqtt

log = logging.getLogger('grott')


class AsyncProxyServer:

    def __init__(self, proxy_config: GrottProxyConfig):
        self.server: Server = None  # noqa
        self.config = proxy_config
        self.tasks = {}
        self.clients: Dict[tuple, ProxyClient] = {}
        self.host = self.config.listen_address
        self.port = self.config.listen_port

    async def proxy_factory(self, reader: StreamReader, writer: StreamWriter):
        """
        Create client instance and run it.

        This method is called by the server on each new connection
        """
        cl = ProxyClient(reader, writer, server=self)
        self.clients.update({cl.peername: cl})
        log.info(f'[GrottProxyServer] Accepted connection from {cl.peername}')
        loop = asyncio.get_running_loop()
        cl_task = loop.create_task(cl.run())
        self.tasks.update({cl.peername: cl_task})
        log.info(f'[GrottProxyServer] Current clients: {len(self.tasks)}')

    def proxy_info(self, *args, **kwargs):
        log.info('--- Current clients report ---')
        for peer_info, client in self.clients.items():
            log.info(f'''
    ---- Proxy client
    {peer_info}:
    {client}
    ----
    ''')

    def stop_server(self, *args):
        log.info('Stopping the proxy')
        self.server.close()

    def _server_exception(self, loop, context):
        log.exception('Someone raised an exception...')
        log.exception(context)

    async def main(self):

        self.server = await asyncio.start_server(
            self.proxy_factory, self.host, self.port
        )
        addr = self.server.sockets[0].getsockname()
        log.info(f'Grott async proxy - PID [{os.getpid()}] ')
        log.info(f'Grott async proxy - listening on {addr}')
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGUSR1, self.proxy_info)
        loop.add_signal_handler(signal.SIGINT, self.stop_server)
        loop.set_exception_handler(self._server_exception)
        async with self.server:
            try:
                await self.server.serve_forever()
            except asyncio.CancelledError:
                pass

    async def client_done_cb(self, sock_name):
        log.info(f'[GrottProxyServer] Clearing {sock_name}')
        self.tasks.pop(sock_name)
        self.clients.pop(sock_name)
        log.debug(f'[GrottProxyServer] Cleared {sock_name}')
        log.debug(f'[GrottProxyServer] Remaining clients: {len(self.tasks)}')


class ProxyClient:
    """
    Async client
    This is a 2 way communication channel between the
    datalogger and the Grott/Growatt server
    Packets are transmitted in both directions with an option
    to redirect copies to third-party services as well

    """
    __remote_host = '127.0.0.1'
    __remote_port = 12000
    __max_datalen = 2 ** 16
    """ 64K bytes of data. Should be enough """

    def __init__(self, cl_reader: StreamReader, cl_writer: StreamWriter, server: AsyncProxyServer = None):
        self.reader = cl_reader
        self.writer = cl_writer
        self.config: GrottProxyConfig = server.config
        self.server: AsyncProxyServer = server
        self.peername = self.writer.get_extra_info('peername')
        self.srv_peername = ('', 0)
        self.forwarder_w: StreamWriter = None  # noqa
        self.forwarder_r: StreamReader = None  # noqa
        self.cl_read_task: asyncio.Task = None  # noqa
        self.fw_read_task: asyncio.Task = None  # noqa
        self.msg_count = 0
        self.fwd_count = 0
        self.device_code = None
        self.logger_serial = ''
        self.inverter_serial = ''
        self.log = log

    def _exc_handler(self, loop, context):
        self.log.exception(f'Client error... {loop} -> {context}')

    async def run(self):
        """
        Start the proxy client reading / forwarding / data processing routines.

        :return:
        """

        loop = asyncio.get_running_loop()
        try:
            self.forwarder_r, self.forwarder_w = await asyncio.open_connection(self.config.growatt_srv,
                                                                               self.config.growatt_port)
        except ConnectionRefusedError:
            self.log.error(f'Cannot connect to {self.__remote_host}. Forwarding refused for {self.peername}')
            """ Do not schedule anything. Cleanup this client from the server """
            await self.server.client_done_cb(self.peername)
            return
        self.srv_peername = self.forwarder_w.get_extra_info('peername')

        self.cl_read_task = loop.create_task(self.client_read())
        self.fw_read_task = loop.create_task(self.server_read())

    async def client_read(self):
        while True:
            try:
                data = await self.reader.read(self.__max_datalen)
            except ConnectionResetError:
                self.log.error('[Client] connection reset...')
                await self.cleanup(client=True)
                return
            if data == b'':
                break
            try:
                await self.process_client_data(data)
            except Exception as e:
                self.log.exception(f'Client data error. Closing due to: {e} ')
                self.log.debug(f'Data causing the error: {data}')
                await self.cleanup(client=True)
                return
            self.msg_count += 1
            self.forwarder_w.write(data)
            await self.forwarder_w.drain()

        self.log.info('Connection closed by the client...')
        await self.cleanup(client=True)

    async def server_read(self):
        while True:
            try:
                data = await self.forwarder_r.read(self.__max_datalen)
            except ConnectionResetError:
                self.log.error('[Server] connection reset...')
                await self.cleanup(server=True)
                return
            self.log.debug(data)
            if data == b'':
                break
            try:
                await self.process_server_data(data)
            except Exception as e:
                self.log.exception(f'Server data error. Closing the connections due to: {e} ')
                self.log.debug(f'Data causing the error: {data}')
                await self.cleanup(server=True)
                return
            """ This probably the section below needs to be moved in process_server_data 
                if the inbound command must be blocked
            """
            self.fwd_count += 1
            self.writer.write(data)
            await self.writer.drain()
        self.log.info('Connection closed by the remote server....')
        await self.cleanup(server=True)

    async def cleanup(self, server=False, client=False) -> None:
        """
        ProxyClient cleanup.
        Cancel all tasks scheduled by 'self' and inform the server
        that this client has exited.

        Inform the opposite side for the closure by sending EOF

        :return:
        """
        self.log.info(f'Proxy client cleanup started [cl: {client}, srv: {server}]')
        if client:
            self.writer.close()
            self.forwarder_w.write_eof()
            self.forwarder_w.close()
        elif server:
            self.forwarder_w.close()
            self.writer.write_eof()
            self.writer.close()
        self.fw_read_task.cancel()
        self.cl_read_task.cancel()
        self.log.info(f'All sockets closed. Client stopped.')
        await self.server.client_done_cb(self.peername)

    async def process_server_data(self, data: bytes) -> None:
        """ To be implemented
            Async in case that the processing needs async code
        """
        _start_processing = perf_counter()
        packet = GrottRawPacket(data)
        self.log.debug(packet)
        self.log.debug(f'*** SRV PACKET PROCESSED [{round((perf_counter() - _start_processing) * 1000, 3)}ms]***')
        return

    async def process_client_data(self, data: bytes) -> None:
        """ To be implemented
            Async in case that the processing needs async code
        """
        _start_processing = perf_counter()
        packet = GrottRawPacket(data)
        self.log.debug(packet)
        if packet.valid_crc is False:
            self.log.error('CRC check failed. Packet not processed!!!')
            return
        if self.logger_serial == '':
            self.logger_serial = packet.datalogger_serial.decode()
            if self.logger_serial != '' and \
                    self.config.separate_logs is True and \
                    self.config.log_to == 'file':
                self._setup_own_logger()
        if self.inverter_serial == '':
            self.inverter_serial = packet.inverter_serial.decode()
        if packet.packet_type in [GrottPacketType.INVERTER_REPORT, GrottPacketType.LIVE_DATA,
                                  GrottPacketType.BUFFERED_DATA] \
                and packet.data_length > 100:
            parsed = GrottDataExtractor(packet.decrypted_packet().hex())
            self.log.debug(f'{parsed.inverter.name} <reg markers>: {parsed.regmaps}')
            self.log.debug(f'{parsed.inverter.name} <maps per section>: {parsed.registers_per_section}')
            self.log.debug(f'{parsed.inverter.name} <detected registers>: {parsed.registers}')

            if parsed.registers_per_section == 125:
                mapping = map_03_125 if packet.packet_type == GrottPacketType.INVERTER_REPORT else map_04_125
            else:
                mapping = map_03_45 if packet.packet_type == GrottPacketType.INVERTER_REPORT else map_04_45

            if packet.packet_type == GrottPacketType.INVERTER_REPORT:
                """ We need data from the report packet packets
                    in order to determine which registers must be extracted 
                """
                log.debug(f'{parsed.inverter}: {parsed.regmaps}')
                for k in mapping.values():
                    if k.id == 43:
                        """ DTC is at the same location for all inverters """
                        if self.device_code is None:
                            self.device_code = parsed.int_at(k.id)
                        self.log.debug(f'{k.description}: {parsed.int_at(k.id)}')
                    if k.id == 34 or k.id == 125 and parsed.registers_per_section == 125:
                        self.log.debug(f'{k.description}: {parsed.ascii_at(k.id, k.id + k.length)}')

            elif packet.packet_type == GrottPacketType.LIVE_DATA and packet.data_length > 100:
                reg_filter = self.config.dtc_mapping.get(self.device_code, mapping.keys())
                """ Use a filter and fallback to all registers 
                    in the complete map if this DTC is not specified in the config 
                """
                self.log.debug(f'Filter: {reg_filter}')
                extracted = {'device': self.inverter_serial, 'time': parsed.tstamp, 'buffered': parsed.buffered,
                             'values': {'logger_serial': self.logger_serial, 'pv_serial': self.inverter_serial}}
                for k in mapping.values():
                    if k.id not in reg_filter:
                        continue
                    if k.type == RegType.TEXT:
                        value = parsed.ascii_at(k.id, k.id + k.length)
                    elif k.length == 1:
                        value = k.format(parsed.int_at(k.id))
                    elif k.length == 2:
                        value = k.format(parsed.long_at(k.id))
                    extracted['values'].update({k.description: value})
                if json.__name__ == 'orjson':
                    self.log.debug(json.dumps(extracted, option=json.OPT_INDENT_2))
                else:
                    self.log.debug(json.dumps(extracted, indent=2))
                loop = asyncio.get_running_loop()

                if self.config.has_mqtt:
                    task = loop.create_task(send_to_mqtt(extracted, self.config, self.log))

                """ Distribute the data to all plugins """
                for plugin in self.config.plugins.sync_plugins.values():
                    loop.run_in_executor(None, plugin.data, packet.decrypted_packet(), extracted, self.log)
                for plugin in self.config.plugins.async_plugins.values():
                    loop.create_task(plugin.data(packet.decrypted_packet(), extracted, self.log))
        self.log.debug(f'*** PACKET PROCESSED [{round((perf_counter() - _start_processing) * 1000, 3)}ms]***')
        # TODO: distribute the data to other plugins specified in the config after this point
        return

    def _setup_own_logger(self):
        """ Logging to a separate file for every datalogger """
        setup_log = GrottLogger(self.config.log_to, fname=f'grott_cl_{self.logger_serial}.log',
                                logger_name=f'grott-{self.logger_serial}', level=self.config.log_level, keep=1)

        self.log = logging.getLogger(f'grott-{self.logger_serial}')

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.peername})> cl_msgs: {self.msg_count} | srv_msgs: {self.fwd_count}'

    def __str__(self):
        return f'''<{self.__class__.__name__}> 
        DTC: {self.device_code} | InvSerial: {self.inverter_serial} | Datalogger: {self.logger_serial}
        Stats -  Client msgs: {self.msg_count} | Server msgs: {self.fwd_count}
        '''

