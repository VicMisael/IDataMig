import os
import json
from typing import Any

from dbmigrator.migration_logging.log import MigrationLogger


class TableState:
    def __init__(self, table_name=None, last_migrated_block=0, fully_migrated=False):
        self.table_name: str = table_name
        self.last_migrated_block: int = last_migrated_block
        self.fully_migrated: bool = fully_migrated


class TablesLog:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TablesLog, cls).__new__(cls)
            cls._instance.tables = []
            #cls._instance.file_path = os.path.join(folder_name, "tables_log.json")
            cls._instance.file_path = "progress.json" 
            if os.path.isfile(cls._instance.file_path):
                cls._instance.load_from_json()
            else:
                cls._instance.save_to_json()
        return cls._instance

    def update_or_add_table(self, table: TableState):
        existing_table_index = next(
            (index for index, t in enumerate(self.tables) if t['table_name'] == table.table_name), None)

        if existing_table_index is not None:
            self.tables[existing_table_index] = table.__dict__
        else:
            self.tables.append(table.__dict__)

        self.save_to_json()

    def get_table(self, table_name) -> Any | None:
        for table in self.tables:
            if table['table_name'] == table_name:
                return TableState(**table)
        
        table_state = TableState(table_name)
        self.update_or_add_table(table_state)
        return table_state

    def save_to_json(self):
        MigrationLogger().log_info(f"saving to file {self.file_path}")
        with open(self.file_path, 'w') as f:
            data = {'tables': self.tables}
            json.dump(data, f, indent=4)

    def load_from_json(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.tables = data.get('tables', [])

