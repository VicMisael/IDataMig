import psycopg2
import psycopg2.extras

from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.configuration_management.utils import format_reserved_word


def postgres_execute_DDL(postgresql_connection, sql):
    try:
        connection = postgresql_connection.connection
        cursor = connection.cursor()
        MigrationLogger().log_info(f"Query: {sql}")
        cursor.execute(sql)
    except Exception as e:
        MigrationLogger().log_error(f"Error executing PostgreSQL DDL query: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()


class PostgreSQLWriter:
    def __init__(self, postgresql, table, schema="", buffer_size=100, bulk_commit=True):
        self.bulk_commit = bulk_commit
        self.postgresql = postgresql
        self.table = table
        self.buffer_size = buffer_size
        self.buffer = []
        if schema != "":
            schema += "."
        self.schema = schema
        self.column_names = ', '.join([format_reserved_word(column.name) for column in self.table.columns])
        self.insert_sql = f"INSERT INTO {self.schema}{self.table.name} ({self.column_names}) VALUES %s"
        self.cursor = None
        parts = []
        for column in self.table.columns:
            if column.data_type.lower() in ['point', 'geometry']:
                parts.append("ST_GeomFromText(%s, 4326)")
            else:
                parts.append("%s")
        self.template = f"({', '.join(parts)})"

    def insert_data(self, data):
        self.buffer.append(data)
        if len(self.buffer) >= self.buffer_size:
            return self.flush_buffer()
        return False

    def flush_buffer(self):
        if not self.buffer or len(self.buffer) == 0:
            return False
        try:
            self.cursor = self.postgresql.connection.cursor()
            # MigrationLogger().log_info(f"Query: {self.insert_sql}")
            psycopg2.extras.execute_values(self.cursor, self.insert_sql, self.buffer, template=self.template)
            num_inserted_rows = len(self.buffer)
            MigrationLogger().log_info(f"Inserted {num_inserted_rows} rows into {self.schema}{self.table.name}.")
            self.buffer.clear()
        except Exception as e:
            MigrationLogger().log_error(f"Error inserting data into PostgreSQL: {e},{self.table.name}")
            raise e
        finally:
            self.close_cursor()
        if self.bulk_commit:
            self.commit()
            return True

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
