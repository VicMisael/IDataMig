import unittest

from dbmigrator.configuration_management.db_credentials import postgres_credentials
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.postgresql_data_access import postgres_execute_DDL

class TestPostgreSQLDDL(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.postgres_conn = PostgreSQLConnection(postgres_credentials())
        cls.postgres_conn.create()

    @classmethod
    def tearDownClass(cls):
        cls.postgres_conn.close()

    def test_postgresql_DDL(self):
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INTEGER,
            point geometry(point)
        );
        """
        
        postgres_execute_DDL(self.postgres_conn, create_table_sql)
        
        drop_table_sql = "DROP TABLE IF EXISTS test_table;"
        
        postgres_execute_DDL(self.postgres_conn, drop_table_sql)
    
        self.postgres_conn.connection.commit()

if __name__ == "__main__":
    unittest.main()
