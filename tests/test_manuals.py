"""Manual references, managed paths, GUI actions and portable recovery."""
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
from PySide6.QtWidgets import QApplication,QMessageBox
from device_store import DeviceStore
from manual_store import ManualStore,manual_path,validate_url
from photo_files import backup_bundle,sha256
from desktop import Window,ManualDialog
import inventory

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]
class Manuals(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.db=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.db)) as c:
            c.executescript((BASE/'schema.sql').read_text());c.execute("INSERT INTO devices(device_id,name,source) VALUES('TEST','Test','TEST ONLY')");c.commit()
        self.store=ManualStore(self.db);self.meta={'title':'Installation guide','source':'TEST ONLY','language':'en','edition':'Revision A','applicable_model':'TEST MODEL'}
        self.pdf=self.root/'original.pdf';self.pdf.write_bytes(b'%PDF-1.4\n%Synthetic test fixture, not a real manual\n%%EOF\n')
    def test_multiple_links_copy_edit_and_restore(self):
        self.store.save('TEST','online',self.meta,'https://example.invalid/manual.pdf')
        self.store.save('TEST','local',{**self.meta,'title':'Offline guide'},self.pdf)
        rows=self.store.list('TEST');self.assertEqual(len(rows),2)
        local=next(r for r in rows if r['kind']=='local');managed=manual_path(self.root,local['relative_path'])
        self.assertEqual(sha256(managed),sha256(self.pdf))
        self.store.save('TEST','local',{**self.meta,'title':'Edited offline guide'},original=local)
        self.assertEqual(next(r for r in self.store.list('TEST') if r['kind']=='local')['title'],'Edited offline guide')
        archive=backup_bundle(self.db,self.root/'complete.zip');restore=self.root/'restored';restore.mkdir()
        with zipfile.ZipFile(archive) as z:z.extractall(restore)
        recovered=ManualStore(restore/'hardware.sqlite3').list('TEST');self.assertEqual(len(recovered),2)
        self.assertTrue(manual_path(restore,local['relative_path']).is_file())
        row=next(r for r in self.store.list('TEST') if r['kind']=='local');self.store.detach(row)
        self.assertEqual(len(self.store.list('TEST')),1);self.assertTrue(managed.is_file());self.assertTrue(self.pdf.is_file())
    def test_invalid_urls_metadata_and_cleanup(self):
        for url in ('javascript:alert(1)','file:///tmp/manual.pdf','ftp://example.invalid/manual','https://user:pass@example.invalid/a','https://example.invalid/a b','https://example.invalid:bad/a'):
            with self.assertRaises(ValueError,msg=url):validate_url(url)
        for bad in ({'title':''},{'source':''},{'language':'English'}):
            with self.assertRaises(ValueError):self.store.save('TEST','online',{**self.meta,**bad},'https://example.invalid')
        invalid=self.root/'bad.pdf';invalid.write_text('not a PDF')
        with self.assertRaises(ValueError):self.store.save('TEST','local',self.meta,invalid)
        with self.assertRaises(sqlite3.IntegrityError):self.store.save('MISSING','local',self.meta,self.pdf)
        self.assertEqual(list((self.root/'manuals').iterdir()),[])
        with patch.object(ManualStore,'_backup',side_effect=OSError('backup failed')):
            with self.assertRaises(OSError):self.store.save('TEST','local',self.meta,self.pdf)
        self.assertEqual(list((self.root/'manuals').iterdir()),[])
        for path in ('../secret','/tmp/manual.pdf','manuals/../document.pdf','manuals/not-uuid/document.pdf'):
            with self.assertRaises(ValueError):manual_path(self.root,path)
    def test_changed_files_and_stale_edit(self):
        self.store.save('TEST','online',self.meta,'https://example.invalid/one')
        original=self.store.list('TEST')[0]
        self.store.save('TEST','online',{**self.meta,'title':'New title'},'https://example.invalid/two',original)
        with self.assertRaises(ValueError):self.store.save('TEST','online',self.meta,'https://example.invalid/three',original)
        with self.assertRaises(ValueError):self.store.detach(original)
        self.store.save('TEST','local',self.meta,self.pdf);row=next(r for r in self.store.list('TEST') if r['kind']=='local')
        file=manual_path(self.root,row['relative_path']);file.write_bytes(b'changed')
        with self.assertRaises(ValueError):backup_bundle(self.db,self.root/'bad.zip')
        self.assertFalse((self.root/'bad.zip').exists())
    def test_dialog_language_opening_and_detach(self):
        window=Window(DeviceStore(self.db));self.addCleanup(window.deleteLater);window.load(window.store.devices()[0])
        dialog=ManualDialog(self.store,'TEST',parent=window);self.addCleanup(dialog.deleteLater)
        dialog.inputs['title'].setText('User title');dialog.inputs['source'].setText('TEST ONLY');dialog.inputs['url'].setText('https://example.invalid/manual')
        for language in ('de','hu','en'):
            window.set_language(language);dialog.show();APP.processEvents()
            self.assertEqual(dialog.inputs['title'].text(),'User title');self.assertEqual(dialog.inputs['url'].text(),'https://example.invalid/manual')
        dialog.save();dialog.hide();window.refresh_manuals();self.assertEqual(window.manual_list.count(),1)
        window.manual_list.setCurrentRow(0)
        with patch('desktop.QDesktopServices.openUrl',return_value=True) as opened:
            window.open_manual();self.assertEqual(opened.call_args[0][0].scheme(),'https')
        window.begin_edit()
        with patch.object(QMessageBox,'question',return_value=QMessageBox.Yes):window.detach_manual()
        self.assertEqual(window.manual_list.count(),0)
        self.store.save('TEST','local',self.meta,self.pdf);window.refresh_manuals();window.manual_list.setCurrentRow(0)
        with patch('desktop.QDesktopServices.openUrl',return_value=True) as opened:
            window.open_manual();self.assertEqual(opened.call_args[0][0].scheme(),'file')
    def test_migration_export_and_database_only_snapshot(self):
        with contextlib.closing(sqlite3.connect(self.root/'old.sqlite3')) as c:
            old=(BASE/'schema.sql').read_text().split('CREATE TABLE device_manuals')[0]+'PRAGMA user_version=13;\nCOMMIT;'
            c.executescript(old);c.execute("INSERT INTO devices(device_id,name,source) VALUES('OLD','Old','TEST ONLY')");c.commit()
            before=c.execute('SELECT * FROM devices').fetchall();c.executescript((BASE/'migrations/014-manual-references.sql').read_text())
            self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before);self.assertEqual(c.execute('SELECT count(*) FROM device_manuals').fetchone()[0],0)
        self.store.save('TEST','local',self.meta,self.pdf)
        import subprocess
        r=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'export','--directory',str(self.root/'export')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        with contextlib.closing(sqlite3.connect(self.root/'sql.sqlite3')) as c:
            c.executescript((self.root/'export/inventory.sql').read_text());inventory.check(c)
            self.assertEqual(c.execute('SELECT count(*) FROM device_manuals').fetchone()[0],1)
        self.store._backup()

if __name__=='__main__':unittest.main()
