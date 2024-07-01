import unittest

from dbmigrator.configuration_management.db_credentials import mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.postgresql_metadata_access import PostgreSQLTableManager


class TestPostgreSQLManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.postgres_conn = PostgreSQLConnection(postgres_credentials())
        cls.postgres_conn.create()

    
    @classmethod
    def tearDownClass(cls):
        cls.postgres_conn.close()
        
        
    def test_postgresql_manager(self):
        
        table_name = 'states'
        schema_name = 'test'

        pg_manager = PostgreSQLTableManager(self.postgres_conn, table_name, schema=schema_name)
        
        print("Max id: ", pg_manager.get_max_id('id'))
        print("Row count: ", pg_manager.get_table_row_count())
        sequence_current_value = pg_manager.get_sequence_current_value()
        print("Sequence current value: ", sequence_current_value)
        pg_manager.set_sequence_value(sequence_current_value + 1)
        sequence_current_value = pg_manager.get_sequence_current_value()
        print("Sequence current value: ", sequence_current_value)
        print("Resetting sequence...")
        pg_manager.reset_sequence()
        sequence_current_value = pg_manager.get_sequence_current_value()
        print("Sequence current value: ", sequence_current_value)
        print("Truncating table...")
        pg_manager.truncate_table()
        print("Row count: ", pg_manager.get_table_row_count())
        
        pg_manager.commit()
        
        
if __name__ == "__main__":
    unittest.main()