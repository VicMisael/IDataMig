class Table:
    def __init__(self, name, num_tuples, excluded=False, columns=None, constraints=None, indexes=None,
                 table_commited=False, primary_key_commited=False, constraints_commited=False,
                 indexes_commited=False, tuples_commited=False):
        self.name = name
        self.num_tuples = num_tuples
        self.columns = columns or []
        self.constraints = constraints or []
        self.indexes = indexes or []

        # Used to track if the table has been commited to the target database or removed from migration
        self.excluded = excluded
        self.table_commited = table_commited
        self.primary_key_commited = primary_key_commited
        self.constraints_commited = constraints_commited
        self.indexes_commited = indexes_commited
        self.tuples_commited = tuples_commited


class Column:
    def __init__(self, name, data_type, nullable, default):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.default = default


class Constraint:
    def __init__(self, name, column_name, referenced_table_schema, referenced_table_name, referenced_column_name):
        self.name = name
        self.column_name = column_name
        self.referenced_table_schema = referenced_table_schema
        self.referenced_table_name = referenced_table_name
        self.referenced_column_name = referenced_column_name


class Index:
    def __init__(self, name, column_name, nullable, index_type, non_unique, excluded):
        self.name = name
        self.column_name = column_name
        self.nullable = nullable
        self.index_type = index_type
        self.non_unique = non_unique
        self.excluded: bool = excluded
