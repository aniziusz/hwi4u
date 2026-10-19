#!/usr/bin/env python3
"""Local hardware inventory. Standard-library-only; no network access."""
import argparse
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

BASE = Path(__file__).resolve().parent
STATES = ('awaiting installation', 'in use', 'spare', 'in storage', 'under assessment', 'under repair', 'retired', 'sold', 'given away', 'returned', 'lost', 'stolen', 'scrapped')
CONDITIONS = ('working', 'partially working', 'faulty', 'untested')

TABLES = ('device_type_groups', 'device_types', 'device_states', 'physical_conditions', 'devices', 'facts', 'relationships', 'component_installations', 'device_photos', 'connection_options', 'device_connectivity', 'device_connections', 'os_families', 'device_software', 'device_manuals', 'device_type_codes', 'device_short_labels', 'device_network', 'network_interfaces', 'network_addresses', 'network_observations','deleted_devices','source_entries','source_links','source_link_history','network_links','network_link_sources','network_link_history','location_places','device_locations','device_location_history','role_choices','device_roles','device_role_history')

def nonempty(value):
    if not value.strip():
        raise argparse.ArgumentTypeError('Value must not be blank')
    return value

def date(value):
    try:
        parsed = dt.date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError()
    except ValueError:
        raise argparse.ArgumentTypeError('Use YYYY-MM-DD')
    return value

def connect(path, readonly=False, timeout=5.0):
    con = sqlite3.connect(path.resolve().as_uri() + ('?mode=ro' if readonly else '?mode=rw'), uri=True, timeout=timeout)
    try:
        con.execute('PRAGMA foreign_keys = ON')
        con.row_factory = sqlite3.Row
        if con.execute('PRAGMA user_version').fetchone()[0] != 24:raise ValueError('Unsupported schema version')
        return con
    except Exception:
        con.close();raise

def check(con):
    integrity = [r[0] for r in con.execute('PRAGMA integrity_check')]
    foreign = [list(r) for r in con.execute('PRAGMA foreign_key_check')]
    if integrity != ['ok'] or foreign:
        raise ValueError(f'Integrity failure: {integrity}; foreign keys: {foreign}')
    if con.execute('PRAGMA user_version').fetchone()[0] >= 12:
        from connectivity import audit
        audit(con)
    if con.execute('PRAGMA user_version').fetchone()[0] >= 13:
        from software import audit_software
        audit_software(con)
    if con.execute('PRAGMA user_version').fetchone()[0] >= 14:
        from manual_store import audit_manuals
        audit_manuals(con)
    if con.execute('PRAGMA user_version').fetchone()[0] >= 16:
        if con.execute('SELECT 1 FROM device_types t LEFT JOIN device_type_codes c USING(type_name) WHERE c.prefix IS NULL LIMIT 1').fetchone():raise ValueError('A device type is missing its two-letter code.')
        if con.execute('SELECT 1 FROM devices d LEFT JOIN device_short_ids n ON n.device_id=d.device_id WHERE n.short_id IS NULL LIMIT 1').fetchone():
            raise ValueError('A device is missing its short ID.')
    if con.execute('PRAGMA user_version').fetchone()[0]>=17:
        from network_identity import audit_network
        audit_network(con)
        from names import validate_name,name_key
        seen=set()
        for row in con.execute('SELECT name FROM devices'):
            key=name_key(validate_name(row[0]))
            if key in seen:raise ValueError('Duplicate normalized device name in database.')
            seen.add(key)
    if con.execute('PRAGMA user_version').fetchone()[0]>=18:
        if con.execute('SELECT 1 FROM device_short_labels l WHERE NOT EXISTS(SELECT 1 FROM devices d WHERE d.device_id=l.device_id) AND NOT EXISTS(SELECT 1 FROM deleted_devices x WHERE x.device_id=l.device_id) LIMIT 1').fetchone():raise ValueError('Reserved short label has no current or deleted device.')
    if con.execute('PRAGMA user_version').fetchone()[0]>=19:
        from source_store import audit_sources
        audit_sources(con)
    if con.execute('PRAGMA user_version').fetchone()[0]>=20:
        from topology_store import audit_links
        audit_links(con)
    if con.execute('PRAGMA user_version').fetchone()[0]>=22:
        from location_store import audit_locations
        audit_locations(con)
    if con.execute('PRAGMA user_version').fetchone()[0]>=23:
        from roles import role_name
        for (value,) in con.execute('SELECT value FROM role_choices'):
            if role_name(value)!=value:raise ValueError('Noncanonical role choice in database.')
    return {'integrity': 'ok', 'foreign_keys': 'ok', 'schema_version': con.execute('PRAGMA user_version').fetchone()[0]}

def exclusive(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    return os.fdopen(fd, 'w', encoding='utf-8')

def main(argv=None):
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=BASE/'hardware.sqlite3')
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init')
    sub.add_parser('check')
    sub.add_parser('list')
    a = sub.add_parser('add-device')
    a.add_argument('--id', type=nonempty, help='Advanced import override; omit for an automatic ID')
    a.add_argument('--name', required=True, type=nonempty)
    a.add_argument('--source', required=True, type=nonempty)
    a = sub.add_parser('set-device-type')
    a.add_argument('--device', required=True, type=nonempty)
    a.add_argument('--type', type=nonempty, help='Omit to clear the type to unknown')
    a = sub.add_parser('set-lifecycle')
    a.add_argument('--device', required=True, type=nonempty)
    a.add_argument('--installation-date', type=date)
    a.add_argument('--state', choices=STATES)
    a.add_argument('--condition', choices=CONDITIONS)
    a.add_argument('--scrapped-date', type=date)
    a = sub.add_parser('set-purchase')
    a.add_argument('--device', required=True, type=nonempty)
    a.add_argument('--date', type=date)
    a.add_argument('--price')
    a.add_argument('--currency')
    a = sub.add_parser('add-fact')
    for flag in ('device', 'field', 'value', 'source'):
        a.add_argument('--'+flag, required=True, type=nonempty)
    a.add_argument('--unit')
    a.add_argument('--status', choices=('user_reported','verified','uncertain'), default='user_reported')
    a.add_argument('--verified-on', type=date)
    a = sub.add_parser('link')
    for flag in ('from-device','to-device','relation','source'):
        a.add_argument('--'+flag, required=True, type=nonempty)
    a = sub.add_parser('install-component')
    a.add_argument('--parent', required=True, type=nonempty)
    a.add_argument('--component', required=True, type=nonempty)
    a.add_argument('--position', type=nonempty)
    a.add_argument('--installed-on', type=date)
    a.add_argument('--source', required=True, type=nonempty)
    a = sub.add_parser('remove-component')
    a.add_argument('--installation', required=True, type=int)
    a.add_argument('--removed-on', required=True, type=date)
    a.add_argument('--source', required=True, type=nonempty)
    a = sub.add_parser('assembly')
    a.add_argument('device')
    a.add_argument('--history', action='store_true')
    a = sub.add_parser('show')
    a.add_argument('device')
    a = sub.add_parser('backup-bundle')
    a.add_argument('--output', type=Path, required=True)
    a = sub.add_parser('backup')
    a.add_argument('--output', type=Path, required=True)
    a = sub.add_parser('export')
    a.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args(argv)
    db = args.db.resolve()
    if args.cmd == 'backup-bundle':
        from photo_files import backup_bundle
        print(f'Verified portable backup: {backup_bundle(db, args.output)}')
        return
    if args.cmd == 'init':
        with exclusive(db):
            pass
        try:
            with contextlib.closing(sqlite3.connect(db)) as con:
                con.executescript((BASE/'schema.sql').read_text())
                check(con)
        except Exception:
            db.unlink(missing_ok=True)
            raise
        print(f'Created empty database: {db}')
        return
    if args.cmd == 'add-fact' and args.status == 'verified' and not args.verified_on:
        parser.error('--verified-on is required for verified facts')
    if args.cmd == 'set-purchase':
        if not any((args.date, args.price is not None, args.currency)):
            parser.error('Supply --date and/or --price with --currency')
        if (args.price is not None) != (args.currency is not None):
            parser.error('--price and --currency must be supplied together')
        if args.price is not None:
            if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', args.price):
                parser.error('Use a non-negative price with a decimal point, e.g. 129.90')
            if not re.fullmatch(r'[A-Z]{3}', args.currency):
                parser.error('Use a three-letter uppercase currency code, e.g. EUR')
    if args.cmd == 'set-lifecycle' and args.installation_date is None and args.state is None and args.scrapped_date is None and args.condition is None:
        parser.error('Supply --installation-date, --scrapped-date, --state and/or --condition')
    if args.cmd == 'add-device':
        from device_store import DeviceStore
        data={'device_id':args.id,'name':args.name,'source':args.source}
        DeviceStore(db).save(data)
        print(f'Added {data["device_id"]}')
        return
    mutating = args.cmd in ('add-device','add-fact','link','set-purchase','set-lifecycle','install-component','remove-component','set-device-type')
    with contextlib.closing(connect(db, readonly=not mutating)) as con:
        for key in ('device','from_device','to_device','parent','component'):
            value=getattr(args,key,None)
            if value:
                exact=con.execute('SELECT device_id FROM devices WHERE device_id=?',(value,)).fetchone()
                short=con.execute('SELECT device_id FROM device_label_aliases WHERE short_id=?',(value,)).fetchone()
                if exact and short and exact[0]!=short[0]:raise ValueError('Ambiguous short ID; use the full device ID.')
                if short and not exact:setattr(args,key,short[0])
        if args.cmd == 'set-device-type':
            with con:
                result=con.execute('UPDATE devices SET device_type=? WHERE device_id=?',(args.type,args.device))
                if result.rowcount != 1: raise ValueError('no data available: unknown device ID')
            print('Updated device type')
        elif args.cmd == 'set-lifecycle':
            updates, values = [], []
            for column, value in (('installation_date', args.installation_date), ('current_state', args.state), ('scrapped_date', args.scrapped_date), ('physical_condition', args.condition)):
                if value is not None:
                    updates.append(column + '=?')
                    values.append(value)
            with con:
                result = con.execute('UPDATE devices SET ' + ','.join(updates) + ' WHERE device_id=?', (*values, args.device))
                if result.rowcount != 1:
                    raise ValueError('no data available: unknown device ID')
            print('Updated lifecycle details')
        elif args.cmd == 'set-purchase':
            updates, values = [], []
            for column, value in (('purchase_date', args.date), ('purchase_price', args.price), ('purchase_currency', args.currency)):
                if value is not None:
                    updates.append(column + '=?')
                    values.append(value)
            with con:
                result = con.execute('UPDATE devices SET ' + ','.join(updates) + ' WHERE device_id=?', (*values, args.device))
                if result.rowcount != 1:
                    raise ValueError('no data available: unknown device ID')
            print('Updated purchase details')
        elif args.cmd == 'add-fact':
            with con:
                con.execute('INSERT INTO facts(device_id,field,value,unit,source,evidence_status,verified_on) VALUES(?,?,?,?,?,?,?)', (args.device,args.field,args.value,args.unit,args.source,args.status,args.verified_on))
            print('Added fact (prior observations retained)')
        elif args.cmd == 'link':
            with con:
                con.execute('INSERT INTO relationships(from_device,to_device,relation,source) VALUES(?,?,?,?)', (args.from_device,args.to_device,args.relation,args.source))
            print('Added relationship')
        elif args.cmd == 'install-component':
            with con:
                row = con.execute('INSERT INTO component_installations(parent_device,component_device,position,installed_on,source) VALUES(?,?,?,?,?)', (args.parent,args.component,args.position,args.installed_on,args.source))
            print(f'Added installation {row.lastrowid}')
        elif args.cmd == 'remove-component':
            with con:
                row = con.execute('UPDATE component_installations SET removed_on=?,removal_source=? WHERE installation_id=? AND removed_on IS NULL', (args.removed_on,args.source,args.installation))
                if row.rowcount != 1:
                    raise ValueError('Unknown installation or already removed')
            print('Recorded removal; installation history retained')
        elif args.cmd == 'assembly':
            if con.execute('SELECT 1 FROM devices WHERE device_id=?',(args.device,)).fetchone() is None:
                raise ValueError('no data available: unknown device ID')
            suffix = '' if args.history else ' AND removed_on IS NULL'
            result = { 'device':args.device }
            for key, column in (('components','parent_device'),('installed_in','component_device')):
                result[key]=[dict(r) for r in con.execute('SELECT * FROM component_installations WHERE '+column+'=?'+suffix+' ORDER BY installation_id',(args.device,))]
            print(json.dumps(result,ensure_ascii=False,indent=2))
        elif args.cmd == 'list':
            print(json.dumps([dict(r) for r in con.execute('SELECT d.*,s.short_id FROM devices d JOIN device_short_ids s USING(device_id) ORDER BY s.short_id')],ensure_ascii=False,indent=2))
        elif args.cmd == 'show':
            row = con.execute('SELECT d.*,s.short_id FROM devices d JOIN device_short_ids s USING(device_id) WHERE d.device_id=?',(args.device,)).fetchone()
            if row is None:
                raise ValueError('no data available: unknown device ID')
            result = dict(row)
            from connectivity import load_connectivity
            result['connectivity']=load_connectivity(con,args.device)
            from software import load_software
            result['software']=load_software(con,args.device)
            from network_identity import load_network
            result['network']=load_network(con,args.device)
            from source_store import load_links
            result['source_links']=load_links(con,args.device)
            result['network_history']=[dict(r) for r in con.execute('SELECT * FROM network_observations WHERE device_id=? ORDER BY observation_id',(args.device,))]
            result['manuals']=[dict(r) for r in con.execute('SELECT * FROM device_manuals WHERE device_id=? ORDER BY title,reference_id',(args.device,))]
            result['photos'] = [dict(r) for r in con.execute('SELECT * FROM device_photos WHERE device_id=? ORDER BY recorded_at,photo_id',(args.device,))]
            result['facts'] = [dict(r) for r in con.execute('SELECT * FROM facts WHERE device_id=? ORDER BY fact_id',(args.device,))]
            result['component_installations'] = [dict(r) for r in con.execute('SELECT * FROM component_installations WHERE parent_device=? OR component_device=? ORDER BY installation_id',(args.device,args.device))]
            result['relationships'] = [dict(r) for r in con.execute('SELECT * FROM relationships WHERE from_device=? OR to_device=? ORDER BY relationship_id',(args.device,args.device))]
            print(json.dumps(result,ensure_ascii=False,indent=2))
        elif args.cmd == 'check':
            result=check(con)
            result['warnings']=[dict(r) for r in con.execute("SELECT device_id,kind,'missing connectivity source' AS warning FROM device_connectivity WHERE (supported_status!='unknown' OR usage_status!='unknown') AND source IS NULL")]
            result['counts']={t: con.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in TABLES}
            print(json.dumps(result,indent=2))
        elif args.cmd == 'backup':
            output = args.output.resolve()
            with exclusive(output):
                pass
            try:
                with contextlib.closing(sqlite3.connect(output)) as dest:
                    con.backup(dest)
                    check(dest)
            except Exception:
                output.unlink(missing_ok=True)
                raise
            print(f'Database-only backup verified: {output}. Use backup-bundle to include photo and manual files.')
        elif args.cmd == 'export':
            directory=args.directory.resolve()
            directory.mkdir(parents=True,exist_ok=False)
            # Capture JSON and SQL from the same read transaction.
            con.execute('BEGIN')
            snapshot={t:[dict(r) for r in con.execute(f'SELECT * FROM {t} ORDER BY 1')] for t in TABLES}
            (directory/'inventory.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
            (directory/'inventory.sql').write_text('PRAGMA foreign_keys=OFF;\n'+'\n'.join(con.iterdump())+'\nPRAGMA user_version = 24;\nPRAGMA foreign_keys=ON;\n')
            con.rollback()
            print(f'Exported JSON and SQL: {directory}. Photo/manual metadata only; use backup-bundle to include local files.')

if __name__ == '__main__':
    try:
        main()
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        sys.exit(1)
