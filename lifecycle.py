"""Sourced, precision-preserving lifecycle observations and reviewed model snapshots."""
import calendar,contextlib,datetime as dt,json,re,sqlite3,unicodedata,uuid
from pathlib import Path
import inventory
from roles import validate_roles

KINDS={
 'market_release':'Market release date',
 'firmware_security_end':'Firmware security-support end',
 'os_security_end':'OS security-support end',
 'hardware_service_end':'Hardware service-support end',
 'production_end':'Production end',
 'warranty_expiry':'Warranty expiry',
}
BLOCK='Purchase date is earlier than the confirmed market release minus one calendar year.'
CONFLICT='Warning: conflicting market release observations; review the sources before relying on the purchase-date check.'
UNCERTAIN='Warning: market release evidence is unverified; purchase-date plausibility cannot be confirmed.'
BOUNDARY='Warning: purchase date falls within the uncertain release-date tolerance boundary.'
MISSING='Warning: no market release date is recorded; purchase-date plausibility cannot be checked.'


def clean(value,limit=200):
    if value is None:return ''
    if not isinstance(value,str) or len(value)>limit or any(unicodedata.category(c).startswith('C') for c in value):raise ValueError('Use printable single-line text within the field limit.')
    return value.strip()

def key(value):return ' '.join(unicodedata.normalize('NFC',clean(value)).casefold().split())

def bounds(value):
    """YYYY, YYYY-MM, YYYY-Qn or exact ISO date; never invent a stored day."""
    if not isinstance(value,str):raise ValueError('Use YYYY, YYYY-MM, YYYY-Q1 to YYYY-Q4, or YYYY-MM-DD.')
    try:
        if re.fullmatch(r'[0-9]{4}',value):
            y=int(value);return dt.date(y,1,1),dt.date(y,12,31)
        if re.fullmatch(r'[0-9]{4}-Q[1-4]',value):
            y=int(value[:4]);m=(int(value[-1])-1)*3+1;return dt.date(y,m,1),dt.date(y,m+2,calendar.monthrange(y,m+2)[1])
        if re.fullmatch(r'[0-9]{4}-[0-9]{2}',value):
            y,m=map(int,value.split('-'));return dt.date(y,m,1),dt.date(y,m,calendar.monthrange(y,m)[1])
        if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',value):
            d=dt.date.fromisoformat(value);return d,d
    except (ValueError,OverflowError):pass
    raise ValueError('Use YYYY, YYYY-MM, YYYY-Q1 to YYYY-Q4, or YYYY-MM-DD.')

def previous_year(value):
    if value.year==1:return dt.date.min
    return value.replace(year=value.year-1,day=min(value.day,calendar.monthrange(value.year-1,value.month)[1]))

def validate_records(con,records):
    if not isinstance(records,list) or len(records)>100:raise ValueError('Choose up to 100 lifecycle observations.')
    result=[]
    for entry in records:
        if not isinstance(entry,dict) or set(entry)-{'kind','date','provider','product','version','applicability','status','observed_on','sources','note'}:raise ValueError('Invalid lifecycle observation.')
        row={k:clean(entry.get(k),2000 if k=='note' else 200) for k in ('kind','date','provider','product','version','applicability','status','observed_on','note')}
        if row['kind'] not in KINDS:raise ValueError('Choose a valid lifecycle property.')
        bounds(row['date'])
        if row['status'] not in ('uncertain','user_reported','verified'):raise ValueError('Choose a valid lifecycle verification status.')
        if row['observed_on']:
            try:inventory.date(row['observed_on'])
            except Exception:raise ValueError('Choose a valid lifecycle observation date.')
        sources=entry.get('sources',[])
        if not isinstance(sources,list) or not all(isinstance(s,str) for s in sources) or len(sources)!=len(set(sources)):raise ValueError('Choose each lifecycle source only once.')
        for ident in sources:
            if not con.execute('SELECT 1 FROM source_entries WHERE source_id=?',(ident,)).fetchone():raise ValueError('A lifecycle source no longer exists; refresh before saving.')
        row['sources']=sorted(sources)
        if row['status']=='verified':
            if not row['observed_on'] or not sources or not all(con.execute("SELECT 1 FROM source_entries WHERE source_id=? AND evidence_status='verified' AND observed_on IS NOT NULL",(ident,)).fetchone() for ident in sources):raise ValueError('Verified lifecycle dates need an observation date and verified dated sources.')
        if row['kind'] in ('market_release','production_end') and not (row['provider'] and row['product']):raise ValueError('Model lifecycle dates need manufacturer and exact model in provider and product.')
        if row['kind'] in ('firmware_security_end','os_security_end') and not (row['provider'] and row['product'] and row['version']):raise ValueError('Software support dates need provider, product and version or support track.')
        if row['kind']=='hardware_service_end' and not row['applicability']:raise ValueError('Describe the hardware service scope and applicable region.')
        if row['kind']=='warranty_expiry' and not row['applicability']:raise ValueError('Describe the individual device warranty or contract.')
        result.append(row)
    return result

def purchase_check(purchase,records,manufacturer=None,model=None):
    if not purchase:return None,[]
    day=dt.date.fromisoformat(purchase);releases=[r for r in records if r['kind']=='market_release']
    if not releases:return None,[MISSING]
    if manufacturer is not None and any(key(r['provider'])!=key(manufacturer) or key(r['product'])!=key(model) for r in releases):return None,['Warning: release-date applicability does not match the device manufacturer and model.']
    intervals={bounds(r['date']) for r in releases}
    if len(intervals)>1:return None,[CONFLICT]
    if any(r['status']!='verified' for r in releases):return None,[UNCERTAIN]
    lo,hi=next(iter(intervals));lo,hi=previous_year(lo),previous_year(hi)
    if day<lo:return BLOCK,[]
    return None,[BOUNDARY] if day<hi else []

def warnings(purchase,records,manufacturer=None,model=None):
    issue,notes=purchase_check(purchase,records,manufacturer,model)
    if issue:notes=[issue]+notes
    if any(not r['sources'] for r in records):notes.append('Warning: lifecycle sources are missing. Unverified observations can still be saved.')
    return notes

def load_lifecycle(con,device):
    row=con.execute('SELECT records_json FROM device_lifecycle WHERE device_id=?',(device,)).fetchone()
    return json.loads(row[0]) if row else []

def save_lifecycle(con,device,records):
    if records==load_lifecycle(con,device):return
    raw=json.dumps(records,sort_keys=True,ensure_ascii=False)
    con.execute('INSERT INTO device_lifecycle_history(device_id,records_json) VALUES(?,?)',(device,raw))
    con.execute('INSERT INTO device_lifecycle VALUES(?,?) ON CONFLICT(device_id) DO UPDATE SET records_json=excluded.records_json',(device,raw))

def profiles(con,manufacturer=None,model=None):
    rows=[dict(r) for r in con.execute('SELECT p.*, t.group_name FROM model_profiles p LEFT JOIN device_types t ON t.type_name=p.device_type WHERE NOT EXISTS(SELECT 1 FROM model_profiles n WHERE n.supersedes=p.profile_id) ORDER BY manufacturer,model,variant,recorded_at')]
    if manufacturer is not None:rows=[r for r in rows if key(r['manufacturer'])==key(manufacturer) and key(r['model'])==key(model)]
    for r in rows:
        for k in ('roles','lifecycle','sources'):r[k]=json.loads(r[k+'_json'])
    return rows

class ModelStore:
    def __init__(self,path):self.path=Path(path).resolve()
    def list(self,manufacturer=None,model=None):
        with contextlib.closing(inventory.connect(self.path,readonly=True)) as c:return profiles(c,manufacturer,model)
    def save(self,data,original=None):
        con=inventory.connect(self.path)
        try:
            con.execute('BEGIN IMMEDIATE')
            manufacturer=clean(data.get('manufacturer'));model=clean(data.get('model'));variant=clean(data.get('variant'))
            note=clean(data.get('note'),2000);kind=data.get('device_type');roles=validate_roles(con,data.get('roles',[]));records=validate_records(con,data.get('lifecycle',[]));sources=data.get('sources',[])
            if not manufacturer or not model or not variant:raise ValueError('Enter manufacturer, model and explicit variant or applicability for the model profile.')
            if not note:raise ValueError('Describe the model profile evidence and applicability.')
            if kind is not None and not con.execute('SELECT 1 FROM device_types WHERE type_name=?',(kind,)).fetchone():raise ValueError('Choose a valid device type.')
            if not isinstance(sources,list) or not sources or any(not isinstance(s,str) or not con.execute('SELECT 1 FROM source_entries WHERE source_id=?',(s,)).fetchone() for s in sources):raise ValueError('Choose at least one source for the model profile.')
            if any(r['kind']=='warranty_expiry' for r in records):raise ValueError('Individual warranty dates cannot be shared through model profiles.')
            active=profiles(con,manufacturer,model);same=[r for r in active if key(r['variant'])==key(variant)]
            if original:
                current=next((r for r in active if r['profile_id']==original['profile_id']),None)
                if current!=original:raise ValueError('Model profile changed; reopen the catalogue.')
                if (key(manufacturer),key(model),key(variant))!=(key(original['manufacturer']),key(original['model']),key(original['variant'])):raise ValueError('A model revision must keep the same manufacturer, model and variant.')
            elif same:raise ValueError('That model variant already exists; select it to create a revision.')
            from update_runtime import full_snapshot_locked
            output=self.path.parent/'backups'/('before-model-profile-'+uuid.uuid4().hex+'.zip');full_snapshot_locked(self.path,output)
            ident=uuid.uuid4().hex
            con.execute('INSERT INTO model_profiles(profile_id,manufacturer,model,variant,device_type,roles_json,lifecycle_json,sources_json,note,supersedes) VALUES(?,?,?,?,?,?,?,?,?,?)',(ident,manufacturer,model,variant,kind,json.dumps(roles),json.dumps(records),json.dumps(sorted(set(sources))),note,original['profile_id'] if original else None));con.commit();return ident
        except Exception:con.rollback();raise
        finally:con.close()

def audit_lifecycle(con):
    for row in con.execute('SELECT records_json FROM device_lifecycle'):validate_records(con,json.loads(row[0]))
    for row in con.execute('SELECT records_json FROM device_lifecycle_history'):validate_records(con,json.loads(row[0]))
    for row in con.execute('SELECT lifecycle_json,sources_json,roles_json FROM model_profiles'):
        validate_records(con,json.loads(row[0]))
        sources=json.loads(row[1]);roles=json.loads(row[2])
        if not isinstance(sources,list) or not sources or any(not isinstance(s,str) or not con.execute('SELECT 1 FROM source_entries WHERE source_id=?',(s,)).fetchone() for s in sources):raise ValueError('Choose at least one source for the model profile.')
        validate_roles(con,roles)
