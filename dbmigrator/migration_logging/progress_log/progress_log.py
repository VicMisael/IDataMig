import json


class ProgressLog:

    def __init__(self, file_path="progress.json"):
        self.file_path = file_path
        self.enums_created = False
        self.are_tables_created = False  # DDL creation
        self.executed_data_migration = False
        self.migrated_tables = []
        self.generated_primary_keys = False
        self.primary_keys_list = []
        self.generated_indexes = False
        self.indexes_list = []
        self.generated_constraints = False
        self.constraint_list = []

    # Setter methods that set the corresponding attribute to True
    def set_enums_created(self):
        self.enums_created = True
        self.save_to_file()

    def set_are_tables_created(self):
        self.are_tables_created = True
        self.save_to_file()

    def set_executed_data_migration(self):
        self.executed_data_migration = True
        self.save_to_file()

    def set_generated_primary_keys(self):
        self.generated_primary_keys = True
        self.save_to_file()

    def set_generated_indexes(self):
        self.generated_indexes = True
        self.save_to_file()

    def set_generated_constraints(self):
        self.generated_constraints = True
        self.save_to_file()

    def add_migrated_table(self, table_name):
        if table_name not in self.migrated_tables:
            self.migrated_tables.append(table_name)
        self.save_to_file()

    def add_primary_key(self, primary_key):
        if primary_key not in self.primary_keys_list:
            self.primary_keys_list.append(primary_key)
        self.save_to_file()

    def add_index(self, index):
        if index not in self.indexes_list:
            self.indexes_list.append(index)
        self.save_to_file()

    def add_constraint(self, constraint):
        if constraint not in self.constraint_list:
            self.constraint_list.append(constraint)
        self.save_to_file()

    def save_to_file(self):
        data_to_save = {key: value for key, value in self.__dict__.items() if key != "file_path"}  # Exclude file_path
        with open(self.file_path, 'w+') as file:
            json.dump(data_to_save, file, indent=4)

    @classmethod
    def load_from_file(cls, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        instance = cls(file_path=file_path)  # Create an instance with the provided file path
        for key, value in data.items():
            setattr(instance, key, value)  # Set attributes except for file_path
        return instance
