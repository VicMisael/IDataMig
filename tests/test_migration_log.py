import unittest

from dbmigrator.configuration_management.db_credentials import mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.postgresql_data_access import postgres_execute_DDL
from dbmigrator.data_migration.mysql_to_postgresql import MySQLToPostgreSQL
from dbmigrator.configuration_management.utils import postgresql_GIST_indexes


class TestMigrationLog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mysql_conn = MySQLConnection(mysql_credentials())
        cls.mysql_conn.create()

        cls.postgres_conn = PostgreSQLConnection(postgres_credentials())
        cls.postgres_conn.create()

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()
        cls.postgres_conn.close()

    def test_migration(self):
        schema_name = 'test'
        json_name = "metadata.json"

        migration = MySQLToPostgreSQL(self.mysql_conn, self.postgres_conn)
        migration.GIST_indexes = postgresql_GIST_indexes()
        migration.bulk_commit = False
        migration.postgresql_bulk_size = 10000
        migration.mysql_batch_size = 10000
        migration.only_tables = ['logs']

        migration.load_mysql_metadata_json(json_name)
        migration.generate_DDLs(schema_name)

        migration.execute_DDL_tables()

        migration.execute_data_migration(schema_name)

        migration.execute_DDL_primary_keys()
        migration.execute_DDL_constraints()
        migration.execute_DDL_indexes()

        self.postgres_conn.connection.commit()

    def test_migration_csv(self):
        schema_name = 'test'
        json_name = "metadata.json"

        migration = MySQLToPostgreSQL(self.mysql_conn, self.postgres_conn)
        migration.GIST_indexes = postgresql_GIST_indexes()
        migration.bulk_commit = False
        migration.postgresql_bulk_size = 10000
        migration.mysql_batch_size = 10000
        # migration.exclude_tables = ['logs']
        migration.only_tables = ['occurrence_comments']
        migration.load_mysql_metadata_json(json_name)
        #
        migration.generate_DDLs(schema_name)
        # migration.execute_DDL_enums()
        #
        # migration.execute_DDL_tables()

        migration.execute_save_to_csv()
        migration.execute_csv_to_postgres(schema_name)
        # migration.execute_data_migration(schema_name)

        # migration.execute_DDL_primary_keys()
        # migration.execute_DDL_constraints()
        # migration.execute_DDL_indexes()

        self.postgres_conn.connection.commit()


if __name__ == "__main__":
    unittest.main()
