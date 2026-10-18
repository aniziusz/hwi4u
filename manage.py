#!/usr/bin/env python3
"""Create and run a private workspace independently of the source repository."""
import argparse
import contextlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from update_runtime import atomic_json,digest,publish,publish_pointer,source_files,published

MARKER='.hwi4u-workspace.json'

def default_workspace():
    if os.name=='nt':return Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData/Local'))/'HWI4U'
    if sys.platform=='darwin':return Path.home()/'Library/Application Support/HWI4U'
    return Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'hwi4u'

def validate_target(source,target):
    source=Path(source).resolve();target=Path(target).expanduser().resolve()
    if target==source or target.is_relative_to(source):raise ValueError('The private workspace must be outside the source repository.')
    return target

def synchronize_source(source,target):
    """Only the explicit application-source list is copied; private files are untouched."""
    target=validate_target(source,target);marker=target/MARKER
    state=json.loads(marker.read_text())
    if state.get('format')!=1:raise ValueError('Unsupported workspace format.')
    files=source_files(Path(source));old=state.get('source_sha256',{})
    for name in set(old)|set(files):
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe source manifest path.')
        path=target/relative
        if any(part.is_symlink() for part in (path,*path.parents)) or not path.resolve().is_relative_to(target):raise ValueError('Source paths must not be symlinks.')
        if path.exists():
            allowed={old.get(name),digest(files[name]) if name in files else None}
            if digest(path.read_bytes()) not in allowed:raise ValueError('Workspace source was edited: '+name+'. Preserve your changes and edit the source repository instead.')
    for name in old.keys()-files.keys():(target/name).unlink(missing_ok=True)
    for name,content in files.items():
        path=target/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(content)
        if path.suffix=='.sh':path.chmod(0o700)
    atomic_json(marker,dict(format=1,source_sha256={n:digest(b) for n,b in files.items()}))
    return target

def initialize(source,target,run_tests=True):
    source=Path(source).resolve();target=validate_target(source,target)
    target.mkdir(parents=True,exist_ok=False,mode=0o700)
    # Existing directories/databases are never adopted or overwritten implicitly.
    atomic_json(target/MARKER,dict(format=1,source_sha256={}))
    synchronize_source(source,target)
    db=target/'hardware.sqlite3'
    with contextlib.closing(sqlite3.connect(db)) as con:
        con.executescript((target/'schema.sql').read_text())
        import inventory
        inventory.check(con)
        if con.execute('SELECT count(*) FROM devices').fetchone()[0]:raise ValueError('Fresh schema must contain no devices.')
    db.chmod(0o600)
    release=publish(target,run_tests=run_tests)
    meta=json.loads((release/'release.json').read_text())
    # This is a new empty installation, not acceptance of an existing inventory update.
    publish_pointer(target,meta['release_id'],'production')
    from environments import refresh_test
    refresh_test(target)
    atomic_json(target/'INSTALLATION.json',dict(format=1,initial_release=meta['release_id'],schema_version=meta['schema_version'],note='Fresh empty installation; no inventory imported.'))
    return target

def execute(source,target,action):
    target=validate_target(source,target)
    if not (target/'INSTALLATION.json').is_file():raise ValueError('No initialized workspace. Run manage.py init first.')
    commands={'run':[],'test':['test'],'refresh-test':['refresh-test','--gui'],'promote':['promote-test','--gui']}
    if action=='publish':
        synchronize_source(source,target)
        print('TEST candidate:',publish(target));return 0
    return subprocess.call([sys.executable,str(target/'run_desktop.py'),*commands[action]])

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('init','run','test','publish','refresh-test','promote'))
    parser.add_argument('--workspace',type=Path,default=default_workspace())
    args=parser.parse_args(argv);source=Path(__file__).resolve().parent
    if args.action=='init':print('Created empty private workspace:',initialize(source,args.workspace));return 0
    return execute(source,args.workspace,args.action)

if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,sqlite3.Error,RuntimeError) as exc:
        print('HWI4U: '+str(exc),file=sys.stderr);sys.exit(1)
