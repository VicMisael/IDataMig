from dbmigrator.configuration_management.db_credentials import  mysql_credentials, postgres_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.database_connections.postgresql_connection import PostgreSQLConnection
from dbmigrator.data_access.postgresql_data_access import postgres_execute_DDL

from dbmigrator.configuration_management.configuration import MigrationConfig
from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.data_migration.mysql_to_postgresql import MySQLToPostgreSQL
from dbmigrator.configuration_management.utils import postgresql_GIST_indexes
from dbmigrator.structure_conversion.csv_utils import folder_name
from dbmigrator.structure_conversion.table_to_json import table_to_json
from dbmigrator.migration_logging.progress_log.tables_log import TablesLog
from dbmigrator.data_access.postgresql_metadata_access import PostgreSQLTableManager


from flask import Flask, render_template
from flask_socketio import SocketIO

import os
import shutil

app = Flask(__name__)
socketio = SocketIO(app)

migration_config = None
config_path = "config.json"

if os.path.exists(config_path):
    migration_config = MigrationConfig.from_json_file(config_path)
    MigrationLogger().log_info(f"Loaded configuration from file")
else:
    migration_config = MigrationConfig.default_config()
    migration_config.save_to_file(config_path)
    MigrationLogger().log_info(f"Loaded default configuration")


migration = MySQLToPostgreSQL(None, None)

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    #print('Client connected')
    pass


@socketio.on('test_connections')
def handle_test_connections():
    mysql, status_mysql = open_mysql_connection()
    postgres, status_postgres = open_postgres_connection()
    try:
        if mysql:
            mysql.close()
        if postgres:
            postgres.close()
    except Exception as e:
        pass

    STATUS = {
        'mysql': status_mysql,
        'postgres': status_postgres
    }
    socketio.emit('status', (STATUS))

@socketio.on('configure')
def handle_configurations(configurations):
    if configurations is not None:
        migration_config.schema_name = configurations['schema_name']
        migration_config.postgres_bulk_size = configurations['postgres_bulk_size']
        migration_config.mysql_batch_size = configurations['mysql_batch_size']
        migration_config.save_to_file(config_path)
        MigrationLogger().log_info(f"Config File Updated")
    STATUS = {
       'configure': {
            'schema_name': migration_config.schema_name,
            'postgres_bulk_size': migration_config.postgres_bulk_size,
            'mysql_batch_size': migration_config.mysql_batch_size,
        }
    }
    socketio.emit('status', (STATUS))

@socketio.on('load_metadata')
def handle_load_metadata(reload):
    if reload:
        mysql, status_mysql = open_mysql_connection()
        postgres, status_postgres = open_postgres_connection()
        open_migration(mysql, postgres)
        if not mysql:
            return
        migration.load_mysql_metadata_json(migration_config.json_name)

        try:
            if mysql:
                mysql.close()
            if postgres:
                postgres.close()
        except Exception as e:
            pass

    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))
    elif reload is None:
        MigrationLogger().log_warning(f"Table metadata missing; conversion step may have been skipped.")
        STATUS = {'tables': []}
        socketio.emit('status', (STATUS))

@socketio.on('update_table_metadata')
def handle_update_table_metadata(table):
    table_name = None
    excluded = None
    if table:
        table_name = table['name']
        excluded = table['excluded']
        type_t = table['type']
        
    if table_name and migration.tables:
        for t in migration.tables:
            if t.name == table_name:
                #t.excluded = excluded
                if type_t is not None:
                    type_t = str(type_t)
                    #value = getattr(t, type_t)
                    setattr(t, type_t, False)
                    #t.excluded = True
                else:
                    t.excluded = excluded
                
                break
              
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))



@socketio.on('update_table_metadata_select_all')
def handle_update_table_metadata_select_all():   
    if migration.tables:
        json_list = []
        for table in migration.tables:
            table.excluded = False
            json_list.append(table_to_json(table))
            
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)
        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))
    else:
        MigrationLogger().log_warning(f"Table metadata missing")

@socketio.on('update_table_metadata_deselect_all')
def handle_update_table_metadata_deselect_all():
    if migration.tables:
        json_list = []
        for table in migration.tables:
            table.excluded = True
            json_list.append(table_to_json(table))
            
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)
        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))
    else:
        MigrationLogger().log_warning(f"Table metadata missing")


@socketio.on('handle_sequences')
def handle_sequences(table, new_value):
    if migration.tables:
        for t in migration.tables:           
            if t.name == table:
                postgres, status_postgres = open_postgres_connection()
                if not postgres:
                    return
               
                pg_manager = PostgreSQLTableManager(postgres, t.name, schema=migration_config.schema_name)
                
                if new_value is None:
                    new_value = pg_manager.get_sequence_current_value()
                else:
                    pg_manager.set_sequence_value(new_value)
                    
                if postgres:
                    postgres.close()
                    
                socketio.emit('update_sequence', (table, new_value) )
                return
        
        MigrationLogger().log_info(f"Table: {table} not found in metadata")
    else:
        MigrationLogger().log_warning(f"Table metadata missing")
    
@socketio.on('handle_specific_index')
def handle_specific_index(table_name, index_name, excluded):
    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
            if table.name == table_name:
                for index in table.indexes:
                    if index.name == index_name:
                        index.excluded = excluded          
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)
        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))
    else:
        MigrationLogger().log_warning(f"Table metadata missing")

@socketio.on('clear_metadata')
def handle_clear_metadata():
   
    if os.path.exists(migration_config.json_name):
        MigrationLogger().log_warning(f"Clearing metadata file: {migration_config.json_name}")
        os.remove(migration_config.json_name)
    else:
        MigrationLogger().log_warning(f"File {migration_config.json_name} does not exist")
    
    if os.path.exists(migration_config.progress_json_name):
        MigrationLogger().log_warning(f"Clearing metadata file: {migration_config.progress_json_name}")
        os.remove(migration_config.progress_json_name)
    else:
        MigrationLogger().log_warning(f"File {migration_config.progress_json_name} does not exist")
    
    migration.tables = []
    STATUS = {'tables': []}
    socketio.emit('status', (STATUS))
    
        
@socketio.on('clear_files')
def handle_clear_files():
    if os.path.exists(folder_name):
        MigrationLogger().log_warning(f"Clearing folder: {folder_name}")
        shutil.rmtree(folder_name)
    else:
        MigrationLogger().log_warning(f"Folder {folder_name} does not exist")
        

@socketio.on('clear_database')
def handle_clear_files():
    postgres, status_postgres = open_postgres_connection()
    if not postgres:
        MigrationLogger().log_error(f"Could not connect to Postgres")
        return

    if migration_config.schema_name:
        postgres_execute_DDL(postgres, "DROP SCHEMA IF EXISTS " + migration_config.schema_name + " CASCADE;")
        postgres_execute_DDL(postgres, "CREATE SCHEMA " + migration_config.schema_name + ";")
        postgres.connection.commit()
    else:
        MigrationLogger().log_warning(f"Target schema name not set")
    
    try:       
        if postgres:
            postgres.close()
    except Exception as e:
        pass
    
@socketio.on('migrate_tables')
def handle_migrate_tables():
    mysql, status_mysql = open_mysql_connection()
    postgres, status_postgres = open_postgres_connection()
    if not postgres:
        return
    open_migration(mysql, postgres)
    #migration.load_mysql_metadata_json(migration_config.json_name)
    table_sql_error = ""
    enum_sql_error = ""
    table_name_error = ""
    try:
        if migration.tables:
            for t in migration.tables:
                if t.excluded is False and t.table_commited is False:
                    table_name_error = t.name
                    table_sql, enum_sql, constraints, primary_keys, indexes = migration.table_to_sql(table=t, schema=migration_config.schema_name, buffer=False)
                    table_sql_error = table_sql
                    enum_sql_error = enum_sql
                    #MigrationLogger().log_error(f"sql: {enum_sql_error} {table_sql_error}")

                    if enum_sql is not None and enum_sql != "":
                        postgres_execute_DDL(postgres, enum_sql)
                    postgres_execute_DDL(postgres, table_sql)
                    postgres.connection.commit()
                    t.table_commited = True
    except Exception as e:
        MigrationLogger().log_error(f"Error migrating table [{table_name_error}] sql: {enum_sql_error} {table_sql_error} -> {str(e)}")

    try:
        if mysql:
            mysql.close()
        if postgres:
            postgres.close()
    except Exception as e:
        pass

    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))


@socketio.on('migrate_primary_keys')
def handle_migrate_primary_keys():
    mysql, status_mysql = open_mysql_connection()
    postgres, status_postgres = open_postgres_connection()
    if not postgres:
        return
    open_migration(mysql, postgres)
    #migration.load_mysql_metadata_json(migration_config.json_name)
    primary_keys_error = ""
    table_name_error = ""
    try:
        if migration.tables:
            for t in migration.tables:
                if t.excluded is False and t.primary_key_commited is False:
                    table_name_error = t.name
                    table_sql, enum_sql, constraints, primary_keys, indexes = migration.table_to_sql(table=t, schema=migration_config.schema_name, buffer=False)
                    primary_keys_error = primary_keys
                    if primary_keys is not None and primary_keys != "":
                        postgres_execute_DDL(postgres, primary_keys)
                    postgres.connection.commit()
                    t.primary_key_commited = True
    except Exception as e:
        MigrationLogger().log_error(f"Error migrating primary key [{table_name_error}] sql: {primary_keys_error} -> {str(e)}")

    try:
        if mysql:
            mysql.close()
        if postgres:
            postgres.close()
    except Exception as e:
        pass

    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))

@socketio.on('migrate_constraints')
def handle_migrate_constraints():
    mysql, status_mysql = open_mysql_connection()
    postgres, status_postgres = open_postgres_connection()
    if not postgres:
        return
    open_migration(mysql, postgres)
    #migration.load_mysql_metadata_json(migration_config.json_name)
    constraints_error = ""
    table_name_error = ""
    try:
        if migration.tables:
            for t in migration.tables:
                if t.excluded is False and t.constraints_commited is False:
                    table_name_error = t.name
                    table_sql, enum_sql, constraints, primary_keys, indexes = migration.table_to_sql(table=t, schema=migration_config.schema_name, buffer=False)
                    constraints_error = constraints
                    if constraints is not None and constraints != "":
                        postgres_execute_DDL(postgres, constraints)
                    postgres.connection.commit()
                    t.constraints_commited = True
    except Exception as e:
        MigrationLogger().log_error(f"Error migrating constraint [{table_name_error}] sql: {constraints_error} -> {str(e)}")

    try:
        if mysql:
            mysql.close()
        if postgres:
            postgres.close()
    except Exception as e:
        pass

    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))

@socketio.on('migrate_indexes')
def handle_migrate_indexes():
    mysql, status_mysql = open_mysql_connection()
    postgres, status_postgres = open_postgres_connection()
    if not postgres:
        return
    open_migration(mysql, postgres)
    #migration.load_mysql_metadata_json(migration_config.json_name)
    indexes_error = ""
    table_name_error = ""
    try:
        if migration.tables:
            for t in migration.tables:
                if t.excluded is False and t.indexes_commited is False:
                    table_name_error = t.name
                    table_sql, enum_sql, constraints, primary_keys, indexes = migration.table_to_sql(table=t, schema=migration_config.schema_name, buffer=False)
                    indexes_error = indexes
                    if indexes is not None and indexes != "":
                        postgres_execute_DDL(postgres, indexes)
                    postgres.connection.commit()
                    t.indexes_commited = True
    except Exception as e:
        MigrationLogger().log_error(f"Error migrating index [{table_name_error}] sql: {indexes_error} -> {str(e)}")

    try:
        if mysql:
            mysql.close()
        if postgres:
            postgres.close()
    except Exception as e:
        pass

    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))



@socketio.on('migrate_tuples')
def handle_migrate_tuples():
    mysql, status_mysql = open_mysql_connection()
    postgres, status_postgres = open_postgres_connection()
    if not postgres:
        return
    open_migration(mysql, postgres)

    tuples_error = ""
    table_name_error = ""
    try:
        if migration.tables:
            for t in migration.tables:
                table_log = TablesLog().get_table(t.name)

                if t.excluded is False and table_log.fully_migrated is False:
                    table_name_error = t.name
                    progress_state = {
                                'name':t.name,
                                'file_name':t.name + ".csv",
                                'total': t.num_tuples,
                                'intermediate_file_progress': 0,
                                'migrate_progress': 0
                    }


                    def progress_file_callback(progress):
                        progress_state['intermediate_file_progress'] = progress
                        if progress % migration.mysql_batch_size == 0 or progress == t.num_tuples:
                            socketio.emit('update_progress', progress_state )

                    def progress_migration_callback(progress):
                        progress_state['migrate_progress'] = progress
                        if progress % migration.postgresql_bulk_size  == 0 or progress == t.num_tuples:
                            socketio.emit('update_progress', progress_state )

                    migration.save_table_to_csv(t, progress_file_callback)
                    migration.read_from_csv(t, migration_config.schema_name, progress_migration_callback)

                    t.tuples_commited = True

                    migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

                    json_list = []
                    for table in migration.tables:
                        json_list.append(table_to_json(table))

                    STATUS = {'tables': json_list}
                    socketio.emit('status', (STATUS))

    except Exception as e:
        MigrationLogger().log_error(f"Error migrating tuple [{table_name_error}] sql: {tuples_error} -> {str(e)}")

    try:
        if mysql:
            mysql.close()
        if postgres:
            postgres.close()
    except Exception as e:
        pass

    if migration.tables:
        json_list = []
        for table in migration.tables:
            json_list.append(table_to_json(table))
        migration.save_mysql_metadata_json(migration.tables, migration_config.json_name)

        STATUS = {'tables': json_list}
        socketio.emit('status', (STATUS))


def open_mysql_connection():
    mysql_conn = MySQLConnection(mysql_credentials())
    status = {
        'MYSQL_DATABASE': mysql_conn.db_credentials.database,
        'MYSQL_USER': mysql_conn.db_credentials.user,
        'MYSQL_HOST': mysql_conn.db_credentials.host,
        'MYSQL_PORT': mysql_conn.db_credentials.port,
    }
    try:
        mysql_conn.create()
        status['connected'] = True if mysql_conn.connection else False
        return mysql_conn, status
    except Exception as e:
        status['connected'] = False
        status['error'] = str(e)
        return None, status

def open_postgres_connection():
    postgres_conn = PostgreSQLConnection(postgres_credentials())
    status = {
        'POSTGRES_DBNAME': postgres_conn.db_credentials.database,
        'POSTGRES_USER': postgres_conn.db_credentials.user,
        'POSTGRES_HOST': postgres_conn.db_credentials.host,
        'POSTGRES_PORT': postgres_conn.db_credentials.port,
    }
    try:
        postgres_conn.create()
        status['connected'] = True if postgres_conn.connection else False
        return postgres_conn, status
    except Exception as e:
        status['connected'] = False
        status['error'] = str(e)
        return None, status



def open_migration(mysql, postgresql):

    migration.mysql_conn = mysql
    migration.postgres_conn = postgresql

    migration.GIST_indexes = postgresql_GIST_indexes()
    migration.bulk_commit = False #migration_config.bulk_commit
    migration.postgresql_bulk_size = migration_config.postgres_bulk_size
    migration.mysql_batch_size = migration_config.mysql_batch_size
    migration.excluded_tables = migration_config.excluded_tables

    return migration


from dbmigrator.migration_logging.log import MigrationLogger
from dbmigrator.migration_logging.observer.i_observer import ILoggingObserver
from dbmigrator.migration_logging.observer.logging_level import LoggingLevel

if __name__ == '__main__':
    class NewObserver(ILoggingObserver):
            def __init__(self):
                pass

            def push(self, message, level: LoggingLevel):
                LOG = {
                    'log_level': str(level).split('.')[-1],
                    'message': message
                }
                socketio.emit('log', (LOG))

    newObserver = NewObserver()
    MigrationLogger().register_observer(newObserver)


    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5005,host="0.0.0.0")
