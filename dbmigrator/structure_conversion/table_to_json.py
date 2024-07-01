import json
from dbmigrator.data_access.metadata_models import Table, Column, Constraint, Index
from dbmigrator.migration_logging.log import MigrationLogger


def save_json_file(tables, file_name):
    try:
        MigrationLogger().log_info(f"Saving JSON file: {file_name}")
        data = database_to_dict_list(tables)
        with open(file_name, "w+") as outfile:
            json.dump(data, outfile, indent=4)
    except Exception as e:
        MigrationLogger().log_error(f"Error occurred while saving JSON file: {e}")

def load_json_file(file_name):
    try:
        with open(file_name, "r") as f:
            MigrationLogger().log_info(f"Loading JSON file: {file_name}")
            data = json.load(f)
            tables = dict_list_to_table_list(data)
            return tables
    except FileNotFoundError:
        MigrationLogger().log_error(f"File '{file_name}' not found.")
        return None
    except Exception as e:
        MigrationLogger().log_error(f"Error occurred while loading JSON file: {e}")
        return None


def database_to_dict_list(database: [Table]):
    return [table_to_dict(table) for table in database]


def table_to_dict(table):
    return {
        "name": table.name or "",
        "num_tuples": table.num_tuples or 0,
        "columns": [column_to_dict(col) for col in table.columns],
        "constraints": [constraint_to_dict(con) for con in table.constraints],
        "indexes": [index_to_dict(ind) for ind in table.indexes],
        
        "excluded": table.excluded,
        "table_commited": table.table_commited,
        "primary_key_commited": table.primary_key_commited,
        "constraints_commited": table.constraints_commited,
        "indexes_commited": table.indexes_commited,
        "tuples_commited": table.tuples_commited
        
    }
    
    
def table_to_dict_simplified(table):
    return {
        "name": table.name or "",
        "num_tuples": table.num_tuples or 0,
        "excluded": table.excluded,
        "table_commited": table.table_commited,
        "primary_key_commited": table.primary_key_commited,
        "constraints_commited": table.constraints_commited,
        "indexes_commited": table.indexes_commited,
        "tuples_commited": table.tuples_commited
        
    }


def table_to_json(table):
    return json.dumps(table_to_dict(table))

def table_to_json_simplified(table):
    return json.dumps(table_to_dict_simplified(table))


def dict_list_to_table_list(data):
    tables: [Table] = []
    for table in data:
        tables.append(dict_to_table(table))
    return tables


def dict_to_table(data):
    return Table(
        name=data["name"],
        num_tuples=data["num_tuples"],
        excluded=data["excluded"],
        columns=[dict_to_column(col_data) for col_data in data["columns"]],
        constraints=[dict_to_constraint(con_data) for con_data in data["constraints"]],
        indexes=[dict_to_index(ind_data) for ind_data in data["indexes"]],
        table_commited=data["table_commited"],
        primary_key_commited=data["primary_key_commited"],
        constraints_commited=data["constraints_commited"],
        indexes_commited=data["indexes_commited"],
        tuples_commited=data["tuples_commited"]
    )


def column_to_dict(column):
    return {
        "name": column.name,
        "data_type": column.data_type,
        "nullable": column.nullable,
        "default": column.default
    }


def dict_to_column(data):
    return Column(
        name=data["name"],
        data_type=data["data_type"],
        nullable=data["nullable"],
        default=data["default"]
    )


def constraint_to_dict(constraint):
    return {
        "name": constraint.name,
        "column_name": constraint.column_name,
        "referenced_table_schema": constraint.referenced_table_schema,
        "referenced_table_name": constraint.referenced_table_name,
        "referenced_column_name": constraint.referenced_column_name
    }


def dict_to_constraint(data):
    return Constraint(
        name=data["name"],
        column_name=data["column_name"],
        referenced_table_schema=data["referenced_table_schema"],
        referenced_table_name=data["referenced_table_name"],
        referenced_column_name=data["referenced_column_name"]
    )


def index_to_dict(index):
    return {
        "name": index.name,
        "column_name": index.column_name,
        "nullable": index.nullable,
        "index_type": index.index_type,
        "non_unique": index.non_unique,
        "excluded": index.excluded
    }


def dict_to_index(data):
    return Index(
        name=data["name"],
        column_name=data["column_name"],
        nullable=data["nullable"],
        index_type=data["index_type"],
        non_unique=data["non_unique"],
        excluded=data["excluded"]
    )
