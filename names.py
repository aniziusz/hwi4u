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



def suggested_name(manufacturer,model,device_type,used=()):
    """Descriptive Unicode name, not a hostname; caller applies only on explicit action."""
    def part(value):
        if not isinstance(value,str):return ''
        return ' '.join(''.join(c for c in value if unicodedata.category(c) not in ('Cc','Cs') and c not in ('\u2028','\u2029')).split())
    identity=' '.join(filter(None,(part(manufacturer),part(model))))
    base=' — '.join(filter(None,(identity,part(device_type))))
    if not base:return None
    occupied={name_key(n) for n in used}
    candidate=base[:100].rstrip();number=1
    while name_key(candidate) in occupied:
        number+=1;suffix=' ('+str(number)+')';candidate=base[:100-len(suffix)].rstrip()+suffix
    return validate_name(candidate)
