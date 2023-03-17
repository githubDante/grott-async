import asyncio
from asyncio.base_events import Server
from typing import Optional
import uuid
from logging import getLogger
from grott_async.utils.packet_builder import ReadHoldingV5, ReadHoldingV6, SetHoldingV5, SetHoldingV6

log = getLogger('grott')


class GrottCMDSocket:

    def __init__(self, proxy):
        from grott_async.grottproxy_async import AsyncProxyServer
        proxy: AsyncProxyServer

        self.sock = 'grott_async.sock'
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
        cl = CMDSockClient(reader, writer, self)
        self.clients.update({cl.id: cl})
        log.debug(f'Client <{cl.id}> connected')
        loop = asyncio.get_running_loop()
        loop.create_task(cl.run())

    def remove_client(self, cl):
        cl: CMDSockClient
        self.clients.pop(cl.id)

    def list_proxy_clients(self):
        return self.proxy.list_clients()

    def get_client(self, logger_sn: str):
        return self.proxy.get_client(logger_sn)


class CMDSockClient:

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server: GrottCMDSocket):
        self.reader = reader
        self.writer = writer
        self.server = server
        self.id = str(uuid.uuid4())

    async def run(self):
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
            log.debug(self.server.clients)
            #return '\n'.join([x for x in self.server.clients.keys()]).encode() + bytes.fromhex('0a')
            clients = self.server.list_proxy_clients()
            for_socket = ''
            for cl in clients:
                for_socket += f'{cl[0]} | {cl[1]} | {cl[2]}\n'
            return for_socket.encode()

        if 'read' in body.lower():
            try:
                as_list = body.split(' ')
                logger = as_list[1]
                register = int(as_list[2])
                proxy_cl = self.server.get_client(logger)
                if not proxy_cl:
                    return
                cmd = None
                if proxy_cl.proto_version == 6:
                    cmd = ReadHoldingV6(proxy_cl.logger_serial.encode(), register, reg_len=1)
                elif proxy_cl.proto_version == 5:
                    cmd = ReadHoldingV5(proxy_cl.logger_serial.encode(), register, reg_len=1)
                if cmd:
                    await proxy_cl.send_local_command(cmd.struct())

            except Exception as e:
                log.exception(e)
                return b''
