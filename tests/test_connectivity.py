"""Connectivity associations, sourced assessments, Qt controls and migrations."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import contextlib
import copy
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
from PySide6.QtCore import Qt
from connectivity import empty_profile,save_profile,load_connectivity,audit
from device_store import DeviceStore
from desktop import Window,ConnectionDialog
from photo_files import backup_bundle
import inventory

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]

class Connectivity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.db=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.db)) as c:c.executescript((BASE/'schema.sql').read_text())
        self.store=DeviceStore(self.db)
        self.data={'device_id':'TEST','name':'Test','source':'TEST ONLY'}
    def known(self):
        p=empty_profile()
        p['interface'].update(supported_status='recorded',usage_status='recorded',supported=['ethernet','wi-fi'],in_use=['ethernet'],source='TEST ONLY',assessed_on='2026-10-18')
        p['protocol'].update(supported_status='recorded',usage_status='none',supported=['modbus tcp','mqtt'],source='TEST ONLY')
        return p
    def test_unknown_none_and_multiple_choices(self):
        self.store.save(self.data)
        self.assertEqual(self.store.devices()[0]['_connectivity'],empty_profile())
        original=self.store.devices()[0];p=self.known()
        self.store.save({**self.data,'connectivity':p},original)
        saved=self.store.devices()[0];self.assertEqual(saved['_connectivity'],p)
        # None and unknown are distinct even when both have no checked choices.
        p['interface'].update(supported_status='none',usage_status='none',supported=[],in_use=[])
        self.store.save({**self.data,'connectivity':p},saved)
        saved=self.store.devices()[0];self.assertEqual(saved['_connectivity']['interface']['supported_status'],'none')
        p['interface']=empty_profile()['interface']
        self.store.save({**self.data,'connectivity':p},saved)
        self.assertEqual(self.store.devices()[0]['_connectivity']['interface']['supported_status'],'unknown')
    def test_validation_is_atomic(self):
        for bad in ('unsupported active','empty recorded','invalid choice','invalid date','none support with usage'):
            p=self.known()
            if bad=='missing source':p['interface']['source']=None
            elif bad=='unsupported active':p['interface']['in_use']=['bluetooth']
            elif bad=='empty recorded':p['interface']['supported']=[]
            elif bad=='invalid choice':p['interface']['supported']=['invented']
            elif bad=='invalid date':p['interface']['assessed_on']='2026-02-30'
            else:p['interface']['supported_status']='none'
            with self.assertRaises(ValueError,msg=bad):self.store.save({**self.data,'connectivity':p})
            self.assertEqual(self.store.devices(),[])
    def test_gui_checkbox_rules_and_discard(self):
        w=Window(self.store);self.addCleanup(w.deleteLater)
        for k,v in self.data.items():w.inputs[k].setText(v)
        panel=w.connection_panels['interface']
        panel.supported.setCurrentIndex(panel.supported.findData('recorded'));panel.usage.setCurrentIndex(panel.usage.findData('recorded'))
        panel.source.setText('TEST ONLY')
        for value in ('ethernet','wi-fi'):
            n=panel.options.index(value);panel.table.item(n,1).setCheckState(Qt.Checked)
        panel.table.item(panel.options.index('ethernet'),2).setCheckState(Qt.Checked)
        w.save();self.assertEqual(self.store.devices()[0]['_connectivity']['interface']['in_use'],['ethernet'])
        panel.table.item(panel.options.index('wi-fi'),2).setCheckState(Qt.Checked)
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Discard):w.cancel()
        self.assertEqual(panel.value()['in_use'],['ethernet'])
        panel.supported.setCurrentIndex(panel.supported.findData('none'))
        self.assertEqual(panel.value()['usage_status'],'none');self.assertEqual(panel.value()['supported'],[])
        dialog=ConnectionDialog(self.store);self.addCleanup(dialog.deleteLater)
        dialog.name.setText('Custom Radio');dialog.save()
        self.assertIn('custom radio',self.store.connection_options('interface'))
    def test_catalogue_rename_conflict_and_sql_guards(self):
        self.store.save({**self.data,'connectivity':self.known()});original=self.store.devices()[0]
        self.store.save_connection_option('interface','wired ethernet','ethernet')
        updated=self.store.devices()[0]
        self.assertIn('wired ethernet',updated['_connectivity']['interface']['supported'])
        self.assertEqual(updated['_connectivity']['interface']['in_use'],['wired ethernet'])
        with self.assertRaises(ValueError):self.store.save({**self.data,'connectivity':self.known()},original)
        with contextlib.closing(self.store.connect()) as c:
            with self.assertRaises(sqlite3.IntegrityError):c.execute("DELETE FROM connection_options WHERE kind='interface' AND value='wired ethernet'")
            with self.assertRaises(sqlite3.IntegrityError):c.execute("INSERT INTO device_connections(device_id,kind,value,in_use) VALUES('TEST','protocol','matter',1)")
            with self.assertRaises(sqlite3.IntegrityError):c.execute("UPDATE device_connectivity SET supported_status='unknown' WHERE kind='interface'")
    def test_stale_assessment_and_backup_restore(self):
        self.store.save({**self.data,'connectivity':self.known()});original=self.store.devices()[0]
        with contextlib.closing(self.store.connect()) as c:
            c.execute("UPDATE device_connectivity SET source='EXTERNAL TEST' WHERE device_id='TEST' AND kind='interface'");c.commit()
        with self.assertRaises(ValueError):self.store.save({**self.data,'connectivity':self.known()},original)
        bundle=backup_bundle(self.db,self.root/'bundle.zip')
        with zipfile.ZipFile(bundle) as z:
            restored=self.root/'restored.sqlite3';restored.write_bytes(z.read('hardware.sqlite3'))
        self.assertEqual(DeviceStore(restored).devices()[0]['_connectivity']['interface']['source'],'EXTERNAL TEST')
        import subprocess
        r=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'export','--directory',str(self.root/'export')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        with contextlib.closing(sqlite3.connect(self.root/'sql.sqlite3')) as c:
            c.executescript((self.root/'export/inventory.sql').read_text());inventory.check(c)
            self.assertEqual(load_connectivity(c,'TEST')['interface']['in_use'],['ethernet'])
    def test_migration_and_audit(self):
        with contextlib.closing(sqlite3.connect(self.root/'old.sqlite3')) as c:
            old=(BASE/'schema.sql').read_text().split('CREATE TABLE connection_options')[0]+'PRAGMA user_version=11;\nCOMMIT;'
            c.executescript(old);c.execute("INSERT INTO devices(device_id,name,source,device_type) VALUES('OLD','Old','TEST ONLY','server')");c.commit()
            c.executescript((BASE/'migrations/012-connectivity.sql').read_text())
            self.assertEqual(c.execute('SELECT device_type FROM devices').fetchone()[0],'server')
            self.assertEqual(load_connectivity(c,'OLD'),empty_profile())
            self.assertEqual(c.execute('SELECT count(*) FROM connection_options').fetchone()[0],18)
            c.execute("INSERT INTO device_connectivity(device_id,kind,supported_status,usage_status,source) VALUES('OLD','interface','recorded','unknown','TEST ONLY')");c.commit()
            with self.assertRaises(ValueError):audit(c)

if __name__=='__main__':unittest.main()
