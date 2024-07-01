
def numeric_or_string_value(s):
    try:
        float(s)
        return s
    except ValueError:
        return f"'{s}'"


def format_reserved_word(word):
    reserved_words = {'NAME', 'DEFAULT', 'ORDER', 'TYPE', 'KEY'}

    if word.upper() in reserved_words:
        return f'"{word}"'
    else:
        return word


def postgresql_GIST_indexes():
    return []
