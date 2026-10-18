"""Validated device editing, with backups and optimistic conflict detection."""
import datetime as dt
from pathlib import Path
import re
import sqlite3
import unicodedata
import uuid
import string
import inventory
from connectivity import load_connectivity,validate_profile,save_profile
from software import load_software,validate_software,save_software
from network_identity import load_network,validate_network,save_network

FIELDS = ('device_id','name','source','purchase_date','purchase_price','purchase_currency','purchased_at',
          'installation_date','scrapped_date','current_state','physical_condition','device_type','location')
DATES = ('purchase_date','installation_date','scrapped_date')

def new_device_id():
    return 'hw-' + uuid.uuid4().hex

from names import name_key,validate_name
from source_store import load_links,validate_links,save_links,citation,SCOPES


class DeviceStore:
    def __init__(self, path):
        self.path = Path(path).resolve()
        with inventory.contextlib.closing(inventory.connect(self.path, readonly=True)) as con:
            inventory.check(con)

    def connect(self):
        con = inventory.connect(self.path)
        con.execute('PRAGMA busy_timeout=2000')
        return con

    def devices(self):
        with inventory.contextlib.closing(self.connect()) as con:
            rows=[dict(r) for r in con.execute('SELECT d.*, s.short_id, t.group_name AS type_group FROM devices d JOIN device_short_ids s ON s.device_id=d.device_id LEFT JOIN device_types t ON t.type_name=d.device_type ORDER BY d.name,d.device_id')]
            for row in rows:
                row['_connectivity']=load_connectivity(con,row['device_id'])
                row['_software']=load_software(con,row['device_id'])
                row['_network']=load_network(con,row['device_id'])
                row['_sources']=load_links(con,row['device_id'])
            return rows

    def name_issue(self,name,device_id=None):
        try:name=validate_name(name)
        except ValueError as exc:return str(exc)
        with inventory.contextlib.closing(inventory.connect(self.path,readonly=True,timeout=0.1)) as con:
            for row in con.execute('SELECT device_id,name FROM devices'):
                if row['device_id']!=device_id and name_key(row['name'])==name_key(name):
                    return 'That device name already exists. Add a distinguishing location or number.'
        return None

    def groups(self):
        with inventory.contextlib.closing(self.connect()) as c:
            return [r[0] for r in c.execute('SELECT group_name FROM device_type_groups ORDER BY group_name')]

    def types(self):
        with inventory.contextlib.closing(self.connect()) as c:
            return [dict(r) for r in c.execute('SELECT t.*,c.prefix FROM device_types t JOIN device_type_codes c USING(type_name) ORDER BY group_name,type_name')]

    def save_type(self, name, group, original=None, prefix=None):
        name=' '.join(name.strip().lower().split())
        group=' '.join(group.strip().lower().split())
        if not name or not group:
            raise ValueError('Both type name and group are required.')
        con=self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            if original is not None:
                current=con.execute('SELECT t.*,c.prefix FROM device_types t JOIN device_type_codes c USING(type_name) WHERE type_name=?',(original['type_name'],)).fetchone()
                if current is None or dict(current)!=original:
                    raise ValueError('Type changed outside this dialog; reopen it.')
            stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            output=self.path.parent/'backups'/f'before-type-change-{stamp}.sqlite3'
            with inventory.exclusive(output):pass
            with inventory.contextlib.closing(inventory.connect(self.path,readonly=True)) as src, inventory.contextlib.closing(sqlite3.connect(output)) as dest:
                src.backup(dest);inventory.check(dest)
            con.execute('INSERT OR IGNORE INTO device_type_groups(group_name) VALUES(?)',(group,))
            if original is None:
                used={r[0] for r in con.execute('SELECT prefix FROM device_type_codes')}|{'UN'}
                if prefix:
                    prefix=prefix.strip().upper()
                    if not re.fullmatch('[A-Z]{2}',prefix) or prefix in used:raise ValueError('Choose an unused two-letter uppercase type code.')
                else:
                    words=re.findall('[a-z]+',name);suggested=(''.join(w[0] for w in words)[:2] if len(words)>1 else ''.join(words)[:2]).upper()
                    prefix=next((v for v in [suggested]+[a+b for a in string.ascii_uppercase for b in string.ascii_uppercase] if len(v)==2 and v not in used),None)
                    if prefix is None:raise ValueError('No unused two-letter type code remains.')
                con.execute('INSERT INTO device_types(type_name,group_name) VALUES(?,?)',(name,group))
                con.execute('INSERT INTO device_type_codes(type_name,prefix) VALUES(?,?)',(name,prefix))
            else:
                con.execute('UPDATE device_types SET type_name=?,group_name=? WHERE type_name=?',(name,group,original['type_name']))
            con.commit()
            return output
        except Exception:
            con.rollback();raise
        finally:con.close()

    def os_families(self):
        with inventory.contextlib.closing(self.connect()) as c:
            return [r[0] for r in c.execute('SELECT value FROM os_families ORDER BY value')]

    def connection_options(self,kind):
        if kind not in ('interface','protocol'):raise ValueError('Unknown connectivity category')
        with inventory.contextlib.closing(self.connect()) as c:
            return [r[0] for r in c.execute('SELECT value FROM connection_options WHERE kind=? ORDER BY value',(kind,))]

    def save_connection_option(self,kind,name,original=None):
        if kind not in ('interface','protocol'):raise ValueError('Unknown connectivity category')
        name=' '.join(name.strip().lower().split())
        if not name:raise ValueError('A choice name is required.')
        con=self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            if original is not None and con.execute('SELECT 1 FROM connection_options WHERE kind=? AND value=?',(kind,original)).fetchone() is None:
                raise ValueError('Choice changed outside the dialog; reopen it.')
            stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            output=self.path.parent/'backups'/f'before-connection-list-change-{stamp}.sqlite3'
            with inventory.exclusive(output):pass
            with inventory.contextlib.closing(inventory.connect(self.path,readonly=True)) as src, inventory.contextlib.closing(sqlite3.connect(output)) as dest:
                src.backup(dest);inventory.check(dest)
            if original is None:con.execute('INSERT INTO connection_options(kind,value) VALUES(?,?)',(kind,name))
            else:con.execute('UPDATE connection_options SET value=? WHERE kind=? AND value=?',(name,kind,original))
            con.commit();return output
        except Exception:
            con.rollback();raise
        finally:con.close()

    def choices(self, table):
        if table not in ('device_states','physical_conditions'):
            raise ValueError('Unknown choice list')
        with inventory.contextlib.closing(self.connect()) as con:
            return [r[0] for r in con.execute('SELECT value FROM '+table+' ORDER BY value')]

    def validate(self, data):
        values = {k: data.get(k) for k in FIELDS}
        values['name']=validate_name(data.get('name'))
        for key in ('device_id','name','source'):
            if not isinstance(values[key], str) or not values[key].strip():
                raise ValueError(f'{key.replace("_"," ").capitalize()} is required.')
            values[key] = values[key].strip()
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',values['device_id']):
            raise ValueError('Device ID: use letters, digits, dots, underscores or hyphens; begin with a letter or digit.')
        for key in DATES:
            if values[key] is not None:
                try: inventory.date(values[key])
                except Exception: raise ValueError(f'{key.replace("_"," ").capitalize()}: choose a valid calendar date.')
        if values['purchased_at'] is not None:
            values['purchased_at']=' '.join(values['purchased_at'].split())
            if not 1<=len(values['purchased_at'])<=200:raise ValueError('Purchased at must contain 1–200 characters.')
        if values['location'] is not None:
            location=values['location']
            if not isinstance(location,str) or any(unicodedata.category(c)=='Cc' for c in location):raise ValueError('Location: use a single line of text, up to 200 characters.')
            location=' '.join(location.split()) or None
            if location and len(location)>200:raise ValueError('Location: use a single line of text, up to 200 characters.')
            values['location']=location
        price, currency = values['purchase_price'], values['purchase_currency']
        if (price is None) != (currency is None):
            raise ValueError('Enter both purchase price and currency, or leave both unknown.')
        if price is not None:
            if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',price):
                raise ValueError('Price: use a non-negative amount with a decimal point, for example 129.90.')
            if not re.fullmatch(r'[A-Z]{3}',currency):
                raise ValueError('Currency: use three uppercase letters, for example EUR or HUF.')
        if values['device_type'] is not None and values['device_type'] not in [r['type_name'] for r in self.types()]:
            raise ValueError('Choose a valid device type.')
        for key,table in (('current_state','device_states'),('physical_condition','physical_conditions')):
            if values[key] is not None and values[key] not in self.choices(table):
                raise ValueError(f'Choose a valid {key.replace("_"," ")}.')
        return values

    def save(self, data, original=None):
        candidate = dict(data)
        if original is None and not candidate.get('device_id'):
            candidate['device_id'] = new_device_id()
        # Validate IDs and build transparent legacy citations under the same write lock.
        values = None
        con = self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            selections=None
            if 'sources' in data:
                selections=validate_links(con,data['sources'])
                if original is not None and original.get('_sources')!=load_links(con,candidate['device_id']):raise ValueError('Source assignments changed outside the form. Cancel and refresh before editing again.')
                if not candidate.get('source') and selections['device']:candidate['source']=citation(con,selections['device'])
            values=self.validate(candidate);values['name']=' '.join(values['name'].split())
            current = con.execute('SELECT * FROM devices WHERE device_id=?',(values['device_id'],)).fetchone()
            if original is None:
                if current is not None: raise ValueError('That device ID already exists. Choose another ID.')
            else:
                if values['device_id'] != original['device_id']:
                    raise ValueError('Existing device IDs cannot be changed in this form.')
                if current is None or dict(current) != {k:v for k,v in original.items() if k not in ('type_group','short_id','_connectivity','_software','_network','_sources')}:
                    raise ValueError('This device changed outside the form. Cancel and refresh before editing again.')
            for row in con.execute('SELECT device_id,name FROM devices'):
                if row['device_id'] != values['device_id'] and name_key(row['name']) == name_key(values['name']):
                    raise ValueError('That device name already exists. Add a distinguishing location or number.')
            profile=None
            if 'connectivity' in data:
                profile_data={kind:dict(v) for kind,v in data['connectivity'].items()}
                if selections:
                    for kind in ('interface','protocol'):
                        if not profile_data[kind].get('source') and selections[kind]:profile_data[kind]['source']=citation(con,selections[kind])
                profile=validate_profile(con,profile_data)
                if original is not None and original.get('_connectivity') != load_connectivity(con,values['device_id']):
                    raise ValueError('Connectivity changed outside the form. Cancel and refresh before editing again.')
            software=None
            if 'software' in data:
                software_data=dict(data['software'])
                if selections and not software_data.get('source') and selections['software']:software_data['source']=citation(con,selections['software'])
                software=validate_software(con,software_data)
                if original is not None and original.get('_software') != load_software(con,values['device_id']):
                    raise ValueError('Software changed outside the form. Cancel and refresh before editing again.')
            network=None
            if 'network' in data:
                network_data=dict(data['network'])
                if selections and not network_data.get('source') and selections['network']:network_data['source']=citation(con,selections['network'])
                network=validate_network(network_data)
                if original is not None and original.get('_network')!=load_network(con,values['device_id']):
                    raise ValueError('Network details changed outside the form. Cancel and refresh before editing again.')
            # The reserved write lock prevents concurrent writes while a separate
            # read connection captures a consistent pre-save SQLite backup.
            stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            output=self.path.parent/'backups'/f'before-device-save-{stamp}.sqlite3'
            with inventory.exclusive(output): pass
            with inventory.contextlib.closing(inventory.connect(self.path, readonly=True)) as src, inventory.contextlib.closing(sqlite3.connect(output)) as dest:
                src.backup(dest)
                inventory.check(dest)
            if original is None:
                con.execute('INSERT INTO devices('+','.join(FIELDS)+') VALUES('+','.join('?' for _ in FIELDS)+')',tuple(values[k] for k in FIELDS))
            else:
                keys=FIELDS[1:]
                con.execute('UPDATE devices SET '+','.join(k+'=?' for k in keys)+' WHERE device_id=?',tuple(values[k] for k in keys)+(values['device_id'],))
            if profile is not None:save_profile(con,values['device_id'],profile)
            if software is not None:save_software(con,values['device_id'],software)
            if network is not None:save_network(con,values['device_id'],network)
            if selections is not None:save_links(con,values['device_id'],selections)
            con.commit()
            data['device_id'] = values['device_id']
            return output
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def delete(self, original):
        """Backed-up hard deletion; retain identity reservations and sourced snapshot."""
        import json
        from update_runtime import full_snapshot_locked
        device_id=original['device_id'];con=self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            current=con.execute('SELECT * FROM devices WHERE device_id=?',(device_id,)).fetchone()
            expected={k:v for k,v in original.items() if k not in ('type_group','short_id','_connectivity','_software','_network','_sources')}
            if current is None or dict(current)!=expected or load_network(con,device_id)!=original['_network'] or load_software(con,device_id)!=original['_software'] or load_connectivity(con,device_id)!=original['_connectivity'] or load_links(con,device_id)!=original['_sources']:
                raise ValueError('This device changed outside the form. Cancel and refresh before editing again.')
            if con.execute('SELECT 1 FROM network_links l JOIN network_interfaces i ON i.interface_id=l.endpoint_a OR i.interface_id=l.endpoint_b WHERE i.device_id=?',(device_id,)).fetchone():
                raise ValueError('Remove the connection records before deleting this device.')
            tables={
                'devices':('device_id=?',(device_id,)), 'facts':('device_id=?',(device_id,)),
                'relationships':('from_device=? OR to_device=?',(device_id,device_id)),
                'component_installations':('parent_device=? OR component_device=?',(device_id,device_id)),
                'device_photos':('device_id=?',(device_id,)), 'device_manuals':('device_id=?',(device_id,)),
                'device_connections':('device_id=?',(device_id,)), 'device_connectivity':('device_id=?',(device_id,)),
                'device_software':('device_id=?',(device_id,)),
                'network_addresses':('interface_id IN(SELECT interface_id FROM network_interfaces WHERE device_id=?)',(device_id,)),
                'network_interfaces':('device_id=?',(device_id,)), 'device_network':('device_id=?',(device_id,)),
                'network_observations':('device_id=?',(device_id,)),
                'source_links':('device_id=?',(device_id,)), 'source_link_history':('device_id=?',(device_id,))}
            snapshot={table:[dict(r) for r in con.execute('SELECT * FROM '+table+' WHERE '+where,args)] for table,(where,args) in tables.items()}
            output=self.path.parent/'backups'/('before-device-delete-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.zip')
            full_snapshot_locked(self.path,output)
            con.execute('INSERT INTO deleted_devices(device_id,snapshot_json) VALUES(?,?)',(device_id,json.dumps(snapshot,ensure_ascii=False)))
            for table,(where,args) in tables.items():
                if table!='devices':con.execute('DELETE FROM '+table+' WHERE '+where,args)
            con.execute('DELETE FROM devices WHERE device_id=?',(device_id,))
            inventory.check(con);con.commit();return output
        except Exception:con.rollback();raise
        finally:con.close()
