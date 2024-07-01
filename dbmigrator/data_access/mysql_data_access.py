from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.configuration_management.utils import format_reserved_word

class MySQLTableIterator:
    def __init__(self, mysql, table, batch_size=10000):
        self.mysql = mysql
        self.table = table
        self.batch_size = batch_size
        self.cursor = None
        self.current_batch = []

        self.columns = []
        for column in self.table.columns:
            if column.data_type.lower() == 'geometry':
                self.columns.append(f"ST_AsText(`{column.name}`) AS `{column.name}`")
            elif column.data_type.lower() == 'point':
                #self.columns.append(f"`{column.name}`")
                self.columns.append(f"ST_AsText(`{column.name}`) AS `{column.name}`")
            else:
                self.columns.append(f"`{column.name}`")

        self.columns = ", ".join(self.columns)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cursor is None:
            self.cursor = self.mysql.connection.cursor(buffered=False)
            database = self.mysql.connection.database
            if database != "":
                database += "."
            sql = f"SELECT {self.columns} FROM {database}{self.table.name}"
            MigrationLogger().log_info(f"Query: {sql}")
            self.cursor.execute(sql)

        if not self.current_batch:
            self.current_batch = self.cursor.fetchmany(self.batch_size)
            if not self.current_batch:
                self.cursor.close()
                raise StopIteration

        row = self.current_batch.pop(0)
        return row

    def close(self):
        if self.cursor:
            self.cursor.close()
