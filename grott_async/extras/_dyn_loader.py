import inspect
import os
from importlib import import_module
from logging import getLogger
from .plugin import GrottProxySyncPlugin, GrottProxyAsyncPlugin

log = getLogger('grott')


class GrottPluginLoader:
    """
    Dynamic loader for plugins

    """
    __plugin_dir__ = 'plugins'

    def __init__(self):
        self.plugins = {}
        self.async_plugins = {}
        self.load()

    def load(self):
        if os.path.exists(self.__plugin_dir__) is False:
            log.info('Plugins dir missing.')
            return
        for f in os.listdir(self.__plugin_dir__):
            if f.endswith('.py'):
                mod_name = f.split('.py')[0]
                try:
                    mod = import_module(f'{self.__plugin_dir__}.{mod_name}')
                except Exception:
                    log.error(f'Loading failed for {mod_name}')
                    continue
                log.info(f'Checking for plugins in {f.split(".py")}')
                sync_plugins = [(x, y) for x, y in inspect.getmembers(mod) if isinstance(y, GrottProxySyncPlugin)]
                async_plugins = [(x, y) for x, y in inspect.getmembers(mod) if isinstance(y, GrottProxyAsyncPlugin)]
                log.info(f'Found: {len(sync_plugins) + len(async_plugins)} in {mod_name}')
                for plugin in sync_plugins:
                    self.plugins.update({plugin[0]: plugin[1]})
                for plugin in async_plugins:
                    self.async_plugins.update({plugin[0]: plugin[1]})
        log.info(f'Loaded [{len(self.plugins) + len(self.async_plugins)}] plugins.')
