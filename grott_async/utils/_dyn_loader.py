import inspect
import os
import sys
from importlib import import_module
from logging import getLogger
from typing import Dict
from grott_async.extras.plugin import GrottProxySyncPlugin, GrottProxyAsyncPlugin

log = getLogger('grott')


class GrottPluginLoader:
    """
    Dynamic loader for plugins

    """
    __plugin_dir__ = 'plugins'

    def __init__(self):
        self.sync_plugins: Dict[str, GrottProxySyncPlugin] = {}
        self.async_plugins: Dict[str, GrottProxyAsyncPlugin] = {}
        self.load()

    def load(self):
        if os.path.exists(self.__plugin_dir__) is False:
            log.info('Plugins dir missing.')
            return
        work_path = os.path.abspath(os.curdir)
        if work_path not in sys.path:
            sys.path.insert(1, work_path)
        for f in os.listdir(self.__plugin_dir__):
            if f.endswith('.py'):
                mod_name = f.split('.py')[0]
                try:
                    mod = import_module(f'{self.__plugin_dir__}.{mod_name}')
                except Exception as e:
                    log.error(f'Loading failed for {mod_name} : {e}')
                    continue
                log.info(f'Checking for plugins in {mod_name}')
                sync_plugins = [(x, y) for x, y in inspect.getmembers(mod) if isinstance(y, GrottProxySyncPlugin)]
                async_plugins = [(x, y) for x, y in inspect.getmembers(mod) if isinstance(y, GrottProxyAsyncPlugin)]
                log.info(f'Found: {len(sync_plugins) + len(async_plugins)} plugin in {mod_name}')
                for plugin in sync_plugins:
                    self.sync_plugins.update({plugin[0]: plugin[1]})
                for plugin in async_plugins:
                    self.async_plugins.update({plugin[0]: plugin[1]})
        log.info(f'Loaded [{len(self.sync_plugins) + len(self.async_plugins)}] plugins total.')
