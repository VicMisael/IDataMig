import json
import unittest
from dbmigrator.configuration_management.db_credentials import mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.mysql_metadata_reader import mysql_fetch_tables
from dbmigrator.structure_conversion.table_to_json import load_json_file, save_json_file
from dbmigrator.structure_conversion.table_to_sql import table_to_postgres_ddl, constraints_to_sql, indexes_to_sql
from dbmigrator.configuration_management.utils import postgresql_GIST_indexes

class TestMetadataMigration(unittest.TestCase):

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

    def test_do_migration(self):

        tables = load_json_file('test.json')
        self.assertIsNotNone(json)
        self.assertTrue(json, "JSON file 'test.json' is empty or does not exist.")
        if tables is None:
            tables = mysql_fetch_tables(self.mysql_conn)
            self.assertIsNotNone(tables)
            save_json_file(tables, 'test.json')
        
        buffer = ""
        buffer_enum = ""
        buffer_constraints = ""
        buffer_primary_keys = ""
        buffer_indexes = ""
        
       
        
        schema = "test"
        for t in tables: 
            if t.name != 'migrations' and t.name != 'migrations_lock': #t.name == 'entry_status':
                sql, enum_sql = table_to_postgres_ddl(t, schema=schema)
                constraints, primary_keys = constraints_to_sql(t.constraints, table=t.name, schema=schema)
                indexes = indexes_to_sql(t.indexes, table=t.name, schema=schema, GIST_indexes=postgresql_GIST_indexes())
                for enum in enum_sql:
                    buffer_enum += enum + '\n'
                    #print(enum)
                #=print(sql)
                #print()
                #print(constraints)
                #print(indexes)
                buffer += sql + '\n\n'
                buffer_constraints += constraints
                buffer_primary_keys += primary_keys
                buffer_indexes += indexes
                
        with open('create_tables.sql', 'w') as f:
            
            f.write(buffer_enum)
            f.write("\n")
            f.write(buffer) 
            f.write("\n\n")
            f.write(buffer_primary_keys)
            f.write("\n\n\n")
            f.write(buffer_constraints)
            f.write("\n\n\n")
        
            f.write(buffer_indexes)
    
if __name__ == '__main__':
    unittest.main()



