import logging
import abc


class GrottProxyAsyncPlugin(abc.ABC):

    @abc.abstractmethod
    async def data(self, packet: bytes, parsed_data: dict, log: logging.Logger):
        """
        Async plugin entrypoint

        :param packet: Raw decoded packet as received by the proxy
        :type packet: bytes
        :param parsed_data: Parsed data from a packet
        :type parsed_data: dict
        :param log: Logger
        """
        raise NotImplementedError


class GrottProxySyncPlugin(abc.ABC):

    @abc.abstractmethod
    def data(self, packet: bytes, parsed_data: dict, log: logging.Logger):
        """
        Sync plugin entrypoint

        :param packet: Raw decoded packet as received by the proxy
        :type packet: bytes
        :param parsed_data: Parsed data from a packet
        :type parsed_data: dict
        :param log: Logger
        """
        raise NotImplementedError
