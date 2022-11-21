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
    - optional *orjson* support (will be used if available)

* Note that only a limited set of registers are supported at the moment. All definitions
  can be found in grott_async/utils/protocol.py

* Usage:

.. code-block:: console

    grot-proxy [-c <config.ini>] [-w <work_dir>]

