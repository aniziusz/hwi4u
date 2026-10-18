"""Optional user-reported functional roles; primary classification is independent."""
import json,datetime,unicodedata

def role_name(value):
    if not isinstance(value,str):raise ValueError('Enter a role name.')
    value=' '.join(value.split()).casefold()
    if not 1<=len(value)<=60 or any(unicodedata.category(c).startswith('C') for c in value):raise ValueError('Role names need 1–60 printable characters.')
    return value

def load_roles(con,device_id):
    return [r[0] for r in con.execute('SELECT role FROM device_roles WHERE device_id=? ORDER BY role',(device_id,))]

def validate_roles(con,values):
    if not isinstance(values,(list,tuple)) or any(not isinstance(v,str) for v in values):raise ValueError('Choose roles from the catalogue.')
    values=sorted(set(values));known={r[0] for r in con.execute('SELECT value FROM role_choices')}
    if not set(values)<=known:raise ValueError('Unknown role; refresh the role choices.')
    return values

def save_roles(con,device_id,values):
    before=load_roles(con,device_id)
    if before==values:return
    con.execute('DELETE FROM device_roles WHERE device_id=?',(device_id,))
    con.executemany('INSERT INTO device_roles VALUES(?,?)',[(device_id,v) for v in values])
    con.execute('INSERT INTO device_role_history(device_id,before_json,after_json,recorded_at) VALUES(?,?,?,?)',(device_id,json.dumps(before,ensure_ascii=False),json.dumps(values,ensure_ascii=False),datetime.datetime.now(datetime.timezone.utc).isoformat()))
