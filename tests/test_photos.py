"""Local photo and portable-backup tests; never write real inventory records."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import contextlib
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from photo_store import PhotoStore
from photo_files import backup_bundle,managed_path,sha256
from desktop import Window
from device_store import DeviceStore

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]

class Photos(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.db=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.db)) as c:
            c.executescript((BASE/'schema.sql').read_text())
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('TEST','Test','TEST ONLY')");c.commit()
        self.source=self.root/'source.png';image=QImage(640,480,QImage.Format_RGB32);image.fill(Qt.blue);self.assertTrue(image.save(str(self.source)))
        self.photos=PhotoStore(self.db)
    def test_import_ui_bundle_and_detach(self):
        ident=self.photos.add('TEST',self.source,'Device front','TEST ONLY')
        row=self.photos.list('TEST')[0]
        self.assertEqual(row['photo_id'],ident)
        self.assertEqual(sha256(managed_path(self.root,row['relative_path'])),sha256(self.source))
        self.assertTrue(managed_path(self.root,row['thumbnail_path']).is_file())
        window=Window(DeviceStore(self.db));self.addCleanup(window.deleteLater)
        window.load(window.store.devices()[0]);self.assertEqual(window.photo_list.count(),1)
        bundle=backup_bundle(self.db,self.root/'complete.zip')
        restored=self.root/'restored';restored.mkdir()
        with zipfile.ZipFile(bundle) as z:z.extractall(restored)
        self.assertEqual(len(PhotoStore(restored/'hardware.sqlite3').list('TEST')),1)
        self.assertTrue(managed_path(restored,row['relative_path']).is_file())
        with contextlib.closing(sqlite3.connect(restored/'hardware.sqlite3')) as c:
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
        self.photos.detach(ident);self.assertEqual(self.photos.list('TEST'),[])
        self.assertTrue(managed_path(self.root,row['relative_path']).is_file())
        self.assertTrue(self.source.is_file())
    def test_invalid_imports_and_cleanup(self):
        with self.assertRaises(ValueError):self.photos.add('TEST',self.source,'',' ')
        invalid=self.root/'bad.png';invalid.write_text('not an image')
        with self.assertRaises(ValueError):self.photos.add('TEST',invalid,'','TEST ONLY')
        with self.assertRaises(sqlite3.IntegrityError):self.photos.add('MISSING',self.source,'','TEST ONLY')
        self.assertEqual(list((self.root/'photos').iterdir()),[])
        with patch.object(PhotoStore,'backup',side_effect=OSError('backup failed')):
            with self.assertRaises(OSError):self.photos.add('TEST',self.source,'','TEST ONLY')
        self.assertEqual(list((self.root/'photos').iterdir()),[])
        for path in ('../outside.png','/tmp/outside','photos/../outside','photos/id/../../outside'):
            with self.assertRaises(ValueError):managed_path(self.root,path)
    def test_backup_checks_missing_and_changed_images(self):
        self.photos.add('TEST',self.source,'','TEST ONLY');row=self.photos.list('TEST')[0]
        photo=managed_path(self.root,row['relative_path']);photo.write_bytes(b'changed')
        with self.assertRaises(ValueError):backup_bundle(self.db,self.root/'bad.zip')
        self.assertFalse((self.root/'bad.zip').exists())
        photo.unlink()
        with self.assertRaises(ValueError):backup_bundle(self.db,self.root/'missing.zip')
    def test_migration_preserves_existing_rows(self):
        with contextlib.closing(sqlite3.connect(self.root/'old.sqlite3')) as c:
            old=(BASE/'schema.sql').read_text().split('CREATE TABLE device_photos')[0]+'PRAGMA user_version=9;\nCOMMIT;'
            c.executescript(old)
            c.execute("INSERT INTO devices(device_id,name,source,current_state) VALUES('OLD','Old','TEST ONLY','in use')");c.commit()
            before=c.execute('SELECT * FROM devices').fetchall()
            c.executescript((BASE/'migrations/010-photo-attachments.sql').read_text())
            self.assertEqual(before,c.execute('SELECT * FROM devices').fetchall())
            self.assertEqual(c.execute('SELECT count(*) FROM device_photos').fetchone()[0],0)

if __name__=='__main__':unittest.main()
