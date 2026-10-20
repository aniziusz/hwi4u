"""Staged local releases and locked, backed-up SQLite migrations. No network access."""
import ast
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
import zipfile

UPDATE_EXIT=75

def digest(data):return hashlib.sha256(data).hexdigest()
def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name('.'+path.name+'-'+uuid.uuid4().hex)
    try:
        with tmp.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)

def source_files(root):
    files=[*root.glob('*.py'),root/'schema.sql',root/'LICENSE-desktop.txt',*root.glob('GUIDE.*.md'),*root.glob('README.*.md'),*root.glob('UPDATES.*.md'),*root.glob('NETWORK.*.md'),*root.glob('HWI4U.*.md'),*root.glob('TESTING.*.md'),*root.glob('*.sh'),*root.glob('*.cmd'),*root.glob('*.command'),*root.glob('FEATURES.*.md'),*root.glob('SOURCES.*.md'),*root.glob('TOPOLOGY.*.md')]
    files += [*root.glob('LICENSE'),*root.glob('NOTICE.*.md'),*root.glob('CONTRIBUTING.*.md'),*root.glob('requirements*.txt'),*root.glob('.python-version'),*list((root/'docs').glob('*.md')),*list((root/'tools').glob('*.py'))]
    files += list((root/'locales').glob('*.json'))
    files += list((root/'migrations').glob('*.sql')) + list((root/'tests').rglob('*.py')) + list((root/'tests/fixtures').glob('*.sql'))
    return {f.relative_to(root).as_posix():f.read_bytes() for f in sorted(files) if f.is_file()}

def verify_release(folder):
    folder=Path(folder);meta=json.loads((folder/'release.json').read_text())
    for name,expected in meta['sha256'].items():
        path=folder/name
        if Path(name).is_absolute() or '..' in Path(name).parts or path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()):raise ValueError('Unsafe release path')
        if digest(path.read_bytes())!=expected:raise ValueError('Release file changed: '+name)
    calculated=digest(json.dumps(meta['sha256'],sort_keys=True).encode())
    if calculated!=meta['release_id']:raise ValueError('Release identity mismatch')
    return meta

def channel_pointer(root,channel='production'):
    if channel not in ('production','test'):raise ValueError('Unknown release channel')
    return Path(root)/'.runtime'/('test.json' if channel=='test' else 'current.json')

def publish_pointer(root,ident,channel='production'):
    path=channel_pointer(root,channel);value={'release_id':ident}
    if path.exists():
        old=json.loads(path.read_text())
        previous=old.get('release_id') if old.get('release_id')!=ident else old.get('previous_release_id')
        if previous:value['previous_release_id']=previous
    atomic_json(path,value)

def published(root,channel='production'):
    root=Path(root).resolve();pointer=channel_pointer(root,channel)
    if not pointer.exists():return None
    ident=json.loads(pointer.read_text())['release_id']
    if not re.fullmatch('[0-9a-f]{64}',ident):raise ValueError('Invalid published release identity')
    folder=root/'.runtime/releases'/ident
    return folder,verify_release(folder)

def publish(root,run_tests=True,channel='test'):
    channel_pointer(root,channel)
    root=Path(root).resolve();files=source_files(root)
    hashes={name:digest(data) for name,data in files.items()};ident=digest(json.dumps(hashes,sort_keys=True).encode())
    release=root/'.runtime/releases'/ident;release.parent.mkdir(parents=True,exist_ok=True)
    if release.exists():
        verify_release(release)
        if run_tests:
            from validation import run_full
            run_full(release,root/'.runtime/validation')
        publish_pointer(root,ident,channel);return release
    with tempfile.TemporaryDirectory(prefix='stage-',dir=release.parent) as tmp:
        stage=Path(tmp)/'release';stage.mkdir()
        for name,data in files.items():
            path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            if path.suffix=='.py':compile(data,str(path),'exec')
        versions={node.targets[0].id:ast.literal_eval(node.value) for node in ast.parse(files['ui_i18n.py']).body if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('APP_VERSION','RELEASE_DATE')}
        schema=int(re.findall(rb'PRAGMA user_version\s*=\s*(\d+)',files['schema.sql'])[-1])
        meta={'release_id':ident,'version':versions['APP_VERSION'],'date':versions['RELEASE_DATE'],'schema_version':schema,'sha256':hashes}
        (stage/'release.json').write_text(json.dumps(meta,indent=2)+'\n')
        if run_tests:
            from validation import run_full
            run_full(stage,root/'.runtime/validation')
        if source_files(root)!=files:raise RuntimeError('Source changed during validation; publish again after edits finish.')
        verify_release(stage)
        os.replace(stage,release)
    publish_pointer(root,ident,channel)
    return release

def sql_statements(script):
    buffer=''
    for line in script.splitlines(keepends=True):
        buffer+=line
        if sqlite3.complete_statement(buffer):
            text=buffer.strip();buffer=''
            if re.fullmatch(r'(?:PRAGMA foreign_keys\s*=\s*(?:ON|OFF)|BEGIN(?: IMMEDIATE)?|COMMIT);',text,re.I):continue
            yield text
    if buffer.strip():raise ValueError('Incomplete migration SQL')

def full_snapshot_locked(db,output):
    """Caller holds BEGIN IMMEDIATE on another connection, excluding other writers."""
    db=Path(db);output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        snapshot=Path(tmp)/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as src,contextlib.closing(sqlite3.connect(snapshot)) as dest:
            src.backup(dest)
            if dest.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or dest.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Pre-update integrity check failed')
            files={'hardware.sqlite3':snapshot};tables={r[0] for r in dest.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            rows=[]
            if 'device_photos' in tables:
                for original,thumb,original_hash,thumb_hash in dest.execute('SELECT relative_path,thumbnail_path,sha256,thumbnail_sha256 FROM device_photos'):
                    rows.extend(((original,original_hash),(thumb,thumb_hash)))
            if 'device_manuals' in tables:rows.extend(dest.execute("SELECT relative_path,sha256 FROM device_manuals WHERE kind='local'"))
            from source_store import source_assets,asset_path
            for source_name,source_hash in source_assets(dest):
                asset_path(db.parent,source_name)
                rows.append((source_name,source_hash))
            for name,expected in rows:
                relative=Path(name);file=db.parent/relative
                if relative.is_absolute() or '..' in relative.parts or len(relative.parts)!=3 or relative.parts[0] not in ('photos','manuals','sources') or any(part.is_symlink() for part in (file,file.parent,file.parent.parent)) or not file.resolve().is_relative_to(db.parent.resolve()):raise ValueError('Unsafe attachment path')
                if digest(file.read_bytes())!=expected:raise ValueError('Attachment missing or changed: '+name)
                files[name]=file
        checks={name:digest(path.read_bytes()) for name,path in files.items()}
        staged=Path(tmp)/'bundle.zip'
        with zipfile.ZipFile(staged,'x',zipfile.ZIP_DEFLATED) as z:
            for name,path in files.items():z.write(path,name)
            z.writestr('MANIFEST.json',json.dumps({'sha256':checks},indent=2))
        with zipfile.ZipFile(staged) as z:
            if z.testzip() is not None:raise ValueError('Backup ZIP integrity failed')
            for name,expected in checks.items():
                if digest(z.read(name))!=expected:raise ValueError('Backup checksum mismatch')
        staged.chmod(0o600)
        os.link(staged,output)

def prepare_database(db,release):
    """Apply only ordered migrations in one transaction; lock contention never kills data."""
    db=Path(db).resolve();release=Path(release);meta=verify_release(release)
    con=sqlite3.connect(db.as_uri()+'?mode=rw',uri=True,timeout=2);con.row_factory=sqlite3.Row
    try:
        version=con.execute('PRAGMA user_version').fetchone()[0];target=meta['schema_version']
        if version==target:return None
        if version>target:raise ValueError('Database is newer than this release; refusing a downgrade.')
        scripts=[]
        for next_version in range(version+1,target+1):
            matches=list((release/'migrations').glob(f'{next_version:03d}-*.sql'))
            if len(matches)!=1:raise ValueError('No unique migration for schema '+str(next_version))
            scripts.extend(sql_statements(matches[0].read_text()))
        con.execute('PRAGMA foreign_keys=OFF');con.execute('BEGIN IMMEDIATE')
        backup=db.parent/'backups'/('before-managed-update-'+uuid.uuid4().hex+'.zip')
        full_snapshot_locked(db,backup)
        for statement in scripts:con.execute(statement)
        if con.execute('PRAGMA user_version').fetchone()[0]!=target:raise ValueError('Migration did not reach target schema')
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Migration integrity failure')
        # Run the new release's application invariants before committing.
        import inventory
        inventory.check(con)
        con.commit();return backup
    except Exception:
        con.rollback();raise
    finally:con.close()

def supervise(root,args,channel='production'):
    root=Path(root).resolve();selection=published(root,channel)
    if selection is None:
        raise ValueError('No published release for this channel. Publish a test candidate first.')
    db=root/'hardware.sqlite3'
    if '--db' in args:db=Path(args[args.index('--db')+1]).resolve()
    else:
        value=next((v.split('=',1)[1] for v in args if v.startswith('--db=')),None)
        if value:db=Path(value).resolve()
        else:args=['--db',str(db),*args]
    if channel=='test':
        from environments import validate_test_database
        validate_test_database(root,db)
    active_file=root/'.runtime'/('active-'+digest(str(db).encode())[:16]+'.json')
    last=None
    if active_file.exists():
        old=json.loads(active_file.read_text());candidate=root/'.runtime/releases'/old['release_id']
        if candidate.exists():last=(candidate,verify_release(candidate))
    if last is None:
        previous=json.loads(channel_pointer(root,channel).read_text()).get('previous_release_id')
        if previous and re.fullmatch('[0-9a-f]{64}',previous):
            candidate=root/'.runtime/releases'/previous
            if candidate.exists():last=(candidate,verify_release(candidate))
    error=''
    while True:
        folder,meta=selection
        prepared=subprocess.run([sys.executable,str(folder/'run_desktop.py'),'prepare','--db',str(db)],capture_output=True,text=True)
        if prepared.returncode:
            error=prepared.stderr.strip() or prepared.stdout.strip() or 'Update could not be prepared.'
            if last and last[1]['release_id']!=meta['release_id']:
                selection=last;continue
            raise RuntimeError(error)
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','INVENTORY_PROJECT_ROOT':str(root),'INVENTORY_RELEASE_ID':meta['release_id'],'INVENTORY_UPDATE_ERROR':error,'INVENTORY_CHANNEL':channel}
        atomic_json(active_file,{'release_id':meta['release_id']})
        if channel=='test':
            from environments import record_test_launch
            record_test_launch(root,db,meta['release_id'])
        result=subprocess.run([sys.executable,str(folder/'desktop.py'),*args],env=env)
        if result.returncode!=UPDATE_EXIT:return result.returncode
        last=selection;selection=published(root,channel) or selection;error=''
