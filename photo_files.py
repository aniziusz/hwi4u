"""Managed photo paths and portable database-plus-local-files backups."""
import contextlib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import tempfile
import zipfile
import inventory


def managed_path(root, relative):
    part=PurePosixPath(relative)
    if part.is_absolute() or len(part.parts)!=3 or part.parts[0]!='photos' or any(p in ('.','..') for p in part.parts):
        raise ValueError('Unsafe photo path in inventory')
    path=Path(root).joinpath(*part.parts)
    if (Path(root)/'photos').is_symlink():
        raise ValueError('Managed photos folder must not be a symlink')
    photos=(Path(root)/'photos').resolve()
    if not path.resolve().is_relative_to(photos) or path.is_symlink() or path.parent.is_symlink():
        raise ValueError('Photo must be a managed local file, not a symlink')
    return path


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def backup_bundle(db, output):
    """Write a verified portable ZIP; refuse missing or changed attached files."""
    db,output=Path(db).resolve(),Path(output).resolve()
    if output.exists():raise FileExistsError('Backup destination already exists')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        snapshot=Path(tmp)/'hardware.sqlite3'
        with contextlib.closing(inventory.connect(db,readonly=True)) as src, contextlib.closing(sqlite3.connect(snapshot)) as dest:
            src.backup(dest);inventory.check(dest)
            schema_version=dest.execute('PRAGMA user_version').fetchone()[0]
            rows=dest.execute('SELECT relative_path,thumbnail_path,sha256,thumbnail_sha256 FROM device_photos').fetchall()
            manuals=dest.execute("SELECT relative_path,sha256 FROM device_manuals WHERE kind='local'").fetchall()
            from source_store import source_assets,asset_path
            evidence=source_assets(dest)
        files={'hardware.sqlite3':snapshot};expected={}
        for original,thumb,original_hash,thumb_hash in rows:
            for name,digest in ((original,original_hash),(thumb,thumb_hash)):
                file=managed_path(db.parent,name)
                if not file.is_file() or sha256(file)!=digest:
                    raise ValueError('Photo missing or changed; backup aborted: '+name)
                files[name]=file;expected[name]=digest
        from manual_store import manual_path
        for name,digest in manuals:
            path=manual_path(db.parent,name)
            if not path.is_file() or sha256(path)!=digest:raise ValueError('Manual missing or changed; backup aborted: '+name)
            files[name]=path;expected[name]=digest
        for name,digest in evidence:
            path=asset_path(db.parent,name)
            if not path.is_file() or sha256(path)!=digest:raise ValueError('Source file missing or changed; backup aborted: '+name)
            files[name]=path;expected[name]=digest
        expected['hardware.sqlite3']=sha256(snapshot)
        partial=Path(tmp)/'bundle.zip'
        with zipfile.ZipFile(partial,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for name,path in files.items():z.write(path,name)
            z.writestr('MANIFEST.json',json.dumps({'schema_version':schema_version,'sha256':expected},indent=2)+'\n')
        with zipfile.ZipFile(partial) as z:
            if z.testzip() is not None:raise ValueError('Backup archive integrity failed')
            for name,digest in expected.items():
                if hashlib.sha256(z.read(name)).hexdigest()!=digest:raise ValueError('Attached file changed during backup: '+name)
        # Publish without overwriting another backup.
        partial.chmod(0o600)
        os.link(partial,output)
    return output
