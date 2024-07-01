import builtins
from datetime import datetime

csv_field_limit: int = 20*262144

folder_name = 'data'

type_conversion_map = {
    'NoneType': lambda x: None,
    'bytearray': lambda x: bytearray.fromhex(x),
    'datetime': lambda x: datetime.fromisoformat(x),
    'date': lambda x: datetime.fromisoformat(x),
    'bool': lambda x: x == 'True'
}


def convert_to_type(value, type_name):
    # Try to get the type object from globals() dictionary
    return getattr(builtins, type_name)(value)


def deserialize_value(s):
    """
    Deserializes a value from a string with type information back to its original type.
    """
    type_str, value_str = s.split(':', 1)
    if type_str == 'bytearray':
        # Convert hex string back to bytearray
        return bytearray.fromhex(value_str)
    if type_str in type_conversion_map:
        return type_conversion_map[type_str](value_str)
    return convert_to_type(value_str, type_str)


def serialize_value(value, col):
    """
    Serializes a value to a string with type information.
    """

    if col.data_type == 'tinyint(1)':
        if value == 1:
            return 'bool:True'
        return 'bool:False'
    
    if isinstance(value, bytearray):
        return f"bytearray:{value.hex()}"
    return f"{type(value).__name__}:{value}"
