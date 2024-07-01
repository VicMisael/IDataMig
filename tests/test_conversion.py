import unittest
from dbmigrator.configuration_management.db_credentials import mysql_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.data_access.mysql_metadata_reader import mysql_metadata_table
from dbmigrator.structure_conversion.table_to_json import table_to_json, dict_to_table
from dbmigrator.structure_conversion.table_to_sql import table_to_postgres_ddl


class TestConversion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mysql_conn = MySQLConnection(mysql_credentials())
        cls.mysql_conn.create()

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_table_to_json(self):
        table = mysql_metadata_table(self.mysql_conn, 'device_transfers')
        self.assertIsNotNone(table, 'The table is None.')
        json_str = table_to_json(table)
       # table2 = dict_to_table(json_str)
       # self.assertEqual(table.name, table2.name)
       # print(json_str)

    def test_table_to_postgres_ddl(self):
        table = mysql_metadata_table(self.mysql_conn, 'device_transfers')
        self.assertIsNotNone(table, 'The table is None.')
        ddl, _ = table_to_postgres_ddl(table,"teste")
        ddl2, _= table_to_postgres_ddl(table)

       # print(ddl)
       # print(ddl2)
       
if __name__ == '__main__':
    unittest.main()