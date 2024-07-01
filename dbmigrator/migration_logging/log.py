from dbmigrator.migration_logging.observer.logging_level import LoggingLevel
from dbmigrator.migration_logging.observer.python_logger_observable import PythonConsoleLoggerObservable

class MigrationLogger:
    _self = None
    _observers = []

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
            cls._self.register_observer(PythonConsoleLoggerObservable("DBMigrator"))
        return cls._self
    
    def register_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def __notify__(self, message, level):
        for observer in self._observers:
            observer.push(message,level)

    def log_notset(self, message):
        self.__notify__(message, LoggingLevel.NOTSET)

    def log_info(self, message):
        self.__notify__(message, LoggingLevel.INFO)

    def log_debug(self, message):
        self.__notify__(message, LoggingLevel.DEBUG)

    def log_error(self, message):
        self.__notify__(message, LoggingLevel.ERROR)

    def log_critical(self, message):
        self.__notify__(message, LoggingLevel.CRITICAL)

    def log_warning(self, message):
        self.__notify__(message, LoggingLevel.WARNING)
