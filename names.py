"""Unicode device-name policy shared by save, live feedback and database audit."""
import unicodedata

def name_key(name):
    return ' '.join(unicodedata.normalize('NFKC', name).casefold().split())


def validate_name(value):
    if not isinstance(value,str) or not value.strip():raise ValueError('Name is required.')
    if any(unicodedata.category(char) in ('Cc','Cs') or char in ('\u2028','\u2029') for char in value):
        raise ValueError('Name cannot contain control characters or line breaks.')
    value=' '.join(value.split())
    if len(value)>100:raise ValueError('Name must be at most 100 characters.')
    return value

