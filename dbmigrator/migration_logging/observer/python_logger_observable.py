import logging
import string

from dbmigrator.migration_logging.observer.i_observer import ILoggingObserver
from dbmigrator.migration_logging.observer.logging_level import LoggingLevel


class PythonConsoleLoggerObservable(ILoggingObserver):
    def __init__(self, name):
        super().__init__()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        # Create a console handler to output logs to the console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # Create a formatter and set the handler formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def push(self, message: string, level: LoggingLevel):
        if level == LoggingLevel.DEBUG:
            self.logger.debug(message)
        elif level == LoggingLevel.WARNING:
            self.logger.warning(message)
        elif level == LoggingLevel.ERROR:
            self.logger.error(message)
        elif level == LoggingLevel.CRITICAL:
            self.logger.critical(message)
        else:
            self.logger.info(message)


class PythonFileLogger(ILoggingObserver):
    def __init__(self, name):
        super().__init__()
        self.logger = logging.getLogger(name)
        logging.basicConfig()

        # Create a console handler to output logs to the console
        ch = logging.FileHandler(filename='logfile.log')
        ch.setLevel(logging.DEBUG)
        # Create a formatter and set the handler formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def push(self, message: string, level: LoggingLevel):
        if level == LoggingLevel.DEBUG:
            self.logger.debug(message)
        elif level == LoggingLevel.WARNING:
            self.logger.warning(message)
        elif level == LoggingLevel.ERROR:
            self.logger.error(message)
        elif level == LoggingLevel.CRITICAL:
            self.logger.critical(message)
        else:
            self.logger.info(message)
