"""Immutable reusable places and device-specific placement; no guessed migration."""
import datetime as dt
from decimal import Decimal, InvalidOperation
import json
import re
import sqlite3
import unicodedata
import uuid

PLACE_FIELDS=('country','postal_code','city','street','house_number','building','floor','room')
PLACEMENT_FIELDS=('position','height_m','height_reference','notes')
REFERENCES=('finished_floor','ground_level','other')

def empty_location():
    return dict(state='unknown',**{k:None for k in (*PLACE_FIELDS,*PLACEMENT_FIELDS)})

def clean(value,limit=200):
    if value is None:return None
    if not isinstance(value,str) or any(unicodedata.category(c)=='Cc' for c in value):
        raise ValueError('Location fields must be single-line text.')
    value=' '.join(value.split())
    if len(value)>limit:raise ValueError('Location fields must contain at most 200 characters.')
    return value or None

def validate_location(data):
    if not isinstance(data,dict):raise ValueError('Invalid location details.')
    result=empty_location();result['state']=data.get('state','unknown')
    if result['state'] not in ('unknown','recorded','not_applicable'):raise ValueError('Choose a valid location status.')
    for key in (*PLACE_FIELDS,*PLACEMENT_FIELDS):result[key]=clean(data.get(key))
    if result['height_m'] is not None:
        try:
            if not re.fullmatch(r'[0-9]+(?:[.,][0-9]+)?',result['height_m']):raise InvalidOperation
            height=Decimal(result['height_m'].replace(',','.'))
            if not height.is_finite() or height<0 or height>10000:raise InvalidOperation
        except InvalidOperation:raise ValueError('Height: enter a number from 0 to 10000 metres, using a comma or point.')
        result['height_m']=format(height.normalize(),'f')
        if result['height_reference'] not in REFERENCES:raise ValueError('Choose a height reference.')
        if result['height_reference']=='other' and not result['notes']:raise ValueError('Describe the other height reference in placement notes.')
    else:result['height_reference']=None
    if result['state']!='recorded' and any(result[k] is not None for k in (*PLACE_FIELDS,*PLACEMENT_FIELDS)):
        raise ValueError('Unknown or not applicable locations must have no structured details.')
    if result['state']=='recorded' and not any(result[k] is not None for k in (*PLACE_FIELDS,*PLACEMENT_FIELDS)):
        raise ValueError('Enter at least one location detail, or choose Unknown.')
    return result

def place_key(data):return json.dumps([data.get(k) for k in PLACE_FIELDS],ensure_ascii=False,separators=(',',':'))

def load_location(con,device):
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    row=cursor.execute('SELECT * FROM device_locations WHERE device_id=?',(device,)).fetchone()
    if row is None:return empty_location()
    result=empty_location();result.update({k:row[k] for k in ('state',*PLACEMENT_FIELDS)})
    if row['place_id']:
        place=cursor.execute('SELECT * FROM location_places WHERE place_id=?',(row['place_id'],)).fetchone()
        result.update({k:place[k] for k in PLACE_FIELDS})
    return result

def save_location(con,device,data):
    before=load_location(con,device)
    if before==data:return
    ident=None
    if any(data[k] is not None for k in PLACE_FIELDS):
        key=place_key(data)
        row=con.execute('SELECT place_id FROM location_places WHERE place_key=?',(key,)).fetchone()
        ident=row[0] if row else 'place-'+uuid.uuid4().hex
        if row is None:
            con.execute('INSERT INTO location_places(place_id,place_key,'+','.join(PLACE_FIELDS)+') VALUES('+','.join('?' for _ in range(len(PLACE_FIELDS)+2))+')',(ident,key,*(data[k] for k in PLACE_FIELDS)))
    con.execute('INSERT INTO device_locations(device_id,state,place_id,position,height_m,height_reference,notes) VALUES(?,?,?,?,?,?,?) ON CONFLICT(device_id) DO UPDATE SET state=excluded.state,place_id=excluded.place_id,position=excluded.position,height_m=excluded.height_m,height_reference=excluded.height_reference,notes=excluded.notes',(device,data['state'],ident,*(data[k] for k in PLACEMENT_FIELDS)))
    con.execute('INSERT INTO device_location_history(device_id,before_json,after_json,recorded_at) VALUES(?,?,?,?)',(device,json.dumps(before,ensure_ascii=False),json.dumps(data,ensure_ascii=False),dt.datetime.now(dt.timezone.utc).isoformat()))

def location_summary(data,translate=lambda x:x):
    if data['state']=='unknown':return translate('Unknown')
    if data['state']=='not_applicable':return translate('Not applicable / portable')
    values=[data[k] for k in PLACE_FIELDS if data.get(k)]
    if data.get('position'):values.append(data['position'])
    if data.get('height_m'):
        labels={'finished_floor':'Above finished floor','ground_level':'Above ground level','other':'Other height reference'}
        values.append(data['height_m']+' m · '+translate(labels[data['height_reference']]))
    if data.get('notes'):values.append(data['notes'])
    return ' › '.join(values)

def audit_locations(con):
    for row in con.execute('SELECT device_id FROM device_locations'):
        data=load_location(con,row[0])
        if validate_location(data)!=data:raise ValueError('Non-canonical location details.')
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    for row in cursor.execute('SELECT * FROM location_places'):
        if row['place_key']!=place_key(dict(row)):raise ValueError('Invalid reusable place key.')
