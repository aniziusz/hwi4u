"""Optional current hostname and per-interface MAC/IP identities, with observations."""
import ipaddress
import json
import re
import sqlite3
import uuid
import inventory


def empty_network():
    return dict(hostname=None,interfaces=[],source=None,observed_on=None,evidence_status='user_reported')

def hostname(value):
    value=(value or '').strip()
    if value.endswith('.'):value=value[:-1]
    if not value:return None
    try:value=value.encode('idna').decode('ascii').lower()
    except UnicodeError:raise ValueError('Hostname: use valid DNS labels with letters, digits and hyphens.')
    if len(value)>253 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',part) for part in value.split('.')):
        raise ValueError('Hostname: use valid DNS labels with letters, digits and hyphens.')
    try:ipaddress.ip_address(value)
    except ValueError:return value
    raise ValueError('Enter IP addresses in an interface row, not in Hostname.')

def mac_address(value):
    if value is not None and not isinstance(value,str):raise ValueError('MAC address must be text or unknown.')
    value=(value or '').strip().lower()
    if not value:return None
    patterns=(r'[0-9a-f]{12}',r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',r'(?:[0-9a-f]{2}-){5}[0-9a-f]{2}',r'(?:[0-9a-f]{4}\.){2}[0-9a-f]{4}')
    if not any(re.fullmatch(pattern,value) for pattern in patterns):raise ValueError('MAC address: enter six hexadecimal octets, for example 02:00:00:00:00:01, or leave unknown blank.')
    plain=re.sub('[:.-]','',value)
    if plain in ('0'*12,'f'*12):raise ValueError('MAC address cannot be all zeros or the broadcast address.')
    return ':'.join(plain[n:n+2] for n in range(0,12,2))

def ip_address(value):
    if not isinstance(value,str) or '%' in value:raise ValueError('Enter a valid IPv4/IPv6 address, optionally with /prefix; the interface row identifies its scope.')
    try:return str(ipaddress.ip_interface(value.strip())) if '/' in value else str(ipaddress.ip_address(value.strip()))
    except ValueError:raise ValueError('Enter a valid IPv4/IPv6 address, optionally with /prefix; the interface row identifies its scope.')

def load_network(con,device):
    result=empty_network();cursor=con.cursor();cursor.row_factory=sqlite3.Row
    row=cursor.execute('SELECT * FROM device_network WHERE device_id=?',(device,)).fetchone()
    if row:
        for key in ('hostname','source','observed_on','evidence_status'):result[key]=row[key]
    for row in cursor.execute('SELECT * FROM network_interfaces WHERE device_id=? ORDER BY label,interface_id',(device,)):
        addresses=[r[0] for r in con.execute('SELECT address FROM network_addresses WHERE interface_id=? ORDER BY address',(row['interface_id'],))]
        result['interfaces'].append(dict(interface_id=row['interface_id'],label=row['label'],mac_address=row['mac_address'],addresses=addresses))
    return result

def validate_network(data):
    if not isinstance(data,dict):raise ValueError('Network identity must be a record.')
    result=empty_network();result.update({k:data[k] for k in result if k in data})
    for key in ('hostname','source','observed_on'):
        if result[key] is not None and not isinstance(result[key],str):raise ValueError('Network identity values must be text or unknown.')
        result[key]=result[key].strip() or None if result[key] is not None else None
    result['hostname']=hostname(result['hostname'])
    if result['evidence_status'] not in ('user_reported','verified','uncertain'):raise ValueError('Choose a valid network evidence status.')
    if result['observed_on'] is not None:
        try:inventory.date(result['observed_on'])
        except Exception:raise ValueError('Network observation date must be a valid calendar date.')
    if result['evidence_status']=='verified' and (not result['source'] or not result['observed_on']):raise ValueError('Verified network details need an evidence source and observation date.')
    if not isinstance(result['interfaces'],list):raise ValueError('Network interfaces must be a list.')
    normalized=[];labels=set();identifiers=set()
    for item in result['interfaces']:
        if not isinstance(item,dict):raise ValueError('Network interface must be a record.')
        label=item.get('label');label=' '.join(label.split()) if isinstance(label,str) else ''
        if not label or len(label)>100:raise ValueError('Each interface needs a label of 1–100 characters, for example igc0 or WAN.')
        if label.casefold() in labels:raise ValueError('Interface labels must be unique within this device.')
        labels.add(label.casefold())
        ident=item.get('interface_id') or uuid.uuid4().hex
        if not isinstance(ident,str) or not re.fullmatch('[0-9a-f]{32}',ident) or ident in identifiers:raise ValueError('Invalid or repeated network interface identity.')
        identifiers.add(ident)
        addresses=item.get('addresses',[])
        if not isinstance(addresses,list):raise ValueError('Interface IP addresses must be a list.')
        canonical=sorted(ip_address(v) for v in addresses)
        hosts=[str(ipaddress.ip_interface(v).ip) if '/' in v else v for v in canonical]
        if len(hosts)!=len(set(hosts)):raise ValueError('Do not repeat an IP address within the same interface.')
        normalized.append(dict(interface_id=ident,label=label,mac_address=mac_address(item.get('mac_address')),addresses=canonical))
    result['interfaces']=sorted(normalized,key=lambda r:(r['label'],r['interface_id']))
    return result

def missing_source(data):return bool((data['hostname'] or data['interfaces']) and not data['source'])

def save_network(con,device,data):
    if load_network(con,device)==data:return
    # Append the new observation before replacing the current assessment; previous observations remain.
    con.execute('INSERT INTO network_observations(device_id,profile_json) VALUES(?,?)',(device,json.dumps(data,ensure_ascii=False,sort_keys=True)))
    con.execute('DELETE FROM network_addresses WHERE interface_id IN(SELECT interface_id FROM network_interfaces WHERE device_id=?)',(device,))
    retained={row['interface_id'] for row in data['interfaces']}
    for (ident,) in list(con.execute('SELECT interface_id FROM network_interfaces WHERE device_id=?',(device,))):
        if ident not in retained:
            if con.execute("SELECT 1 FROM sqlite_master WHERE name='network_links'").fetchone() and con.execute('SELECT 1 FROM network_links WHERE endpoint_a=? OR endpoint_b=?',(ident,ident)).fetchone():
                raise ValueError('Remove the connection records before removing this interface.')
            con.execute('DELETE FROM network_interfaces WHERE interface_id=?',(ident,))
    # Temporary unique labels avoid collisions when two retained ports swap names.
    for ident in retained:
        owner=con.execute('SELECT device_id FROM network_interfaces WHERE interface_id=?',(ident,)).fetchone()
        if owner and owner[0]!=device:raise ValueError('Interface identity belongs to another device.')
        con.execute('UPDATE network_interfaces SET label=? WHERE interface_id=?',('temporary-'+uuid.uuid4().hex,ident))
    con.execute('INSERT INTO device_network(device_id,hostname,source,observed_on,evidence_status) VALUES(?,?,?,?,?) ON CONFLICT(device_id) DO UPDATE SET hostname=excluded.hostname,source=excluded.source,observed_on=excluded.observed_on,evidence_status=excluded.evidence_status',
                (device,data['hostname'],data['source'],data['observed_on'],data['evidence_status']))
    for row in data['interfaces']:
        con.execute('INSERT INTO network_interfaces(interface_id,device_id,label,mac_address) VALUES(?,?,?,?) ON CONFLICT(interface_id) DO UPDATE SET label=excluded.label,mac_address=excluded.mac_address',(row['interface_id'],device,row['label'],row['mac_address']))
        con.executemany('INSERT INTO network_addresses(interface_id,address) VALUES(?,?)',[(row['interface_id'],address) for address in row['addresses']])

def audit_network(con):
    for (device,) in con.execute('SELECT device_id FROM device_network'):
        data=load_network(con,device)
        if validate_network(data)!=data:raise ValueError('Network identity needs normalization for '+device)
