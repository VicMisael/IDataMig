from dbmigrator.configuration_management.configuration import MigrationConfig
from dbmigrator.configuration_management.db_credentials import postgres_credentials, mysql_credentials
from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.migration_logging.progress_log.runner.runner import run


def main():
    run(mysql_credentials(), postgres_credentials(), MigrationConfig.default_config(), MigrationLogger())


if __name__ == '__main__':
    main()
