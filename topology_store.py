"""Sourced port-to-port connections; independent backed-up editing and retained history."""
import contextlib,datetime as dt,json,math,sqlite3,uuid
from pathlib import Path
import inventory
from source_store import citation

FIELDS=('endpoint_a','endpoint_b','medium','state','speed_mbps','source','observed_on','evidence_status','notes')

def load_link(con,ident):
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    row=cursor.execute('SELECT * FROM network_links WHERE link_id=?',(ident,)).fetchone()
    if row is None:return None
    data=dict(row);data['source_ids']=[r[0] for r in con.execute('SELECT source_id FROM network_link_sources WHERE link_id=? ORDER BY source_id',(ident,))];return data

def validate_link(con,data):
    result={k:data.get(k) for k in FIELDS}
    a,b=result['endpoint_a'],result['endpoint_b']
    if not isinstance(a,str) or not isinstance(b,str) or a==b:raise ValueError('Choose two different saved interfaces.')
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    endpoints=cursor.execute('SELECT interface_id,device_id FROM network_interfaces WHERE interface_id IN(?,?)',(a,b)).fetchall()
    if len(endpoints)!=2 or endpoints[0]['device_id']==endpoints[1]['device_id']:raise ValueError('Choose interfaces on two different saved devices.')
    result['endpoint_a'],result['endpoint_b']=sorted((a,b))
    if result['medium'] not in ('ethernet','fiber','wi-fi','powerline','other'):raise ValueError('Choose a connection medium.')
    if result['state'] not in ('planned','observed','retired'):raise ValueError('Choose a connection state.')
    if result['evidence_status'] not in ('uncertain','user_reported','verified'):raise ValueError('Choose a valid source verification status.')
    for k in ('source','observed_on','notes'):
        if result[k] is not None and not isinstance(result[k],str):raise ValueError('Connection notes and dates must be text.')
        result[k]=(result[k] or '').strip() or None
    if result['observed_on'] is not None:
        try:inventory.date(result['observed_on'])
        except Exception:raise ValueError('Choose a valid source observation or access date.')
    speed=result['speed_mbps']
    if speed is not None and speed!='':
        try:speed=float(speed)
        except (ValueError,TypeError):raise ValueError('Speed must be a positive number in Mbit/s, or blank.')
        if not math.isfinite(speed) or not 0<speed<=10000000:raise ValueError('Speed must be a positive number in Mbit/s, or blank.')
        result['speed_mbps']=speed
    else:result['speed_mbps']=None
    ids=data.get('source_ids',[])
    if not isinstance(ids,list) or any(not isinstance(x,str) for x in ids):raise ValueError('Choose existing evidence entries.')
    ids=sorted(set(ids))
    for ident in ids:
        if not con.execute('SELECT 1 FROM source_entries WHERE source_id=?',(ident,)).fetchone():raise ValueError('Choose existing evidence entries.')
    if not result['source'] and ids:result['source']=citation(con,ids)
    if result['evidence_status']=='verified' and (not result['source'] or not result['observed_on']):raise ValueError('Verified connections need evidence and an observation date.')
    result['source_ids']=ids;return result

def audit_links(con):
    for (ident,) in con.execute('SELECT link_id FROM network_links'):
        row=load_link(con,ident)
        if validate_link(con,row)!={k:row[k] for k in (*FIELDS,'source_ids')}:raise ValueError('Connection needs normalization.')

class TopologyStore:
    def __init__(self,path):self.path=Path(path)
    def connect(self):
        con=inventory.connect(self.path);con.execute('PRAGMA busy_timeout=2000');return con
    def endpoints(self):
        with contextlib.closing(self.connect()) as c:
            return [dict(r) for r in c.execute('SELECT i.*,d.name,s.short_id FROM network_interfaces i JOIN devices d USING(device_id) JOIN device_short_ids s USING(device_id) ORDER BY d.name,i.label')]
    def list(self):
        with contextlib.closing(self.connect()) as c:return [load_link(c,r[0]) for r in c.execute('SELECT link_id FROM network_links ORDER BY link_id')]
    def save(self,data,original=None):return self._write(data,original,False)
    def remove(self,original):return self._write(None,original,True)
    def _write(self,data,original,remove):
        con=self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            ident=original['link_id'] if original else uuid.uuid4().hex
            if original is not None and load_link(con,ident)!=original:raise ValueError('This connection changed. Close and reopen the connection list.')
            row=validate_link(con,data) if not remove else None
            if row:
                if con.execute('SELECT 1 FROM network_links WHERE endpoint_a=? AND endpoint_b=? AND link_id!=?',(row['endpoint_a'],row['endpoint_b'],ident)).fetchone():raise ValueError('This pair of interfaces already has a connection record.')
            stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=self.path.parent/'backups'/('before-connection-'+stamp+'.sqlite3')
            with inventory.exclusive(out):pass
            with contextlib.closing(inventory.connect(self.path,readonly=True)) as src,contextlib.closing(sqlite3.connect(out)) as dst:src.backup(dst);inventory.check(dst)
            snapshot=original if remove else dict(link_id=ident,**row)
            # Retain endpoint labels/owners even if devices are subsequently deleted.
            snapshot=dict(snapshot);snapshot['endpoints']=[dict(r) for r in con.execute('SELECT i.*,d.name FROM network_interfaces i JOIN devices d USING(device_id) WHERE interface_id IN(?,?)',(snapshot['endpoint_a'],snapshot['endpoint_b']))]
            con.execute('INSERT INTO network_link_history(link_id,action,snapshot_json) VALUES(?,?,?)',(ident,'remove' if remove else 'save',json.dumps(snapshot,ensure_ascii=False,sort_keys=True)))
            con.execute('DELETE FROM network_link_sources WHERE link_id=?',(ident,))
            if remove:con.execute('DELETE FROM network_links WHERE link_id=?',(ident,))
            else:
                con.execute('INSERT INTO network_links(link_id,'+','.join(FIELDS)+') VALUES('+','.join('?' for _ in range(len(FIELDS)+1))+') ON CONFLICT(link_id) DO UPDATE SET '+','.join(k+'=excluded.'+k for k in FIELDS),(ident,*(row[k] for k in FIELDS)))
                con.executemany('INSERT INTO network_link_sources(link_id,source_id) VALUES(?,?)',[(ident,x) for x in row['source_ids']])
            inventory.check(con);con.commit();return ident
        except Exception:con.rollback();raise
        finally:con.close()
