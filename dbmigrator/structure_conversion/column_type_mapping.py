mysql_to_pgsql_type_mapping = {
    'bigint(20)': 'BIGINT',
    'bigint(20) unsigned': 'BIGINT',  # Consider using a check constraint if necessary
    'date': 'DATE',
    'datetime': 'TIMESTAMP WITHOUT TIME ZONE',
    'double': 'DOUBLE PRECISION',
    'double unsigned': 'DOUBLE PRECISION',  # Consider check constraint for positive values
    'enum': 'TEXT',
    'geometry': 'public.geometry(Polygon,4326)', # Consider using PostGIS --> CREATE EXTENSION postgis; 
    'int(10) unsigned': 'INTEGER',
    'int(11)': 'INTEGER',
    'longtext': 'TEXT',
    'mediumtext': 'TEXT',
    'point': 'public.geometry(Point,4326)',
    'text': 'TEXT',
    'timestamp': 'TIMESTAMP WITHOUT TIME ZONE',
    'tinyint(1)': 'boolean',  # Commonly used for boolean values in MySQL
    # For VARCHARs, directly map to VARCHAR with the same length
    'varchar(10)': 'VARCHAR(10)',
    'varchar(100)': 'VARCHAR(100)',
    'varchar(11)': 'VARCHAR(11)',
    'varchar(15)': 'VARCHAR(15)',
    'varchar(20)': 'VARCHAR(20)',
    'varchar(200)': 'VARCHAR(200)',
    'varchar(255)': 'VARCHAR(255)',
    'varchar(500)': 'VARCHAR(500)',
    'varchar(7)': 'VARCHAR(7)',
    'varchar(8)': 'VARCHAR(8)',
    
    # For ENUMs, map to TEXT
    "enum('A+','A-','B+','B-','AB+','AB-','O+','O-')": 'enum_blood_type',
    "enum('public','private','secret')": 'enum_level',
    "enum('lpr','ptz','context','bullet','dome')": 'enum_type',
    "enum('drug','object','organization','people','vehicle','weapon','animal')": 'enum_item_type',
    "enum('create','update','delete')": 'enum_operation'
}