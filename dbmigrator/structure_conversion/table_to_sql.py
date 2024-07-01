from dbmigrator.data_access.metadata_models import Table, Constraint, Index
from dbmigrator.structure_conversion.column_type_mapping import mysql_to_pgsql_type_mapping
from dbmigrator.configuration_management.utils import format_reserved_word, numeric_or_string_value

def table_to_mysql_ddl(table: Table, schema=""):
    if schema != "":
        schema += "."
    columns_sql = []
    for col in table.columns:
        nullable = "NULL" if col.nullable else "NOT NULL"
        columns_sql.append(f'{col.name} {col.data_type} {nullable}')
    columns_sql = ',\n'.join(columns_sql)
    return f"CREATE TABLE {schema}{table.name} (\n{columns_sql}\n);"


def table_to_postgres_ddl(table: Table, schema=""):
    if schema != "":
        schema += "."

    columns_sql = []
    enum_sqls = []  

    for col in table.columns:
        nullable = "NULL" if col.nullable else "NOT NULL"
        data_type = col.data_type
        
        type_sql = mysql_to_pgsql_type_mapping.get(data_type)
        
        if data_type.startswith("enum(") and data_type.endswith(")"):
            #enum_name = f"{table.name}_{col.name}_enum"
            enum_name = type_sql
            enum_sql = f"CREATE TYPE {schema}{enum_name} AS {data_type};"
            enum_sqls.append(enum_sql)
            type_sql = f'{schema}{enum_name}'

        if type_sql is None or type_sql == "":
            raise Exception(f"Type {data_type} not found in mapping")
        
        #if type_sql == "geometry(Point)":
            #print(f"Geometry column {col.name} in table {table.name} is of type {data_type}. Consider using PostGIS --> CREATE EXTENSION postgis; ")
        
        default = ""
        if col.default is not None:
            if col.default == "current_timestamp()":
                default = f" DEFAULT CURRENT_TIMESTAMP"
            else:
                default = f" DEFAULT { numeric_or_string_value(col.default) }"
                
            if type_sql == 'boolean':
                default = f" DEFAULT " + ("TRUE" if col.default == "1" else "FALSE")
            
        columns_sql.append(f'{format_reserved_word(col.name)} {type_sql} {nullable}{default}')

    columns_sql = ',\n'.join(columns_sql)
    create_table_sql = f"CREATE TABLE {schema}{table.name} (\n{columns_sql}\n);"

    return create_table_sql, enum_sqls

'''
def table_to_postgres_ddl_old(table: Table, schema=""):
    if schema != "":
        schema += "."

    columns_sql = []
    for col in table.columns:
        nullable = "NULL" if col.nullable else "NOT NULL"
        type = mysql_to_pgsql_type_mapping[col.data_type]
        if type == None or type == "":
            raise Exception(f"Type {col.data_type} not found in mapping")
        columns_sql.append(f'{col.name} {type} {nullable}')
    columns_sql = ',\n'.join(columns_sql)
    return f"CREATE TABLE {schema}{table.name} (\n{columns_sql}\n);"
'''

def constraints_to_sql(constraints: [Constraint], table=None, schema=""):
    if schema != "":
        schema += "."
    if table is None:
        raise Exception("Table is required")
    
    constraints_sql = []
    constraints_primary_key = []
    
    for constraint in constraints:
        if constraint.name == "PRIMARY":
            # Add the instruction to add the primary key to the table
            sql = f"\nALTER TABLE {schema}{table} ADD PRIMARY KEY ({constraint.column_name});"
            constraints_primary_key.append(sql)
            # Creates the sequence for the id column
            sequence_sql = f"\nCREATE SEQUENCE {schema}{table}_id_seq;"
            constraints_primary_key.append(sequence_sql)
            # Sets the id column to default to string
            default_sql = f"\nALTER TABLE {schema}{table} ALTER COLUMN {constraint.column_name} SET DEFAULT nextval('{schema}{table}_id_seq');"
            constraints_primary_key.append(default_sql)
            # Sets the sequence value to the maximum id value in the table
            setval_sql = f"\nSELECT setval('{schema}{table}_id_seq', (SELECT COALESCE(MAX({constraint.column_name}), 1) FROM {schema}{table}));"
            constraints_primary_key.append(setval_sql)
        else:   
            if constraint.referenced_table_name is None: # not a foreign key
                sql = f"\nALTER TABLE {schema}{table} ADD CONSTRAINT {constraint.name} UNIQUE ({constraint.column_name});"
                constraints_sql.append(sql)
            else:
                sql = f"\nALTER TABLE {schema}{table} ADD CONSTRAINT {constraint.name} FOREIGN KEY ({constraint.column_name}) REFERENCES {schema}{constraint.referenced_table_name}({constraint.referenced_column_name});"
                constraints_sql.append(sql)
    return '\n'.join(constraints_sql), '\n'.join(constraints_primary_key)



INDEX_NAME_MAP = {}

def indexes_to_sql(indexes: [Index], table=None, schema="", GIST_indexes=None):
    if schema != "":
        schema += "."  # If a schema is provided, prepend it with a dot
    if table is None:
        raise Exception("Table is required")
    
    index_groups = {}  # Dictionary to group indexes by name
    for index in indexes:
        if index.name == "PRIMARY" or index.non_unique == 0 or index.excluded:  # Ignore unique indexes and primary keys
            continue
        if index.name not in index_groups:
            index_groups[index.name] = []  # Create a new list for the index name if it doesn't exist yet
        index_groups[index.name].append(format_reserved_word(index.column_name))  # Add the column name to the index's column list
    
    indexes_sql = []
    for index_name, column_names in index_groups.items():
        
        index_formatted_name = index_name
        if index_name not in INDEX_NAME_MAP:
            INDEX_NAME_MAP[index_name] = 1
        else:
            INDEX_NAME_MAP[index_name] += 1
            index_formatted_name = index_name + "_" + str(INDEX_NAME_MAP[index_name])
        
        if GIST_indexes and index_name in GIST_indexes:
            sql = f"\nCREATE INDEX {index_formatted_name} ON {schema}{table} USING GIST ({', '.join(column_names)});"
        else:
            sql = f"\nCREATE INDEX {index_formatted_name} ON {schema}{table} ({', '.join(column_names)});"
        indexes_sql.append(sql)
    
    return '\n'.join(indexes_sql)