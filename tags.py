"""Optional reusable labels; catalogue and assignment changes commit with the device."""
import datetime,json,unicodedata,uuid
from names import name_key


def tag_label(value):
    if not isinstance(value,str) or any(unicodedata.category(c).startswith('C') or c in ('\u2028','\u2029') for c in value):
        raise ValueError('Tags need 1–50 printable characters on one line.')
    value=' '.join(unicodedata.normalize('NFC',value).split())
    if not 1<=len(value)<=50:raise ValueError('Tags need 1–50 printable characters on one line.')
    return value


def load_tags(con,device_id):
    return sorted((r[0] for r in con.execute('SELECT t.label FROM tag_choices t JOIN device_tags d USING(tag_id) WHERE d.device_id=?',(device_id,))),key=name_key)


def validate_tags(con,values):
    if not isinstance(values,(list,tuple)):raise ValueError('Choose tags or add a tag label.')
    known={r['normalized_key']:r['label'] for r in con.execute('SELECT * FROM tag_choices')}
    result={}
    for value in values:
        label=tag_label(value);key=name_key(label)
        result.setdefault(key,known.get(key,label))
    return sorted(result.values(),key=name_key)


def save_tags(con,device_id,values):
    before=load_tags(con,device_id)
    if before==values:return
    def snapshot():
        return [dict(r) for r in con.execute('SELECT t.tag_id,t.label FROM tag_choices t JOIN device_tags d USING(tag_id) WHERE d.device_id=? ORDER BY t.normalized_key',(device_id,))]
    old=snapshot();con.execute('DELETE FROM device_tags WHERE device_id=?',(device_id,))
    for label in values:
        key=name_key(label)
        row=con.execute('SELECT tag_id FROM tag_choices WHERE normalized_key=?',(key,)).fetchone()
        ident=row[0] if row else uuid.uuid4().hex
        if row is None:con.execute('INSERT INTO tag_choices VALUES(?,?,?)',(ident,label,key))
        con.execute('INSERT INTO device_tags VALUES(?,?)',(device_id,ident))
    con.execute('INSERT INTO device_tag_history(device_id,before_json,after_json,recorded_at) VALUES(?,?,?,?)',
        (device_id,json.dumps(old,ensure_ascii=False),json.dumps(snapshot(),ensure_ascii=False),datetime.datetime.now(datetime.timezone.utc).isoformat()))


def audit_tags(con):
    for label,key in con.execute('SELECT label,normalized_key FROM tag_choices'):
        if tag_label(label)!=label or name_key(label)!=key:
            raise ValueError('Invalid normalized tag label in database.')
