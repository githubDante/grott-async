import asyncio
import logging
import os
from argparse import ArgumentParser
from .utils import GrottProxyConfig, GrottLogger
from .grottproxy_async import AsyncProxyServer


def async_proxy():
    parser = ArgumentParser('grott-proxy', description='Growatt proxy server (async)')
    parser.add_argument('-c', '--config', required=False, default='grott_async.ini',
                        help='Config path (relative to work-dir if used)')
    parser.add_argument('-w', '--work-dir', required=False)
    options = parser.parse_args()
    if options.work_dir:
        dir = options.work_dir
        if not os.path.exists(dir):
            print(f'The directory {dir} does not exist. Please create it first.')
            exit(3)
        print(f'Switching to dir: {options.work_dir}')
        os.chdir(dir)

    """ Parse the INI file, load all dynamic plugins and start the main loop """
    config = GrottProxyConfig(options.config)
    logger = GrottLogger(output=config.log_to, level=config.log_level, fname=config.log_file)
    config.load_plugins()
    log = logging.getLogger('grott')
    log.debug(config)
    proxy = AsyncProxyServer(config)
    asyncio.run(proxy.main())
