import unittest
from dbmigrator.configuration_management.db_credentials import mysql_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.data_access.mysql_data_access import MySQLTableIterator
from dbmigrator.data_access.mysql_metadata_reader import mysql_metadata_table


class TestMysqlIterator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mysql_conn = MySQLConnection(mysql_credentials())
        cls.mysql_conn.create()

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()
        
    def test_mysql_table_iterator(self):
        
        table = mysql_metadata_table(self.mysql_conn, 'areas')
        table_iterator = MySQLTableIterator(self.mysql_conn, table)
        
        for row in table_iterator:
            print(row)
        table_iterator.close()

if __name__ == "__main__":
    unittest.main()