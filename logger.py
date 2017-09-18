import logging
from logging.handlers import RotatingFileHandler
import sys
import os


class Logger:
    # log files location
    __DEBUG_LOG_FILENAME = 'log/xmltvparser_debug.log'
    __WARNING_LOG_FILENAME = 'log/xmltvparser.log'

    # log formatter
    __formatter = logging.Formatter('#%(levelname)-8s [%(asctime)s] (%(process)d) %(module)s: %(message)s')

    def __init__(self):
        # create log dir if not exists
        if not os.path.exists('log'):
            os.makedirs('log')

        # log debug info to console
        self.__sh = logging.StreamHandler(sys.stdout)
        self.__sh.setLevel(logging.DEBUG)
        self.__sh.setFormatter(self.__formatter)

        # log debug info to debug log file
        self.__fh = RotatingFileHandler(self.__DEBUG_LOG_FILENAME, maxBytes=1048576,
                                        backupCount=5)
        self.__fh.setLevel(logging.DEBUG)
        self.__fh.setFormatter(self.__formatter)

        # log warnings to warning log file
        self.__fh2 = RotatingFileHandler(self.__WARNING_LOG_FILENAME, maxBytes=1048576,
                                         backupCount=5)
        self.__fh2.setLevel(logging.WARN)
        self.__fh2.setFormatter(self.__formatter)

        # setting up logger with handlers
        self.mylogger = logging.getLogger('XmlTvParserLogger')
        self.mylogger.setLevel(logging.DEBUG)
        self.mylogger.addHandler(self.__sh)
        self.mylogger.addHandler(self.__fh)
        self.mylogger.addHandler(self.__fh2)


# logger object and logging functions shortcut
logger = Logger()
debug = logger.mylogger.debug
info = logger.mylogger.info
warning = logger.mylogger.warning
error = logger.mylogger.error
critical = logger.mylogger.critical
