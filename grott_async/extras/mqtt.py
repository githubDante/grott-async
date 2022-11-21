try:
    import orjson as json
except ImportError:
    import json
import asyncio_mqtt as aiomqtt
from logging import getLogger
from grott_async.utils import GrottProxyConfig

log = getLogger('grott-proxy')


async def _mqtt_with_auth(data: dict, conf: GrottProxyConfig):
    async with aiomqtt.Client(conf.mqtt_server, port=conf.mqtt_port,
                              username=conf.mqtt_user, password=conf.mqtt_pass) as client:
        await client.publish(conf.mqtt_topic, payload=json.dumps(data))


async def _mqtt_without_auth(data: dict, conf: GrottProxyConfig):
    async with aiomqtt.Client(conf.mqtt_server, port=conf.mqtt_port) as client:
        await client.publish(conf.mqtt_topic, payload=json.dumps(data))


async def send_to_mqtt(data: dict, conf: GrottProxyConfig):
    """
    Send extracted data to MQTT broker.
    :param data: Data extracted from LIVE_DATA packet
    :type data: dict
    :param conf: GrottProxy config
    :type conf:
    :return:
    :rtype:
    """
    try:
        if conf.mqtt_auth:
            await _mqtt_with_auth(data, conf)
        else:
            await _mqtt_without_auth(data, conf)
    except Exception as e:
        log.exception(f'[GrottProxy-MQTT sender] Error while sending to MQTT: {e}')



