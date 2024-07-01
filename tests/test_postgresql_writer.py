import unittest

from dbmigrator.configuration_management.db_credentials import mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.mysql_data_access import MySQLTableIterator
from dbmigrator.data_access.mysql_metadata_reader import mysql_metadata_table
from dbmigrator.data_access.postgresql_data_access import PostgreSQLWriter


class TestPostgreSQLWriter(unittest.TestCase):

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
        
        
    def test_postgresql_writer(self):
        table_name = 'areas'
        schema_name = 'test'
        table = mysql_metadata_table(self.mysql_conn, table_name)
        table_iterator = MySQLTableIterator(self.mysql_conn, table)
        postgres_writer = PostgreSQLWriter(self.postgres_conn, table, schema=schema_name, buffer_size=1, bulk_commit=False)
          
        for row in table_iterator:
            #print(row)
            postgres_writer.insert_data(row)
        
        
        table_iterator.close()
        
        postgres_writer.flush_buffer() # flush is mandatory to insert the last rows
        #postgres_writer.rollback()
        postgres_writer.commit()
        
        
if __name__ == "__main__":
    unittest.main()