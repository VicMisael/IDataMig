import unittest

from dbmigrator.configuration_management.db_credentials import mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.postgresql_data_access import postgres_execute_DDL
from dbmigrator.data_migration.mysql_to_postgresql import MySQLToPostgreSQL
from dbmigrator.configuration_management.utils import postgresql_GIST_indexes


class TestMigration(unittest.TestCase):

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

    def test_migration_user_id_constraint(self):
        with  self.mysql_conn.connection.cursor(buffered=True) as cursor:
            cursor.execute("""select  v.TABLE_NAME,kc.COLUMN_NAME from information_schema.KEY_COLUMN_USAGE as kc inner join  (select * from (select * 
                            from information_schema.referential_constraints 
                            where referenced_table_name = 'users') as d where d.CONSTRAINT_NAME like '%user_id%') as v on v.CONSTRAINT_NAME=kc.CONSTRAINT_NAME;
                            """)
            data = [table for table in cursor.fetchall()]
            tables_with_bad_reference = []
            for tuple in data:
                column_name = tuple[1]
                table_name = tuple[0]
                query = f"""
                    SELECT COUNT(*) FROM {table_name} where {column_name} = 1"""
                print(query)
                cursor.execute(query)
                result = cursor.fetchone()[0]
                if (result > 0):
                    tables_with_bad_reference.append(table_name)
            print(tables_with_bad_reference)

    def test_migration(self):
        schema_name = 'test'
        json_name = "metadata2.json"

        migration = MySQLToPostgreSQL(self.mysql_conn, self.postgres_conn)
        migration.GIST_indexes = postgresql_GIST_indexes()
        migration.bulk_commit = False
        migration.postgresql_bulk_size = 10000
        migration.mysql_batch_size = 10000
        migration.exclude_tables = ['logs', 'migrations', 'migrations_lock']

        # Step 1: Load the metadata from MySQL
        migration.load_mysql_metadata_json(json_name)
        # # Step 2: Generate the DDLs
        # migration.generate_DDLs(schema_name)
        # # Step 3: Execute the DDLs for the enums
        # migration.execute_DDL_enums()
        # # Step 4: Execute the DDLs for the tables
        # migration.execute_DDL_tables()
        # # Step 5: Execute the data migration
        # migration.execute_data_migration(schema_name)

        # self.postgres_conn.connection.commit()

        # sql = f"""
        #     INSERT INTO {schema_name}.users
        #     (id, login, "name", email, cpf, registration, birth_date, phone, blood_type, emergency_contact_name, emergency_contact_phone, agency_id, active, is_connected, need_to_change_password, created_at, updated_at, deleted_at, rank_id, nickname, representation_name)
        #     VALUES(1, 'admin2', 'ADMINISTRADOR2', 'admin2@admin.com', '2', '2', '1990-01-01', '(85) 99999-9999', 'O+'::{schema_name}."enum_blood_type", NULL, '2222222222', 1, 1, 1, 1, '2022-07-05 02:59:30.000', '2024-01-25 18:00:18.000', NULL, NULL, NULL, 'ADMINISTRADOR');
        # """
        # postgres_execute_DDL(self.postgres_conn, sql)

        # Step 6: Execute the DDLs for the primary keys
        # migration.execute_DDL_primary_keys()
        # Step 7: Execute the DDLs for the constraints
        # migration.execute_DDL_constraints()
        # Step 8: Execute the DDLs for the indexes
        # migration.execute_DDL_indexes()


if __name__ == "__main__":
    unittest.main()
