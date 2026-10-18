"""One sourced current OS/firmware assessment per physical device."""
import sqlite3
import inventory

SOFTWARE_FIELDS=('os_status','os_family','os_name','os_version','firmware_status','firmware_version','source','checked_on')
def empty_software():
    return dict(os_status='unknown',os_family=None,os_name=None,os_version=None,
                firmware_status='unknown',firmware_version=None,source=None,checked_on=None)

def load_software(con,device):
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    row=cursor.execute('SELECT * FROM device_software WHERE device_id=?',(device,)).fetchone()
    return {key:row[key] for key in SOFTWARE_FIELDS} if row else empty_software()

def validate_software(con,data):
    if not isinstance(data,dict):raise ValueError('Software assessment must be a record.')
    result=empty_software();result.update({k:data[k] for k in SOFTWARE_FIELDS if k in data})
    for field in SOFTWARE_FIELDS:
        if field not in ('os_status','firmware_status'):
            value=result[field]
            if value is not None and not isinstance(value,str):raise ValueError('Software values must be text or unknown.')
            result[field]=value.strip() or None if value is not None else None
    for field in ('os_status','firmware_status'):
        if result[field] not in ('unknown','not_applicable','recorded'):raise ValueError('Choose unknown, not applicable or recorded for software status.')
    if result['os_status']=='recorded':
        if not result['os_family'] and not result['os_name']:raise ValueError('Recorded OS needs a family or OS name.')
        if result['os_family'] is not None and con.execute('SELECT 1 FROM os_families WHERE value=?',(result['os_family'],)).fetchone() is None:
            raise ValueError('Choose a valid OS family.')
    elif any(result[k] is not None for k in ('os_family','os_name','os_version')):
        raise ValueError('Unknown or not applicable OS cannot have OS details.')
    if result['firmware_status']=='recorded':
        if result['firmware_version'] is None:raise ValueError('Recorded firmware needs a version.')
    elif result['firmware_version'] is not None:raise ValueError('Unknown or not applicable firmware cannot have a version.')
    if (result['os_status'],result['firmware_status'])!=('unknown','unknown') and result['source'] is None:
        raise ValueError('Information source is required for known software or not applicable status.')
    if result['checked_on'] is not None:
        try:inventory.date(result['checked_on'])
        except Exception:raise ValueError('Software checked date must be a valid calendar date.')
    return result

def save_software(con,device,data):
    names=','.join(SOFTWARE_FIELDS)
    con.execute('INSERT INTO device_software(device_id,'+names+') VALUES('+','.join('?' for _ in range(len(SOFTWARE_FIELDS)+1))+') ON CONFLICT(device_id) DO UPDATE SET '+','.join(k+'=excluded.'+k for k in SOFTWARE_FIELDS),(device,*(data[k] for k in SOFTWARE_FIELDS)))

def audit_software(con):
    for row in con.execute('SELECT device_id FROM device_software'):
        validate_software(con,load_software(con,row[0]))
