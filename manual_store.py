"""Online manual links and separately stored local PDF references."""
import contextlib
import datetime as dt
from pathlib import Path,PurePosixPath
import re
import shutil
import sqlite3
from urllib.parse import urlsplit
import uuid
import inventory

META=('title','language','edition','applicable_model','source','notes')

def validate_url(value):
    if not isinstance(value,str) or not value or any(c.isspace() or ord(c)<32 for c in value):
        raise ValueError('Enter a complete HTTP or HTTPS URL without spaces.')
    try:
        parsed=urlsplit(value)
        if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username is not None or parsed.password is not None or '\\' in value:
            raise ValueError()
        parsed.port
    except ValueError:raise ValueError('Use an HTTP or HTTPS URL with a host and without embedded credentials.')
    return value

def relative_parts(relative):
    p=PurePosixPath(relative)
    if p.is_absolute() or len(p.parts)!=3 or p.parts[0]!='manuals' or p.parts[2]!='document.pdf' or not re.fullmatch('[0-9a-f]{32}',p.parts[1]):
        raise ValueError('Unsafe manual file path in inventory.')
    return p.parts

def manual_path(root,relative):
    parts=relative_parts(relative)
    base=Path(root)/'manuals';path=base/parts[1]/parts[2]
    if base.is_symlink() or path.parent.is_symlink() or path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
        raise ValueError('Manual must be a managed local file, not a symlink.')
    return path

def validate_metadata(data):
    result={}
    for key in META:
        value=data.get(key)
        if value is not None and not isinstance(value,str):raise ValueError('Manual metadata must be text.')
        result[key]=value.strip() or None if value is not None else None
    if not result['title'] or not result['source']:raise ValueError('Manual title and information source are required.')
    if result['language'] is not None:
        if not re.fullmatch(r'[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*',result['language']):raise ValueError('Use a language code such as en, de, hu or en-GB; leave unknown blank.')
        result['language']=result['language'].lower()
    return result

def audit_manuals(con):
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    for r in cursor.execute('SELECT * FROM device_manuals'):
        validate_metadata(dict(r))
        if r['kind']=='online':validate_url(r['url'])
        else:relative_parts(r['relative_path'])
    # File existence/hashes are checked on opening/full backup, not database-only snapshots.

class ManualStore:
    def __init__(self,db):self.db=Path(db).resolve()
    def list(self,device):
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as c:
            return [dict(r) for r in c.execute('SELECT * FROM device_manuals WHERE device_id=? ORDER BY title,reference_id',(device,))]
    def _backup(self):
        name='before-manual-change-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite3'
        path=self.db.parent/'backups'/name
        with inventory.exclusive(path):pass
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as src, contextlib.closing(sqlite3.connect(path)) as dest:
            src.backup(dest);inventory.check(dest)
        return path
    def save(self,device,kind,data,location=None,original=None):
        values=validate_metadata(data)
        if kind not in ('online','local'):raise ValueError('Choose an online link or local PDF.')
        if original is not None and (original['device_id']!=device or original['kind']!=kind):raise ValueError('Reference device and kind cannot be changed by editing.')
        ident=original['reference_id'] if original else uuid.uuid4().hex
        url=validate_url(location.strip()) if kind=='online' and isinstance(location,str) else None
        if kind=='online' and url is None:raise ValueError('An online reference needs a URL.')
        path=None;created=False;committed=False
        from photo_files import sha256
        relative=original['relative_path'] if original else None
        original_name=original['original_name'] if original else None
        digest=original['sha256'] if original else None
        try:
            if kind=='local' and original is None:
                source=Path(location) if location else None
                if source is None or not source.is_file():raise ValueError('Choose a local PDF file.')
                if source.suffix.lower()!='.pdf' or source.stat().st_size>100*1024*1024:raise ValueError('Choose a PDF file up to 100 MiB.')
                with source.open('rb') as f:
                    if not f.read(1024).startswith(b'%PDF-'):raise ValueError('This file does not have a PDF header.')
                root=self.db.parent/'manuals';root.mkdir(exist_ok=True)
                if root.is_symlink():raise ValueError('Managed manuals folder must not be a symlink.')
                relative=f'manuals/{ident}/document.pdf';path=manual_path(self.db.parent,relative);path.parent.mkdir(mode=0o700);created=True
                shutil.copyfile(source,path);path.chmod(0o600)
                if path.stat().st_size>100*1024*1024 or sha256(path)!=sha256(source):raise ValueError('Manual changed during import; please retry.')
                original_name=source.name;digest=sha256(path)
            c=inventory.connect(self.db)
            try:
                c.execute('BEGIN IMMEDIATE')
                if original is not None:
                    current=c.execute('SELECT * FROM device_manuals WHERE reference_id=?',(ident,)).fetchone()
                    if current is None or dict(current)!=original:raise ValueError('Manual reference changed outside this dialog; refresh and try again.')
                self._backup()
                if original is None:
                    fields=('reference_id','device_id','kind','url','relative_path','original_name','sha256')+META
                    payload=(ident,device,kind,url,relative,original_name,digest)+tuple(values[k] for k in META)
                    c.execute('INSERT INTO device_manuals('+','.join(fields)+') VALUES('+','.join('?' for _ in fields)+')',payload)
                else:
                    fields=META+('url',)
                    c.execute('UPDATE device_manuals SET '+','.join(k+'=?' for k in fields)+' WHERE reference_id=?',tuple(values[k] for k in META)+(url,ident))
                c.commit();committed=True;return ident
            except Exception:c.rollback();raise
            finally:c.close()
        finally:
            if created and not committed:
                path.unlink(missing_ok=True);path.parent.rmdir()
    def detach(self,original):
        c=inventory.connect(self.db)
        try:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM device_manuals WHERE reference_id=?',(original['reference_id'],)).fetchone()
            if row is None or dict(row)!=original:raise ValueError('Manual reference changed outside this dialog; refresh and try again.')
            self._backup();c.execute('DELETE FROM device_manuals WHERE reference_id=?',(original['reference_id'],));c.commit()
        except Exception:c.rollback();raise
        finally:c.close()
