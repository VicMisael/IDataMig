import unittest

from dbmigrator.configuration_management.db_credentials import  mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection

class TestConnections(unittest.TestCase):

    def test_mysql_connection(self):
        mysql_conn = MySQLConnection(mysql_credentials())
        mysql_conn.create()
        self.assertIsNotNone(mysql_conn.connection, 'The MySQL connection is None.')
        mysql_conn.close()

    def test_postgresql_connection(self):
        postgres_conn = PostgreSQLConnection(postgres_credentials())
        postgres_conn.create()
        self.assertIsNotNone(postgres_conn.connection, 'The PostgreSQL connection is None.')
        postgres_conn.close()

if __name__ == '__main__':
    unittest.main()