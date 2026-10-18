#!/usr/bin/env python3
"""Verify and extract an inventory full backup only into a fresh directory."""
import argparse
import contextlib
import hashlib
import json
from pathlib import Path,PurePosixPath
import sqlite3
import zipfile

def restore(bundle,destination):
    destination=Path(destination)
    if destination.exists():raise FileExistsError('Restore destination must not exist.')
    with zipfile.ZipFile(bundle) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP members.')
        manifest=json.loads(archive.read('MANIFEST.json'));checks=manifest['sha256']
        if not isinstance(checks,dict) or 'hardware.sqlite3' not in checks or set(names)!=set(checks)|{'MANIFEST.json'}:raise ValueError('Backup manifest/member mismatch.')
        for name,expected in checks.items():
            part=PurePosixPath(name)
            if part.is_absolute() or '..' in part.parts or '\\' in name or not (name=='hardware.sqlite3' or len(part.parts)==3 and part.parts[0] in ('photos','manuals','sources')):raise ValueError('Unsafe ZIP member.')
            if hashlib.sha256(archive.read(name)).hexdigest()!=expected:raise ValueError('Backup checksum mismatch.')
        destination.mkdir(parents=True,exist_ok=False,mode=0o700)
        for name in checks:
            path=destination/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(archive.read(name));path.chmod(0o600)
    with contextlib.closing(sqlite3.connect((destination/'hardware.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)) as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Restored database integrity failure.')
    return destination

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('bundle',type=Path);parser.add_argument('destination',type=Path);args=parser.parse_args()
    print('Verified restore:',restore(args.bundle,args.destination))
