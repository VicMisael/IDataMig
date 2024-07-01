from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.data_access.metadata_models import Table, Column, Constraint, Index


def mysql_fetch_tables(mysql: MySQLConnection, excluded_tables=[]) -> [Table]:
    table_data: [Table] = []
    for table in mysql_database_info(mysql):
        if table not in excluded_tables:
            table_data.append(mysql_metadata_table(mysql, table))
    return table_data


def mysql_database_info(mysql: MySQLConnection) -> [str]:
    try:
        with mysql.connection.cursor(dictionary=False) as cursor:

            sql = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{mysql.database}'"
            MigrationLogger().log_info(f"Query: {sql}")

            cursor.execute(sql)

            # Fetch all the rows in a list of lists.
            return [table[0] for table in cursor.fetchall()]


    except Exception as e:
        MigrationLogger().log_error(f"Error searching metadata for database {mysql.database}: {e}")
        raise e


def mysql_metadata_table(mysql: MySQLConnection, table_name):
    try:
        table = fetch_table_info(mysql, table_name)
        if table is None:
            return None
        columns = fetch_columns_info(mysql, table_name)
        if columns is None:
            return None
        constraints = fetch_constraints_info(mysql, table_name)
        if constraints is None:
            return None
        indexes = fetch_indexes_info(mysql, table_name)
        if indexes is None:
            return None
        table.columns = columns
        table.constraints = constraints
        table.indexes = indexes
        return table
    except Exception as e:
        MigrationLogger().log_error(f"Error searching metadata for table {mysql.database}.{table_name}: {e}")
        raise e


def fetch_table_info(mysql: MySQLConnection, table_name):
    try:

        cursor = mysql.connection.cursor(dictionary=True)

        try:
            sql = f"""
            SELECT COUNT(*) as num_tuples FROM {mysql.database}.{table_name};
            """
            MigrationLogger().log_info(f"Query: {sql}")
            cursor.execute(sql)
            result = cursor.fetchone()
            num_tuples = result['num_tuples']
            table = Table(name=table_name, num_tuples=num_tuples)
            return table
        finally:
            # MigrationLogger().log_info(f"Closing the {mysql.database}.{table_name} table count cursor")
            cursor.close()
    except Exception as e:
        MigrationLogger().log_error(f"Error searching metadata for table {mysql.database}.{table_name}: {e}")
        raise e


def fetch_columns_info(mysql: MySQLConnection, table_name):
    try:
        # Consulta para obter informações sobre as colunas da tabela
        sql = f"""
        DESCRIBE {mysql.database}.{table_name};
        """
        MigrationLogger().log_info(f"Query: {sql}")

        cursor = mysql.connection.cursor(dictionary=True)

        columns = []
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                column_name = row['Field']
                data_type = row['Type']
                nullable = row['Null'] == 'YES'
                default = row['Default']
                column = Column(name=column_name, data_type=data_type, nullable=nullable, default=default)
                columns.append(column)
            return columns
        finally:
            cursor.close()
    except Exception as e:
        MigrationLogger().log_error(f"Error fetching columns info for table {mysql.database}.{table_name}: {e}")
        raise e


def fetch_constraints_info(mysql: MySQLConnection, table_name):
    try:
        # Consulta para obter informações sobre as constraints da tabela
        sql = f"""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME 
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{mysql.database}';
        """
        MigrationLogger().log_info(f"Query: {sql}")

        cursor = mysql.connection.cursor(dictionary=True)

        constraints = []
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                constraint_name = row['CONSTRAINT_NAME']
                column_name = row['COLUMN_NAME']
                referenced_table_schema = row['REFERENCED_TABLE_SCHEMA']
                referenced_table_name = row['REFERENCED_TABLE_NAME']
                referenced_column_name = row['REFERENCED_COLUMN_NAME']
                constraint = Constraint(name=constraint_name, column_name=column_name,
                                        referenced_table_schema=referenced_table_schema,
                                        referenced_table_name=referenced_table_name,
                                        referenced_column_name=referenced_column_name)
                constraints.append(constraint)
            return constraints
        finally:
            cursor.close()
    except Exception as e:
        MigrationLogger().log_error(f"Error fetching constraints info for table {mysql.database}.{table_name}: {e}")
        raise e


def fetch_indexes_info(mysql: MySQLConnection, table_name):
    try:
        # Consulta para obter informações sobre os índices da tabela
        sql = f"""
        SELECT INDEX_NAME, COLUMN_NAME, NULLABLE, INDEX_TYPE, NON_UNIQUE
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{mysql.database}';
        """
        MigrationLogger().log_info(f"Query: {sql}")

        cursor = mysql.connection.cursor(dictionary=True)

        indexes = []
        try:
            cursor.execute(sql)
            for row in cursor.fetchall():
                index_name = row['INDEX_NAME']
                column_name = row['COLUMN_NAME']
                nullable = row['NULLABLE'] == 'YES'
                index_type = row['INDEX_TYPE']
                non_unique = row['NON_UNIQUE']
                index = Index(name=index_name, column_name=column_name, nullable=nullable,
                              index_type=index_type, non_unique=non_unique, excluded=False)
                indexes.append(index)
            return indexes
        finally:
            cursor.close()
    except Exception as e:
        MigrationLogger().log_error(f"Error fetching indexes info for table {mysql.database}.{table_name}: {e}")
        raise e
