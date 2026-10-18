"""Sourced, normalized multi-select device connectivity assessments."""
from copy import deepcopy
import inventory
import sqlite3

KINDS=('interface','protocol')
STATUSES=('unknown','none','recorded')

def empty_profile():
    return {k:{'supported_status':'unknown','usage_status':'unknown','source':None,
               'assessed_on':None,'supported':[],'in_use':[]} for k in KINDS}

def load_connectivity(con,device):
    result=empty_profile()
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    for row in cursor.execute('SELECT * FROM device_connectivity WHERE device_id=? ORDER BY kind',(device,)):
        key=row['kind']
        for field in ('supported_status','usage_status','source','assessed_on'):result[key][field]=row[field]
    for row in cursor.execute('SELECT * FROM device_connections WHERE device_id=? ORDER BY kind,value',(device,)):
        result[row['kind']]['supported'].append(row['value'])
        if row['in_use']:result[row['kind']]['in_use'].append(row['value'])
    return result

def validate_profile(con,profile):
    if set(profile)!=set(KINDS):raise ValueError('Connectivity needs interface and protocol assessments.')
    result=deepcopy(profile)
    for kind in KINDS:
        value=result[kind]
        for field in ('supported_status','usage_status'):
            if value[field] not in STATUSES:raise ValueError('Choose unknown, none or recorded for connectivity status.')
        value.setdefault('assessed_on',None)
        source=value.get('source')
        value['source']=source.strip() or None if isinstance(source,str) else None
        if value.get('assessed_on') is not None:
            try:inventory.date(value['assessed_on'])
            except Exception:raise ValueError('Connectivity assessment date must be a valid calendar date.')
        allowed={r[0] for r in con.execute('SELECT value FROM connection_options WHERE kind=?',(kind,))}
        for field in ('supported','in_use'):
            if not isinstance(value[field],list) or not all(isinstance(v,str) for v in value[field]):raise ValueError('Connectivity choices must be lists.')
            if len(set(value[field]))!=len(value[field]):raise ValueError('Duplicate connectivity selection.')
            if not set(value[field])<=allowed:raise ValueError(f'Unknown {kind} choice; refresh the lists.')
            value[field]=sorted(value[field])
        if not set(value['in_use'])<=set(value['supported']):raise ValueError('An in-use choice must also be marked supported.')
        for status_field,choices in (('supported_status','supported'),('usage_status','in_use')):
            if (value[status_field]=='recorded')!=bool(value[choices]):
                raise ValueError(f'{kind}: recorded needs at least one {choices.replace("_"," ")} choice; unknown/none must have no choices.')
        if value['supported_status']=='none' and value['usage_status']!='none':raise ValueError('No supported capabilities means no capabilities in use.')
    return result

def save_profile(con,device,profile):
    for kind,value in profile.items():
        con.execute('DELETE FROM device_connections WHERE device_id=? AND kind=?',(device,kind))
        con.execute('INSERT INTO device_connectivity(device_id,kind,supported_status,usage_status,source,assessed_on) VALUES(?,?,?,?,?,?) ON CONFLICT(device_id,kind) DO UPDATE SET supported_status=excluded.supported_status,usage_status=excluded.usage_status,source=excluded.source,assessed_on=excluded.assessed_on',
                    (device,kind,value['supported_status'],value['usage_status'],value['source'],value['assessed_on']))
        for choice in value['supported']:
            con.execute('INSERT INTO device_connections(device_id,kind,value,in_use) VALUES(?,?,?,?)',(device,kind,choice,int(choice in value['in_use'])))

def audit(con):
    """Check multi-row invariants that SQL row constraints cannot enforce alone."""
    for row in con.execute('SELECT DISTINCT device_id FROM device_connectivity'):
        validate_profile(con,load_connectivity(con,row[0]))

def missing_sources(profile):
    return [kind for kind,value in profile.items()
            if (value['supported_status'],value['usage_status'])!=('unknown','unknown') and not value.get('source')]
