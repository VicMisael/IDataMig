import string
from abc import ABC, abstractmethod

from dbmigrator.migration_logging.observer.logging_level import LoggingLevel


class ILoggingObserver(ABC):

    def push(self, message: string, level: LoggingLevel):
        raise NotImplementedError
