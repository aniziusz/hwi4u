"""Current OS/firmware assessments, UI, atomic edits and portable recovery."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import contextlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication,QMessageBox
from software import empty_software,load_software
from device_store import DeviceStore
from desktop import Window
from photo_files import backup_bundle
import inventory

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]
class Software(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.db=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.db)) as c:c.executescript((BASE/'schema.sql').read_text())
        self.store=DeviceStore(self.db);self.data={'device_id':'TEST','name':'Test','source':'TEST ONLY'}
    def known(self):
        return dict(os_status='recorded',os_family='linux',os_name='Proxmox VE',os_version='EXAMPLE VERSION',
                    firmware_status='recorded',firmware_version='EXAMPLE FIRMWARE',source='TEST ONLY',checked_on='2026-10-18')
    def test_save_edit_and_independent_statuses(self):
        self.store.save(self.data);row=self.store.devices()[0]
        self.assertEqual(row['_software'],empty_software())
        self.store.save({**self.data,'software':self.known()},row);row=self.store.devices()[0]
        self.assertEqual(row['_software'],self.known())
        sw=empty_software();sw.update(os_status='not_applicable',firmware_status='recorded',firmware_version='DISK TEST',source='TEST ONLY')
        self.store.save({**self.data,'software':sw},row)
        self.assertEqual(self.store.devices()[0]['_software'],sw)
        row=self.store.devices()[0];self.store.save({**self.data,'software':empty_software()},row)
        self.assertEqual(self.store.devices()[0]['_software'],empty_software())
    def test_invalid_inputs_leave_no_device(self):
        for changes in ({'source':None},{'os_family':'imaginary'},{'checked_on':'2026-02-30'},
                        {'os_status':'not_applicable'},{'os_status':'unknown'},
                        {'firmware_version':None},{'firmware_status':'unknown'},
                        {'os_family':None,'os_name':None},{'os_status':'unexpected'}):
            with self.assertRaises(ValueError,msg=str(changes)):self.store.save({**self.data,'software':{**self.known(),**changes}})
            self.assertEqual(self.store.devices(),[])
    def test_sql_constraints_and_stale_edit(self):
        self.store.save({**self.data,'software':self.known()});original=self.store.devices()[0]
        with contextlib.closing(self.store.connect()) as c:
            with self.assertRaises(sqlite3.IntegrityError):c.execute("UPDATE device_software SET checked_on='2026-02-30'")
            with self.assertRaises(sqlite3.IntegrityError):c.execute("UPDATE device_software SET source=NULL")
            with self.assertRaises(sqlite3.IntegrityError):c.execute("UPDATE device_software SET os_status='not_applicable'")
            c.execute("UPDATE device_software SET os_version='EXTERNAL TEST'");c.commit()
        with self.assertRaises(ValueError):self.store.save({**self.data,'software':self.known()},original)
        self.assertEqual(self.store.devices()[0]['_software']['os_version'],'EXTERNAL TEST')
    def test_gui_language_calendar_search_cancel(self):
        w=Window(self.store);self.addCleanup(w.deleteLater)
        for key,value in self.data.items():w.begin_edit();w.inputs[key].setText(value)
        p=w.software_panel
        p.os_status.setCurrentIndex(p.os_status.findData('recorded'))
        p.family.setCurrentIndex(p.family.findData('linux'));p.name.setText('Arch Linux');p.version.setText('Rolling TEST')
        p.source.setText('TEST ONLY');p.checked.known.setChecked(True);p.checked.editor.setDate(QDate(2026,10,18))
        before=w.values()
        for language in ('de','hu','en'):
            w.set_language(language);self.assertEqual(w.values(),before)
        w.save();self.assertEqual(self.store.devices()[0]['_software']['os_name'],'Arch Linux')
        w.search.setText('rolling');self.assertFalse(w.table.isRowHidden(0))
        w.search.setText('unknownOSname');self.assertTrue(w.table.isRowHidden(0))
        p.name.setText('unsaved')
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Discard):w.cancel()
        self.assertEqual(p.name.text(),'Arch Linux')
        p.os_status.setCurrentIndex(p.os_status.findData('not_applicable'))
        self.assertFalse(p.name.isEnabled());self.assertIsNone(p.value()['os_name'])
    def test_migration_and_export_recovery(self):
        old=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(old)) as c:
            ddl=(BASE/'schema.sql').read_text().split('CREATE TABLE os_families')[0]+'PRAGMA user_version=12;\nCOMMIT;'
            c.executescript(ddl);c.execute("INSERT INTO devices(device_id,name,source,device_type) VALUES('OLD','Old','TEST ONLY','hdd')");c.commit()
            before=c.execute('SELECT * FROM devices').fetchall();c.executescript((BASE/'migrations/013-software-properties.sql').read_text())
            self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before)
            self.assertEqual(load_software(c,'OLD'),empty_software())
            self.assertEqual(c.execute('SELECT count(*) FROM os_families').fetchone()[0],6)
        self.store.save({**self.data,'software':self.known()});bundle=backup_bundle(self.db,self.root/'bundle.zip')
        with zipfile.ZipFile(bundle) as z:
            restored=self.root/'restored.sqlite3';restored.write_bytes(z.read('hardware.sqlite3'))
            self.assertEqual(json.loads(z.read('MANIFEST.json'))['schema_version'],26)
        self.assertEqual(DeviceStore(restored).devices()[0]['_software'],self.known())
        import subprocess
        r=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'export','--directory',str(self.root/'export')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        with contextlib.closing(sqlite3.connect(self.root/'sql.sqlite3')) as c:
            c.executescript((self.root/'export/inventory.sql').read_text());inventory.check(c)
            self.assertEqual(load_software(c,'TEST'),self.known())

if __name__=='__main__':unittest.main()
