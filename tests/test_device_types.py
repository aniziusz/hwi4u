"""Classification editing, filtering and preservation tests on temporary data."""
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
from PySide6.QtWidgets import QApplication,QMessageBox
from device_store import DeviceStore
from desktop import Window,TypeDialog
from photo_files import backup_bundle

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]

class DeviceTypes(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.db=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.db)) as c:c.executescript((BASE/'schema.sql').read_text())
        self.store=DeviceStore(self.db)
    def test_catalogue_edit_and_references(self):
        self.assertEqual(len(self.store.groups()),12);self.assertEqual(len(self.store.types()),55)
        for kind in ('mobile phone','gaming console','dect telephone','boiler','ont','smoke detector','smoke detector hub'):
            self.assertIn(kind,[r['type_name'] for r in self.store.types()])
        data={'device_id':'TEST','name':'Test','source':'TEST ONLY','device_type':'server'}
        self.store.save(data);original=self.store.devices()[0]
        self.assertEqual(original['type_group'],'computers')
        self.store.save({**data,'name':'Edited'},original)
        self.store.save_type('Tablet','Mobile devices')
        self.store.save_type('tablet computer','computers',next(r for r in self.store.types() if r['type_name']=='tablet'))
        self.assertIn({'type_name':'tablet computer','group_name':'computers'},[{k:r[k] for k in ('type_name','group_name')} for r in self.store.types()])
        server=next(r for r in self.store.types() if r['type_name']=='server')
        self.store.save_type('physical server','computers',server)
        self.assertEqual(self.store.devices()[0]['device_type'],'physical server')
        with contextlib.closing(self.store.connect()) as c:
            with self.assertRaises(sqlite3.IntegrityError):c.execute("DELETE FROM device_types WHERE type_name='physical server'")
        with self.assertRaises(ValueError):self.store.save({**data,'device_id':'NEW','device_type':'invented'})
        with self.assertRaises(sqlite3.IntegrityError):self.store.save_type('physical server','other')
    def test_gui_groups_filters_and_manager(self):
        w=Window(self.store);self.addCleanup(w.deleteLater)
        for k,v in (('device_id','TEST'),('name','Server'),('source','TEST ONLY')):w.begin_edit();w.inputs[k].setText(v)
        w.type_group.setCurrentIndex(w.type_group.findData('networking'))
        self.assertGreaterEqual(w.inputs['device_type'].findData('ont'),0)
        self.assertEqual(w.inputs['device_type'].findData('server'),-1)
        with patch.object(QMessageBox,'warning') as warning:
            w.save();self.assertTrue(warning.called)
        w.begin_edit();w.inputs['device_type'].setCurrentIndex(w.inputs['device_type'].findData('ont'));w.save()
        self.assertEqual(self.store.devices()[0]['device_type'],'ont')
        w.group_filter.setCurrentIndex(w.group_filter.findData('computers'));self.assertTrue(w.table.isRowHidden(0))
        w.group_filter.setCurrentIndex(w.group_filter.findData('networking'));self.assertFalse(w.table.isRowHidden(0))
        w.type_filter.setCurrentIndex(w.type_filter.findData('router'));self.assertTrue(w.table.isRowHidden(0))
        w.type_filter.setCurrentIndex(w.type_filter.findData('ont'));self.assertFalse(w.table.isRowHidden(0))
        d=TypeDialog(self.store);self.addCleanup(d.deleteLater)
        d.name.setText('Custom equipment');d.group.setCurrentText('custom group');d.save()
        self.assertIn({'type_name':'custom equipment','group_name':'custom group'},[{k:r[k] for k in ('type_name','group_name')} for r in self.store.types()])
    def test_migration_null_and_complete_backup(self):
        old=self.root/'old.sqlite3'
        # Reconstruct the preceding schema using DDL only, never user records.
        ddl=(BASE/'schema.sql').read_text().split('CREATE TABLE connection_options')[0]+'PRAGMA user_version = 10;\nCOMMIT;'
        start=ddl.index('CREATE TABLE device_type_groups');end=ddl.index('CREATE TABLE devices')
        ddl=ddl[:start]+ddl[end:]
        ddl=ddl.replace(' device_type TEXT REFERENCES device_types(type_name) ON UPDATE CASCADE ON DELETE RESTRICT,','')
        ddl=ddl.replace('CREATE INDEX devices_type ON devices(device_type);','').replace('PRAGMA user_version = 11;','PRAGMA user_version = 10;')
        with contextlib.closing(sqlite3.connect(old)) as c:
            c.executescript(ddl)
            c.execute("INSERT INTO devices(device_id,name,source,current_state) VALUES('MIGRATION-TEST','Test','TEST ONLY','in use')");c.commit()
            before={r[1] for r in c.execute('PRAGMA table_info(devices)')}
            c.executescript((BASE/'migrations/011-device-types.sql').read_text())
            row=c.execute("SELECT device_type,current_state FROM devices WHERE device_id='MIGRATION-TEST'").fetchone()
            self.assertEqual(row,(None,'in use'));self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            c.executescript((BASE/'migrations/012-connectivity.sql').read_text())
            c.executescript((BASE/'migrations/013-software-properties.sql').read_text())
            c.executescript((BASE/'migrations/014-manual-references.sql').read_text())
            c.executescript((BASE/'migrations/015-usability-refinements.sql').read_text())
            c.executescript((BASE/'migrations/016-type-random-short-labels.sql').read_text())
            c.executescript((BASE/'migrations/017-network-identities.sql').read_text())
            c.executescript((BASE/'migrations/018-hwi4u.sql').read_text())
            c.executescript((BASE/'migrations/019-source-library.sql').read_text())
            c.executescript((BASE/'migrations/020-network-links.sql').read_text())
            c.executescript((BASE/'migrations/021-location.sql').read_text());c.executescript((BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((BASE/'migrations/023-device-roles.sql').read_text());c.executescript((BASE/'migrations/024-device-identification.sql').read_text());c.executescript((BASE/'migrations/025-model-lifecycle.sql').read_text());c.executescript((BASE/'migrations/026-device-tags.sql').read_text())
        backup=backup_bundle(old,self.root/'bundle.zip')
        with zipfile.ZipFile(backup) as z:
            self.assertEqual(json.loads(z.read('MANIFEST.json'))['schema_version'],26)
        data={'device_id':'TEST','name':'Test','source':'TEST ONLY','device_type':'boiler'};self.store.save(data)
        import subprocess
        r=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'export','--directory',str(self.root/'export')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        with contextlib.closing(sqlite3.connect(self.root/'restore.sqlite3')) as c:
            c.executescript((self.root/'export/inventory.sql').read_text())
            self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            self.assertEqual(c.execute('SELECT device_type FROM devices').fetchone()[0],'boiler')

if __name__=='__main__':unittest.main()
