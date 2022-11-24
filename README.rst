Growatt/Grott proxy (async)
=================================

Build on top of asyncio.

* Features:

  - automatic inverter/data registers detection
  - DTC (device type code) filter (optional)
  - logging - log levels: debug, info, error etc.
  - logging options: stdout/file
  - separate log file per datalogger/inverter (when logging to file)
  - datalogger session
  - server stats (on signal.SIGUSR1/kill -10)
  - plugins: sync & async plugins
  - optional *orjson* support (will be used if available)

* Note that only a limited set of registers are supported at the moment. All definitions
  can be found in grott_async/utils/protocol.py

* Usage:

.. code-block:: console

    grott-proxy [-c <config.ini>] [-w <work_dir>]


* Plugins - async & sync. Each plugin must be an instance of **GrottProxyASyncPlugin** or **GrottProxySyncPlugin**. The plugin file must be placed in directory *plugins* relative to the working path (*-w* command switch or the directory from which *grott-proxy* is called). The variable in the file doesn't matter as long as it is unique for the respective plugin type. The data method of the class will be called with each data packet from every datalogger.

  - sync example:

    .. code-block:: python

        import logging
        from grott_async.extras.plugin import GrottProxySyncPlugin


        class MyPlugin(GrottProxySyncPlugin):

        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

        def show_data(self, data: dict):
            print(data)

        def data(self, packet: bytes, parsed_data: dict, log: logging.Logger):
            self.show_data(parsed_data)

        cool_plugin_name = MyPlugin(1, 2, 3)


