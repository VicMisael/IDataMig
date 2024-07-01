import json
from typing import List


class MigrationConfig:
    def __init__(self, schema_name: str,
                 json_name: str,
                 progress_json_name: str,
                 bulk_commit: bool,
                 excluded_tables: List[str],
                 postgres_bulk_size: int = 1000,
                 mysql_batch_size: int = 1000):
        self.schema_name = schema_name
        self.json_name = json_name
        self.progress_json_name = progress_json_name
        self.bulk_commit = bulk_commit
        self.mysql_batch_size = mysql_batch_size
        self.excluded_tables = excluded_tables
        self.postgres_bulk_size = postgres_bulk_size

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            "schema_name": self.schema_name,
            "json_name": self.json_name,
            "progress_json_name": self.progress_json_name,
            "bulk_commit": self.bulk_commit,
            "mysql_batch_size": self.mysql_batch_size,
            "excluded_tables": self.excluded_tables,
            "postgres_bulk_size": self.postgres_bulk_size
        }

    def to_json(self):
        """Serializes the object to a JSON string."""
        return json.dumps(self.to_dict(), indent=4)

    def save_to_file(self, file_path: str):
        """Saves the configuration to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        """Creates an instance of the class from a dictionary."""
        return cls(
            schema_name=data.get("schema_name"),
            json_name=data.get("json_name"),
            progress_json_name=data.get("progress_json_name"),
            bulk_commit=data.get("bulk_commit"),
            mysql_batch_size=data.get("mysql_batch_size"),
            excluded_tables=data.get("excluded_tables"),
            postgres_bulk_size=data.get("postgres_bulk_size")
        )

    @classmethod
    def from_json_file(cls, file_path: str):
        """Creates an instance of the class from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            return cls.from_dict(data)

    @classmethod
    def default_config(cls):
        return cls("test", "metadata.json", "progress.json", True, ['logs'])
