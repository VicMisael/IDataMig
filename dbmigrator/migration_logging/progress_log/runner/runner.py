from dbmigrator.configuration_management.configuration import MigrationConfig
from dbmigrator.configuration_management.db_credentials import DBCredentials
from dbmigrator.configuration_management.utils import postgresql_GIST_indexes
from dbmigrator.data_migration.mysql_to_postgresql import MySQLToPostgreSQL
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.migration_logging.progress_log.progress_log import ProgressLog



def run(mysql_credentials: DBCredentials,
        postgres_credentials: DBCredentials,
        migration_configuration: MigrationConfig, migration_logger: MigrationLogger):
    try:
        progress_log = ProgressLog.load_from_file(migration_configuration.progress_json_name)
        migration_logger.log_info(f'resuming from file`{migration_configuration.progress_json_name}')
    except FileNotFoundError:
        migration_logger.log_info(f'file not found, creating new file`{migration_configuration.progress_json_name}')
        progress_log = ProgressLog(migration_configuration.progress_json_name)

    mysql_conn = MySQLConnection(mysql_credentials)
    mysql_conn.create()

    postgres_conn = PostgreSQLConnection(postgres_credentials)
    postgres_conn.create()

    migration = MySQLToPostgreSQL(mysql_conn, postgres_conn)
    migration.GIST_indexes = postgresql_GIST_indexes()
    migration.bulk_commit = migration_configuration.bulk_commit
    migration.postgresql_bulk_size = migration_configuration.postgres_bulk_size
    migration.mysql_batch_size = migration_configuration.mysql_batch_size
    migration.exclude_tables = migration_configuration.excluded_tables

    json_name = migration_configuration.json_name
    schema_name = migration_configuration.schema_name

    def read_metadata():
        # Step 1: Load the metadata from MySQL
        migration.load_mysql_metadata_json(json_name)
        # Step 2: Generate the DDLs
        migration.generate_DDLs(schema_name)

    def generate_ddl_enums():
        # Step 3: Execute the DDLs for the enums
        migration.execute_DDL_enums()

    def generate_ddl():
        # Step 4: Execute the DDLs for the tables
        migration.execute_DDL_tables()

    def generate_execute_data_migration():
        # Step 5: Execute the data migration
        # migration.execute_save_to_csv(schema_name)
        migration.execute_data_migration(schema_name, progress_log)

    def generate_primary_keys():
        # Step 6: Execute the DDLs for the primary keys
        migration.execute_DDL_primary_keys()

    def generate_constraints():
        # Step 7: Execute the DDLs for the constraints
        migration.execute_DDL_constraints()

    def generate_execute_ddl_indexes():
        # Step 8: Execute the DDLs for the indexes
        migration.execute_DDL_indexes()

    read_metadata()
    if not progress_log.enums_created:
        generate_ddl_enums()
        progress_log.set_enums_created()
    if not progress_log.are_tables_created:
        generate_ddl()
        progress_log.set_are_tables_created()
    if not progress_log.migrated_tables:
        generate_execute_data_migration()
        progress_log.set_executed_data_migration()
    if not progress_log.generated_primary_keys:
        generate_primary_keys()
        progress_log.set_generated_primary_keys()
    if not progress_log.generated_constraints:
        generate_constraints()
        progress_log.set_generated_constraints()
    if not progress_log.generated_indexes:
        generate_execute_ddl_indexes()
        progress_log.set_generated_indexes()

# load_progress()
# check progress, jump to step
# if progress is in data migration, check migrated tables(The tables should be fully migrated)
# check current_table, if is set, then the table is partially migrated, if None, a table was fully migrated(Use CSV
# for finer control over the migration)
#
