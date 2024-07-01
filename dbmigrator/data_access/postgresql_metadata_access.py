import psycopg2
from dbmigrator.migration_logging.log import MigrationLogger

class PostgreSQLTableManager:
    def __init__(self, postgresql, table_name, schema=""):
        self.postgresql = postgresql
        self.table_name = table_name
        if schema != "":
            schema += "."
        self.schema = schema
        self.cursor = None

    def get_table_row_count(self):
        try:
            self.cursor = self.postgresql.connection.cursor()
            sql = f"SELECT COUNT(*) FROM {self.schema}{self.table_name}"
            self.cursor.execute(sql)
            row_count = self.cursor.fetchone()[0]
            return row_count if row_count is not None else 0
        except Exception as e:
            MigrationLogger().log_error(f"Error getting row count from PostgreSQL table: {e}")
            raise e
        finally:
            self.close_cursor()
            
    def get_max_id(self, id_column):
        try:
            self.cursor = self.postgresql.connection.cursor()
            sql = f"SELECT MAX({id_column}) FROM {self.schema}{self.table_name}"
            MigrationLogger().log_info(f"Query: {sql}")
            self.cursor.execute(sql)
            max_id = self.cursor.fetchone()[0]
            return max_id
        except Exception as e:
            MigrationLogger().log_error(f"Error getting maximum value of ID column from PostgreSQL table: {e}")
            raise e
        finally:
            self.close_cursor()

    def truncate_table(self):
        try:
            self.cursor = self.postgresql.connection.cursor()
            sql = f"TRUNCATE TABLE {self.schema}{self.table_name} CASCADE"
            MigrationLogger().log_info(f"Query: {sql}")
            self.cursor.execute(sql)
            self.postgresql.connection.commit()
            MigrationLogger().log_info(f"Table {self.schema}{self.table_name} truncated.")
        except Exception as e:
            MigrationLogger().log_error(f"Error truncating PostgreSQL table: {e}")
            raise e
        finally:
            self.close_cursor()

    def reset_sequence(self):
        try:
            self.cursor = self.postgresql.connection.cursor()
            sql = f"ALTER SEQUENCE {self.schema}{self.table_name}_id_seq RESTART WITH 1"
            MigrationLogger().log_info(f"Query: {sql}")
            self.cursor.execute(sql)
            self.postgresql.connection.commit()
            MigrationLogger().log_info(f"Sequence for table {self.schema}{self.table_name} reset.")
        except Exception as e:
            MigrationLogger().log_error(f"Error resetting sequence for PostgreSQL table: {e}")
            raise e
        finally:
            self.close_cursor()

    def get_sequence_current_value(self):
        try:
            self.cursor = self.postgresql.connection.cursor()
            sql = f"SELECT last_value FROM {self.schema}{self.table_name}_id_seq"
            MigrationLogger().log_info(f"Query: {sql}")
            self.cursor.execute(sql)
            current_value = self.cursor.fetchone()[0]
            return current_value
        except Exception as e:
            MigrationLogger().log_error(f"Error getting current value from PostgreSQL sequence: {e}")
            raise e
        finally:
            self.close_cursor()
    
    def set_sequence_value(self, value):
        try:
            self.cursor = self.postgresql.connection.cursor()
            sql = f"SELECT setval('{self.schema}{self.table_name}_id_seq', %s, false)"
            MigrationLogger().log_info(f"Query: {sql}")
            self.cursor.execute(sql, (value,))
            self.postgresql.connection.commit()
            MigrationLogger().log_info(f"Sequence value for table {self.schema}{self.table_name} set to {value}.")
        except Exception as e:
            MigrationLogger().log_error(f"Error setting sequence value for PostgreSQL table: {e}")
            raise e
        finally:
            self.close_cursor()

    def close_cursor(self):
        if self.cursor and not self.cursor.closed:
            self.cursor.close()
            self.cursor = None
            
    def commit(self):
        try:
            self.postgresql.connection.commit()
        except Exception as e:
            MigrationLogger().log_error(f"Error committing data to PostgreSQL: {e}")
            raise e   
        self.close_cursor()

    def rollback(self):
        try:
            self.postgresql.connection.rollback()
        except Exception as e:
            MigrationLogger().log_error(f"Error committing data to PostgreSQL: {e}")
            raise e  
        self.close_cursor()