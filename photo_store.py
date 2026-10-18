"""Photo import/metadata. Original files never edited or deleted by this app."""
import contextlib
import datetime as dt
from pathlib import Path
import shutil
import sqlite3
import uuid
from PySide6.QtCore import Qt,QFile,QIODevice
from PySide6.QtGui import QImageReader
import inventory
from photo_files import managed_path,sha256

QImageReader.setAllocationLimit(64)

class PhotoStore:
    def __init__(self,db):self.db=Path(db).resolve()
    def list(self,device):
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as c:
            return [dict(r) for r in c.execute('SELECT * FROM device_photos WHERE device_id=? ORDER BY recorded_at,photo_id',(device,))]
    def backup(self):
        path=self.db.parent/'backups'/('before-photo-change-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite3')
        with inventory.exclusive(path):pass
        with contextlib.closing(inventory.connect(self.db,readonly=True)) as src,contextlib.closing(sqlite3.connect(path)) as dest:
            src.backup(dest);inventory.check(dest)
        return path
    def add(self,device,filename,caption,source):
        if not source.strip():raise ValueError('Photo information source is required.')
        filename=Path(filename)
        if filename.stat().st_size>25*1024*1024:raise ValueError('Choose a JPEG or PNG file up to 25 MiB.')
        device=QFile(str(filename))
        if not device.open(QIODevice.ReadOnly):raise OSError(device.errorString())
        try:
            reader=QImageReader(device);reader.setAutoTransform(True)
            fmt=bytes(reader.format()).lower()
            if fmt not in (b'jpeg',b'jpg',b'png'):raise ValueError('Supported photo formats: JPEG and PNG.')
            size=reader.size()
            if size.width()<=0 or size.height()<=0 or size.width()*size.height()>16_000_000:
                raise ValueError('Choose an image up to 16 megapixels; export a smaller copy if needed.')
            image=reader.read()
            if image.isNull():raise ValueError('Could not decode this image: '+reader.errorString())
        finally:device.close()
        ident=uuid.uuid4().hex
        root=self.db.parent/'photos';root.mkdir(exist_ok=True)
        if root.is_symlink():raise ValueError('Managed photos folder must not be a symlink')
        folder=root/ident;folder.mkdir(mode=0o700)
        original=folder/('original.jpg' if fmt in (b'jpg',b'jpeg') else 'original.png')
        thumbnail=folder/'thumbnail.png'
        committed=False
        try:
            shutil.copyfile(filename,original);original.chmod(0o600)
            # Decode the managed copy to protect against source-file changes during import.
            copy_device=QFile(str(original))
            if not copy_device.open(QIODevice.ReadOnly):raise OSError(copy_device.errorString())
            try:
                copyreader=QImageReader(copy_device);copyreader.setAutoTransform(True)
                copied=copyreader.read()
            finally:copy_device.close()
            if copied.isNull() or copied.size()!=image.size() or sha256(filename)!=sha256(original):
                raise ValueError('Source image changed while importing; please retry.')
            small=copied.scaled(240,180,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            if not small.save(str(thumbnail),'PNG'):raise OSError('Could not save thumbnail')
            thumbnail.chmod(0o600)
            self.backup()
            with contextlib.closing(inventory.connect(self.db)) as c:
                with c:
                    c.execute('INSERT INTO device_photos(photo_id,device_id,relative_path,thumbnail_path,caption,source,original_name,sha256,thumbnail_sha256) VALUES(?,?,?,?,?,?,?,?,?)',(ident,device,original.relative_to(self.db.parent).as_posix(),thumbnail.relative_to(self.db.parent).as_posix(),caption.strip() or None,source.strip(),filename.name,sha256(original),sha256(thumbnail)))
            committed=True
            return ident
        finally:
            if not committed:
                original.unlink(missing_ok=True);thumbnail.unlink(missing_ok=True);folder.rmdir()
    def detach(self,photo_id):
        self.backup()
        with contextlib.closing(inventory.connect(self.db)) as c:
            with c:
                result=c.execute('DELETE FROM device_photos WHERE photo_id=?',(photo_id,))
                if result.rowcount!=1:raise ValueError('Photo attachment no longer exists; refresh the device.')
        # Retained files support older database snapshots; deliberate cleanup is separate.
