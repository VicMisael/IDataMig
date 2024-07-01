import psycopg2
from dbmigrator.migration_logging.log import MigrationLogger

class PostgreSQLConnection:
    def __init__(self, db_credentials):
        self.db_credentials = db_credentials
        self.connection = None
        self.database = db_credentials.database
        
    def create(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.db_credentials.database,
                user=self.db_credentials.user,
                password=self.db_credentials.password,
                host=self.db_credentials.host,
                port=self.db_credentials.port
            )
            MigrationLogger().log_info("PostgreSQL connection created successfully.")
        except Exception as e:
            MigrationLogger().log_error(f"Error creating PostgreSQL connection: {e}")
            raise e

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                MigrationLogger().log_info("PostgreSQL connection closed.")
                self.connection = None
            except Exception as e:
                MigrationLogger().log_error(f"Error closing PostgreSQL connection: {e}")
                raise e
