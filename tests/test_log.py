import string
import unittest

from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.migration_logging.observer.i_observer import ILoggingObserver
from dbmigrator.migration_logging.observer.logging_level import LoggingLevel


class TestLog(unittest.TestCase):

    def test_log_msgs(self):
        MigrationLogger().log_critical("TESTE")
        MigrationLogger().log_info("TESTE INFO")
        MigrationLogger().log_debug("TESTE DEBUG")
        MigrationLogger().log_error("TESTE ERROR")
        MigrationLogger().log_warning("TESTE WARNING")
        MigrationLogger().log_notset("TESTE NOTSET")

    def test_log_new_observer(self):
        class NewObserver(ILoggingObserver):
            def __init__(self):
                self.messages = []

            def push(self, message: string, level: LoggingLevel):
                self.messages.append(str(level) + message)

        newObserver = NewObserver()
        MigrationLogger().register_observer(newObserver)

        MigrationLogger().log_info("TESTE")
        MigrationLogger().log_critical("TESTE CRITICAL")

        print(newObserver.messages)
        self.assertEqual(len(newObserver.messages), 2)


if __name__ == '__main__':
    unittest.main()
