import asyncio
from asyncio.base_events import Server
from typing import Optional
import uuid
from logging import getLogger
import struct
from grott_async.utils.packet_builder import ReadHoldingV5, ReadHoldingV6, SetHoldingV5, SetHoldingV6
from grott_async.utils.packet import GrottRawPacket
from grott_async.grottproxy_async import ProxyClient

log = getLogger('grott')


class GrottCMDSocket:

    def __init__(self, proxy):
        from grott_async.grottproxy_async import AsyncProxyServer
        proxy: AsyncProxyServer
        self.server: Server = None  # noqa
        self.clients = {}
        self.proxy = proxy

    async def stop(self):
        await self.server.wait_closed()

    async def start(self):

        self.server = await asyncio.start_server(self._factory, host='127.0.0.1', port='15279')
        log.debug('Command endpoint listening on (127.0.0.1, 15279)')
        async with self.server:
            try:
                await self.server.serve_forever()
            except asyncio.CancelledError:
                pass

    async def _factory(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        CMD socket client connections factory

        :param reader: Will be provided by the server
        :param writer: Will be provided by the server
        :return:
        """
        cl = CMDSockClient(reader, writer, self)
        self.clients.update({cl.id: cl})
        log.debug(f'Client <{cl.id}> connected')
        loop = asyncio.get_running_loop()
        loop.create_task(cl.run())

    def remove_client(self, cl):
        cl: CMDSockClient
        self.clients.pop(cl.id)

    def list_proxy_clients(self):
        """
        Get a list with the clients/inverters currently connected to the proxy
        :return:
        """
        return self.proxy.list_clients()

    def get_client(self, logger_sn: str) -> ProxyClient:
        """
        Get a ProxyClient object from the server

        :param logger_sn: Serial number of the datalogger
        :return:
        """
        return self.proxy.get_client(logger_sn)


class CMDSockClient:

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server: GrottCMDSocket):
        self.reader = reader
        self.writer = writer
        self.server = server
        self.id = str(uuid.uuid4())

    async def run(self):
        """
        Start the CommandServer

        :return:
        """
        while True:
            try:
                data = await asyncio.wait_for(self.reader.read(1024), 30)
                command_res = await self._command_body(data)
                print(data)
                if command_res:
                    self.writer.write(command_res)
                    #self.writer.write(data)
                    await self.writer.drain()

                if data == b'':
                    break
            except asyncio.TimeoutError:
                self.writer.write(b'')
                await self.writer.drain()
                self.writer.close()
                self._deref()
                return
            except ConnectionResetError:
                self.writer.close()
                self._deref()
                return

        log.debug(f'Client <{self.id}> exiting')
        try:
            self.writer.write(b'')
            await self.writer.drain()
            self.writer.close()
        except Exception:
            pass
        finally:
            self._deref()

    def _deref(self):
        self.server.remove_client(self)

    async def _command_body(self, body: bytes) -> Optional[bytes]:
        body = body.decode().lstrip().rstrip()
        if body == 'list':
            """ List all clients currently connected """
            log.debug(self.server.clients)
            #return '\n'.join([x for x in self.server.clients.keys()]).encode() + bytes.fromhex('0a')
            clients = self.server.list_proxy_clients()
            for_socket = ''
            for cl in clients:
                for_socket += f'{cl[0]} | {cl[1]} | {cl[2]}\n'
            return for_socket.encode()

        elif 'read' in body.lower():
            """ Command for read a holding register from the inverter """
            try:
                as_list = body.split(' ')
                logger = as_list[1]
                register = int(as_list[2])
                proxy_cl = self.server.get_client(logger)
                if not proxy_cl:
                    return
                cmd = None
                if proxy_cl.proto_version == 6:
                    cmd = ReadHoldingV6(proxy_cl.logger_serial.encode(), register)
                elif proxy_cl.proto_version == 5:
                    cmd = ReadHoldingV5(proxy_cl.logger_serial.encode(), register)
                if cmd:
                    await proxy_cl.send_local_command(cmd.struct())
                    response = await proxy_cl.local_cmd_queue.get()
                    packet = GrottRawPacket(response)
                    reg = struct.unpack('>H', packet.decrypted_packet()[-6:-4])[0]
                    value = struct.unpack('>H', packet.decrypted_packet()[-4:-2])[0]
                    fmt = f'Reg: {reg} Value: {value}\n'
                    return fmt.encode()

            except Exception as e:
                log.exception(e)
                return b''

        elif 'set' in body.lower():
            """ Command for writing a value to a holding register of the inverter """
            try:
                as_list = body.split(' ')
                logger = as_list[1]
                address = int(as_list[2])
                value = int(as_list[3])
                proxy_client = self.server.get_client(logger)
                if not proxy_client:
                    return
                cmd = None
                if proxy_client.proto_version == 6:
                    cmd = SetHoldingV6(proxy_client.logger_serial, address, value)
                elif proxy_client.proto_version == 5:
                    cmd = SetHoldingV5(proxy_client.logger_serial, address, value)
                if cmd:
                    await proxy_client.send_local_command(cmd.struct())
                    response = await proxy_client.local_cmd_queue.get()
                    packet = GrottRawPacket(response)
                    reg = struct.unpack('>H', packet.decrypted_packet()[-6:-4])[0]
                    value = struct.unpack('>H', packet.decrypted_packet()[-4:-2])[0]
                    fmt = f'SET Reg: {reg} Value: {value}\n'
                    return fmt.encode()

            except Exception as e:
                return b''

