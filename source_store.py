"""Reusable immutable evidence entries and atomic, scoped assignment history."""
import contextlib
import datetime as dt
import json
from pathlib import Path,PurePosixPath
import re
import shutil
import sqlite3
import uuid
import inventory
from manual_store import validate_url

SCOPES=('device','software','network','interface','protocol')
KINDS=('website','document','photo','observation','legacy_text')
FIELDS=('kind','title','url','relative_path','original_name','sha256','body','observed_on','evidence_status','source_note','origin_key','supersedes')


def asset_path(root,relative):
    p=PurePosixPath(relative)
    if p.is_absolute() or len(p.parts)!=3 or '..' in p.parts or p.parts[0] not in ('sources','manuals','photos') or not re.fullmatch('[0-9a-f]{32}',p.parts[1]):raise ValueError('Unsafe source file path.')
    if p.parts[0]=='sources' and p.parts[2] not in ('document.pdf','image.jpg','image.png'):raise ValueError('Unsafe source file name.')
    root=Path(root);path=root.joinpath(*p.parts);base=root/p.parts[0]
    if any(x.is_symlink() for x in (base,path.parent,path)) or not path.resolve().is_relative_to(base.resolve()):raise ValueError('Source files must not be symlinks.')
    return path


def source_assets(con):
    if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='source_entries'").fetchone():return []
    return con.execute('SELECT relative_path,sha256 FROM source_entries WHERE relative_path IS NOT NULL').fetchall()


def validate_entry(data):
    result={k:data.get(k) for k in FIELDS}
    for key,value in result.items():
        if value is not None and not isinstance(value,str):raise ValueError('Source metadata must be text or unknown.')
        if key not in ('body',):result[key]=value.strip() or None if value is not None else None
    if result['kind'] not in KINDS:raise ValueError('Choose a valid source kind.')
    if not result['title'] or len(result['title'])>200:raise ValueError('A source title of 1–200 characters is required.')
    if result['evidence_status'] not in ('uncertain','user_reported','verified'):raise ValueError('Choose a valid source verification status.')
    if result['observed_on'] is not None:
        try:inventory.date(result['observed_on'])
        except Exception:raise ValueError('Choose a valid source observation or access date.')
    if result['evidence_status']=='verified' and not result['observed_on']:raise ValueError('A verified source needs an observation or access date.')
    if result['kind']=='website':
        validate_url(result['url'])
        if result['relative_path'] is not None:raise ValueError('A website source cannot have a local file.')
    elif result['kind'] in ('observation','legacy_text'):
        if not result['body'] or not result['body'].strip():raise ValueError('Write the observation or preserved source text.')
        if result['url'] or result['relative_path']:raise ValueError('An observation uses text, not a website or file.')
    else:
        if not result['relative_path'] or not result['original_name'] or not re.fullmatch('[0-9a-f]{64}',result['sha256'] or ''):raise ValueError('Local source file metadata is incomplete.')
        # Validate lexical paths without requiring files in database-only snapshots.
        parts=PurePosixPath(result['relative_path'])
        if parts.parts and parts.parts[0]=='sources' and parts.name not in ('document.pdf','image.jpg','image.png'):raise ValueError('Unsafe source file name.')
        if parts.is_absolute() or len(parts.parts)!=3 or parts.parts[0] not in ('sources','manuals','photos') or '..' in parts.parts or not re.fullmatch('[0-9a-f]{32}',parts.parts[1]):raise ValueError('Unsafe source file path.')
        if result['kind']=='document' and parts.suffix.lower()!='.pdf':raise ValueError('A document source must use a PDF file.')
        if result['kind']=='photo' and parts.suffix.lower() not in ('.jpg','.jpeg','.png'):raise ValueError('A photo source must use a JPEG or PNG file.')
        if result['url']:raise ValueError('A local source cannot have a website URL.')
    return result


def load_links(con,device):
    result={scope:[] for scope in SCOPES}
    for scope,ident in con.execute('SELECT scope,source_id FROM source_links WHERE device_id=? ORDER BY scope,source_id',(device,)):result[scope].append(ident)
    return result


def validate_links(con,data):
    if not isinstance(data,dict) or set(data)!=set(SCOPES):raise ValueError('Source assignments need all assessment sections.')
    result={}
    for scope,ids in data.items():
        if not isinstance(ids,list) or not all(isinstance(v,str) for v in ids) or len(ids)!=len(set(ids)):raise ValueError('Choose each source only once per section.')
        for ident in ids:
            if not con.execute('SELECT 1 FROM source_entries WHERE source_id=?',(ident,)).fetchone():raise ValueError('A selected source no longer exists; reopen the source selector.')
        result[scope]=sorted(ids)
    return result


def citation(con,ids):
    return 'Sources and evidence: '+'; '.join(con.execute('SELECT title FROM source_entries WHERE source_id=?',(ident,)).fetchone()[0]+' [source:'+ident+']' for ident in ids) if ids else None


def save_links(con,device,data):
    if load_links(con,device)==data:return
    con.execute('INSERT INTO source_link_history(device_id,links_json) VALUES(?,?)',(device,json.dumps(data,sort_keys=True)))
    con.execute('DELETE FROM source_links WHERE device_id=?',(device,))
    con.executemany('INSERT INTO source_links(device_id,scope,source_id) VALUES(?,?,?)',[(device,scope,ident) for scope,ids in data.items() for ident in ids])


def audit_sources(con):
    cursor=con.cursor();cursor.row_factory=sqlite3.Row
    for row in cursor.execute('SELECT * FROM source_entries'):validate_entry(dict(row))
    for (device,) in con.execute('SELECT DISTINCT device_id FROM source_links'):validate_links(con,load_links(con,device))
    for (payload,) in con.execute('SELECT links_json FROM source_link_history'):validate_links(con,json.loads(payload))


class SourceStore:
    def __init__(self,db):self.db=Path(db).resolve()
    def list(self):
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as c:return [dict(r) for r in c.execute('SELECT * FROM source_entries ORDER BY title,created_at,source_id')]
    def _backup(self):
        output=self.db.parent/'backups'/('before-source-change-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite3')
        with inventory.exclusive(output):pass
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as src,contextlib.closing(sqlite3.connect(output)) as dest:src.backup(dest);inventory.check(dest)
    def save(self,data,filename=None,original=None,asset=None):
        from photo_files import sha256
        ident=uuid.uuid4().hex;values={k:data.get(k) for k in FIELDS};folder=None;committed=False
        if original:
            if values['kind']!=original['kind']:raise ValueError('A revision must keep the source kind; add a new source instead.')
            values['supersedes']=original['source_id'];values['origin_key']=None
            for k in ('relative_path','sha256','original_name'):values[k]=original[k]
        elif asset:
            for k in ('relative_path','sha256','original_name'):values[k]=asset[k]
        try:
            if values['kind'] in ('document','photo') and not original and not asset:
                source=Path(filename) if filename else None
                if source is None or not source.is_file():raise ValueError('Choose a local source file.')
                if values['kind']=='document':
                    if source.suffix.lower()!='.pdf' or source.stat().st_size>100*1024*1024:raise ValueError('Choose a PDF file up to 100 MiB.')
                    with source.open('rb') as f:
                        if not f.read(1024).startswith(b'%PDF-'):raise ValueError('This file does not have a PDF header.')
                    name='document.pdf'
                else:
                    from PySide6.QtGui import QImageReader
                    from PySide6.QtCore import QFile,QIODevice
                    if source.stat().st_size>25*1024*1024:raise ValueError('Choose a JPEG or PNG file up to 25 MiB.')
                    source_device=QFile(str(source))
                    if not source_device.open(QIODevice.ReadOnly):raise OSError(source_device.errorString())
                    try:
                        reader=QImageReader(source_device);size=reader.size();fmt=bytes(reader.format()).lower()
                        if fmt not in (b'jpg',b'jpeg',b'png') or size.width()<=0 or size.height()<=0 or size.width()*size.height()>16_000_000 or reader.read().isNull():raise ValueError('Choose a valid JPEG/PNG photo up to 16 megapixels.')
                    finally:source_device.close()
                    name='image.png' if fmt==b'png' else 'image.jpg'
                values['relative_path']=f'sources/{ident}/{name}';destination=asset_path(self.db.parent,values['relative_path']);destination.parent.parent.mkdir(exist_ok=True);destination.parent.mkdir(mode=0o700);folder=destination.parent
                shutil.copyfile(source,destination);destination.chmod(0o600)
                if sha256(source)!=sha256(destination):raise ValueError('Source file changed during import; retry.')
                if values['kind']=='photo':
                    copy_device=QFile(str(destination))
                    if not copy_device.open(QIODevice.ReadOnly):raise OSError(copy_device.errorString())
                    try:
                        copied=QImageReader(copy_device);copied_size=copied.size()
                        if copied_size!=size or bytes(copied.format()).lower()!=fmt or copied.read().isNull():raise ValueError('Source photo changed during import; retry.')
                    finally:copy_device.close()
                else:
                    with destination.open('rb') as f:
                        if not f.read(1024).startswith(b'%PDF-'):raise ValueError('Source document changed during import; retry.')
                values.update(original_name=source.name,sha256=sha256(destination))
            values=validate_entry(values)
            if values['relative_path']:
                file=asset_path(self.db.parent,values['relative_path'])
                if not file.is_file() or sha256(file)!=values['sha256']:raise ValueError('Source file is missing or changed.')
            with contextlib.closing(inventory.connect(self.db)) as c:
                c.execute('BEGIN IMMEDIATE')
                if original:
                    current=c.execute('SELECT * FROM source_entries WHERE source_id=?',(original['source_id'],)).fetchone()
                    if current is None or dict(current)!=original:raise ValueError('Source changed outside this dialog; reopen it.')
                self._backup()
                c.execute('INSERT INTO source_entries(source_id,'+','.join(FIELDS)+') VALUES('+','.join('?' for _ in range(len(FIELDS)+1))+')',(ident,*(values[k] for k in FIELDS)))
                c.commit();committed=True;return ident
        finally:
            if folder and not committed:
                for file in folder.iterdir():file.unlink()
                folder.rmdir()
    def reusable(self,device):
        if not device:return []
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as c:
            return [('manual',dict(r)) for r in c.execute('SELECT * FROM device_manuals WHERE device_id=? ORDER BY title',(device,))]+[('photo',dict(r)) for r in c.execute('SELECT * FROM device_photos WHERE device_id=? ORDER BY recorded_at',(device,))]
    def import_existing(self,kind,row):
        from photo_files import sha256
        key=kind+':'+sha256_bytes(json.dumps(row,sort_keys=True))
        for entry in self.list():
            if entry['origin_key']==key:return entry['source_id']
        if kind=='manual':
            details=[label+': '+row[key] for key,label in [('applicable_model','Applicable model'),('language','Language'),('edition','Edition')] if row[key]]
            if row['notes']:details.append(row['notes'])
            data=dict(kind='website' if row['kind']=='online' else 'document',title=row['title'][:200],url=row['url'],body='\n'.join((['Original title: '+row['title']] if len(row['title'])>200 else [])+details) or None)
        elif kind=='photo':
            full_title=row['caption'] or row['original_name'];data=dict(kind='photo',title=full_title[:200],body=full_title if len(full_title)>200 else None,url=None)
        else:raise ValueError('Unknown existing attachment kind.')
        data.update(evidence_status='uncertain',source_note=row['source'],origin_key=key)
        return self.save(data,asset=row if data['kind'] in ('photo','document') else None)


def sha256_bytes(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()
