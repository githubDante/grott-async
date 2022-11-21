from configparser import ConfigParser
from typing import Dict, List


class _Sections:
    GROTT = 'Grott'
    GROWATT = 'Growatt'
    MQTT = 'MQTT'
    DTC = 'DTCMapping'


class _OptionNames:
    SERVER = 'address'
    PORT = 'port'
    USER = 'username'
    PASS = 'password'
    AUTH = 'use_auth'
    """ Enable authentication """
    TOPIC = 'topic'
    """ Topic for MQTT """
    BUFFERED = 'buffered'
    """ Send buffered data """
    LOG_TO = 'log'
    LOG_LEVEL = 'log_level'
    LOG_FILE = 'log_filename'
    DATALOG_SEP = 'separate_logs'


class GrottProxyConfig:

    def __init__(self, ini_file: str = 'grott_async.ini'):
        self._file = ini_file
        self.parser = ConfigParser(allow_no_value=False)
        self.dtc_mapping: Dict[int, List[int]] = {}
        self.listen_address = '0.0.0.0'
        self.listen_port = 5279
        self.log_level = 'debug'
        self.log_to = 'stdout'
        self.log_file = 'grott_proxy.log'
        self.separate_logs = False
        self.growatt_srv: str = 'server.growatt.com'
        self.growatt_port: int = 5279
        self.mqtt_server: str = '127.0.0.1'
        self.mqtt_port: int = 1883
        self.mqtt_auth: bool = False
        self.mqtt_user: str = ''
        self.mqtt_pass: str = ''
        self.mqtt_buffered: bool = False
        self.mqtt_topic: str = 'grott/energy'

        self._has_mqtt = False
        self._has_dtc = False
        self.__parse()

    def __parse(self):
        self.parser.read(self._file)
        has_growatt = self.parser.has_section(_Sections.GROWATT)
        has_grott = self.parser.has_section(_Sections.GROTT)
        self.has_dtc = self.parser.has_section(_Sections.DTC)
        self.has_mqtt = self.parser.has_section(_Sections.MQTT)

        """ Proxy settings """
        if has_grott:
            self.listen_address = self._get_val(_Sections.GROTT, _OptionNames.SERVER, self.listen_address)
            self.listen_port = self._get_val(_Sections.GROTT, _OptionNames.PORT, self.listen_port)
            self.log_to = self._get_val(_Sections.GROTT, _OptionNames.LOG_TO, self.log_to)
            self.log_level = self._get_val(_Sections.GROTT, _OptionNames.LOG_LEVEL, self.log_level)
            self.log_file = self._get_val(_Sections.GROTT, _OptionNames.LOG_FILE, self.log_file)
            self.separate_logs = self._get_val(_Sections.GROTT, _OptionNames.DATALOG_SEP, self.separate_logs, bool_=True)

        """ Proxy forward settings """
        if has_growatt:
            self.growatt_srv = self._get_val(_Sections.GROWATT, _OptionNames.SERVER, self.growatt_srv)
            self.growatt_port = self._get_val(_Sections.GROWATT, _OptionNames.PORT, self.growatt_port)

        """ MQTT Options """
        if self.has_mqtt:
            self.mqtt_server = self._get_val(_Sections.MQTT, _OptionNames.SERVER, self.mqtt_server)
            self.mqtt_port = self._get_val(_Sections.MQTT, _OptionNames.PORT, self.mqtt_port, int_=True)
            self.mqtt_auth = self._get_val(_Sections.MQTT, _OptionNames.AUTH, self.mqtt_auth, bool_=True)
            self.mqtt_user = self._get_val(_Sections.MQTT, _OptionNames.USER, self.mqtt_user)
            self.mqtt_pass = self._get_val(_Sections.MQTT, _OptionNames.PASS, self.mqtt_pass)
            self.mqtt_topic = self._get_val(_Sections.MQTT, _OptionNames.TOPIC, self.mqtt_topic)

        """ DTC Maps """
        if self.has_dtc:
            """ Get registers which the user want to be included in the JSON from this section """
            for dtc in self.parser.options(_Sections.DTC):
                try:
                    dtc_map = self.parser.get(_Sections.DTC, dtc)
                    dtc = int(dtc)
                    dtc_map = [int(x) for x in dtc_map.split(',')]
                    self.dtc_mapping.update({dtc: dtc_map})
                except ValueError:
                    continue

        """ Other Options / Plugins etc """

    def _get_val(self, section, option, default, int_=False, float_=False, bool_=False):
        """

        :param section:
        :type section:
        :param option:
        :type option:
        :param default:
        :type default:
        :param int_:
        :type int_:
        :param float_:
        :type float_:
        :param bool_:
        :type bool_:
        :return:
        :rtype:
        """
        if self.parser.has_option(section, option):
            if int_:
                return self.parser.getint(section, option)
            if float_:
                return self.parser.getfloat(section, option)
            if bool_:
                return self.parser.getboolean(section, option)
            return self.parser.get(section, option)
        return default

    def __str__(self):
        base = f'''
    *** {self.__class__.__name__} ***
        Listen address: {self.listen_address}
        Listen port:    {self.listen_port}
        Forward to:     {self.growatt_srv}
        Forward port:   {self.growatt_port}
        Log to:         {self.log_to}
        Log level:      {self.log_level}
        Separate logs:  {self.separate_logs}
    '''
        if self.has_mqtt:
            base += f'''
        MQTT server:    {self.mqtt_server}
        MQTT port:      {self.mqtt_port}
        MQTT auth:      {self.mqtt_auth}
        MQTT user:      {self.mqtt_user}
        MQTT pass:      {self.mqtt_pass}
        MQTT buffered:  {self.mqtt_buffered}
        MQTT topic:     {self.mqtt_topic}
        '''
        if self.has_dtc:
            for dtc, map_ in self.dtc_mapping.items():
                base += f'''
        DTC code [{dtc}]: {map_}'''

        base += f'''
        
    {40 * '*'}
        '''
        return base
