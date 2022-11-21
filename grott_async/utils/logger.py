import sys
import logging
from logging.handlers import RotatingFileHandler


class GrottLogger:

    def __init__(self, output: str = 'stdout', fname: str = 'grott_proxy_async.log', level: str='critical',
                 logger_name=None, f_size: int=20, keep: int=4):
        """
        Logger with options to send everything to stdout or to file.
        If file is selected then a Rotating file handler will be used
        for all messages

        :param log_name: The name which the logger should use
        :type log_name:  str
        :param fname: File to which the log messages will be written
        :type fname: str
        :param level: Filtering level (default: critical)
        :type level: str (optional)
        :param logger_name: Different logger name (used for client separation)
        :type logger_name: str (optional)
        :param f_size: Size of the file before rotation in MBs (default: 20MB)
        :type f_size: int (optional)
        :param keep: How many files should be kept (default: 5)
        :type keep: int (optional)

        """
        self._f_size = f_size
        self._keep = keep
        self._log_file = fname
        self.level = getattr(logging, level.upper(), 20)
        if logger_name:
            self.log = logging.getLogger(logger_name)
        else:
            self.log = logging.getLogger('grott')
        self.ouput = output
        self.__setup()

    def __setup(self):
        if self.level < 20:
            """ DEBUG """
            fmt = '%(asctime)s - [%(levelname)s] - %(module)s->%(funcName)s:%(lineno)d-> %(message)s'
        else:
            fmt =  '%(asctime)s - [%(levelname)s]: %(message)s'
        formatter = logging.Formatter(fmt)

        self.log.setLevel(self.level)
        if self.ouput == 'file':
            handler = RotatingFileHandler(self._log_file, maxBytes=self._f_size * 1024 ** 2, backupCount=self._keep)
        else:
            handler = logging.StreamHandler(sys.stdout)

        handler.setFormatter(formatter)
        self.log.addHandler(handler)
