"""Schema-14 upgrade and save workflow regressions; never uses the live database."""
import contextlib
import copy
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_desktop
from PySide6.QtWidgets import QMessageBox,QPushButton
from PySide6.QtCore import Qt
from device_store import DeviceStore
from connectivity import empty_profile,missing_sources,save_profile
from desktop import Window
import inventory

BASE=test_desktop.BASE
class Usability(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_short_id_allocation_rename_and_cli(self):
        one={'name':'first','source':'TEST ONLY'};self.store.save(one)
        first=self.store.devices()[0];self.assertRegex(first['short_id'],r'^UN[0-9]{5}$')
        self.store.save({**one,'name':'renamed'},first)
        two={'name':'second','source':'TEST ONLY'};self.store.save(two)
        self.assertEqual(len({r['short_id'] for r in self.store.devices()}),2)
        self.assertEqual(next(r for r in self.store.devices() if r['short_id']==first['short_id'])['device_id'],one['device_id'])
        result=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'show',first['short_id']],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertIn('renamed',result.stdout)
        with contextlib.closing(self.store.connect()) as c:
            with self.assertRaises(sqlite3.IntegrityError):c.execute('UPDATE device_short_labels SET number=99')
    def test_unsourced_connectivity_saves_and_warns(self):
        w=self.window;w.inputs['name'].setText('test');w.inputs['source'].setText('TEST ONLY')
        panel=w.connection_panels['interface'];panel.supported.setCurrentIndex(panel.supported.findData('recorded'))
        panel.table.item(panel.options.index('m.2'),1).setCheckState(Qt.Checked)
        self.assertIn('warning',panel.warning.text().lower());self.assertTrue(w.save())
        saved=self.store.devices()[0];self.assertIsNone(saved['_connectivity']['interface']['source'])
        self.assertEqual(missing_sources(saved['_connectivity']),['interface'])
        with contextlib.closing(self.store.connect()) as c:inventory.check(c)
        self.assertIn('Warning',w.status.text())
    def test_save_discard_cancel_prompt_and_failed_save(self):
        w=self.window;w.inputs['name'].setText('test');w.inputs['source'].setText('TEST ONLY')
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Save):w.new()
        self.assertEqual(len(self.store.devices()),1);self.assertIsNone(w.original)
        w.inputs['name'].setText('incomplete')
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Save),patch.object(QMessageBox,'warning'):
            w.new();self.assertEqual(w.inputs['name'].text(),'incomplete')
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Cancel):self.assertFalse(w.discard_ok())
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Discard):self.assertTrue(w.discard_ok())
        self.assertGreaterEqual(sum(b.text()=='Save device' for b in w.findChildren(QPushButton)),2)
    def test_migration_preserves_history_and_handles_assigned_knx(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((BASE/'tests/fixtures/schema-014.sql').read_text())
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('old-parent','parent','TEST ONLY'),('old-child','child','TEST ONLY')")
            c.execute("INSERT INTO component_installations(parent_device,component_device,source) VALUES('old-parent','old-child','TEST ONLY')")
            p=empty_profile();p['protocol'].update(supported_status='recorded',usage_status='recorded',supported=['knx'],in_use=['knx'],source='TEST ONLY')
            save_profile(c,'old-parent',p);c.commit()
            before=c.execute('SELECT * FROM devices').fetchall();links=c.execute('SELECT * FROM component_installations').fetchall()
            c.executescript((BASE/'migrations/015-usability-refinements.sql').read_text())
            self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before)
            self.assertEqual(c.execute('SELECT * FROM component_installations').fetchall(),links)
            self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            self.assertEqual(c.execute('SELECT count(*) FROM device_numbers').fetchone()[0],2)
            self.assertEqual(c.execute("SELECT supported_status,usage_status FROM device_connectivity WHERE kind='protocol'").fetchone(),('unknown','unknown'))
            self.assertIsNone(c.execute("SELECT 1 FROM connection_options WHERE value='knx'").fetchone())
            c.execute("INSERT INTO device_connectivity(device_id,kind,supported_status,usage_status) VALUES('old-child','interface','none','none')")
            c.commit();inventory.check(c)
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((BASE/'migrations/016-type-random-short-labels.sql').read_text())
            c.executescript((BASE/'migrations/017-network-identities.sql').read_text())
            c.executescript((BASE/'migrations/018-hwi4u.sql').read_text())
            c.executescript((BASE/'migrations/019-source-library.sql').read_text())
            c.executescript((BASE/'migrations/020-network-links.sql').read_text())
            c.executescript((BASE/'migrations/021-location.sql').read_text());c.executescript((BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((BASE/'migrations/023-device-roles.sql').read_text());c.executescript((BASE/'migrations/024-device-identification.sql').read_text())
        self.assertEqual(len(DeviceStore(db).devices()),2)
    def test_catalogues_and_language_preserve_short_id(self):
        self.assertIn('freebsd',self.store.os_families())
        for value in ('m.2','sata','pcie','so-dimm','hdmi','displayport'):self.assertIn(value,self.store.connection_options('interface'))
        self.assertNotIn('knx',self.store.connection_options('protocol'))
        data={'name':'test','source':'TEST ONLY'};self.store.save(data)
        self.window.reload();self.window.load(self.store.devices()[0])
        label=self.window.short_id.text();self.assertRegex(label,r'^UN[0-9]{5}$');self.assertTrue(self.window.short_id.isReadOnly())
        for language in ('de','hu','en'):
            self.window.set_language(language);self.assertEqual(self.window.short_id.text(),label)
    def test_save_during_row_switch_keeps_intended_target(self):
        z={'name':'zulu','source':'TEST ONLY'};a={'name':'alpha','source':'TEST ONLY'}
        self.store.save(z);self.store.save(a)
        w=self.window;w.reload();w.load(next(r for r in w.rows if r['device_id']==z['device_id']))
        w.inputs['name'].setText('aardvark')
        target=next(n for n,r in enumerate(w.rows) if r['device_id']==a['device_id'])
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Save):w.table.setCurrentCell(target,0)
        self.assertEqual(w.original['device_id'],a['device_id'])
        self.assertEqual(next(r for r in self.store.devices() if r['device_id']==z['device_id'])['name'],'aardvark')
    def test_warning_translation_and_version_help(self):
        w=self.window;p=w.connection_panels['interface'];p.supported.setCurrentIndex(p.supported.findData('none'))
        for language,word in [('de','Warnung'),('hu','Figyelem'),('en','Warning')]:
            w.set_language(language);self.assertIn(word,p.warning.text())
        with patch.object(QMessageBox,'information') as message:
            w.software_panel.show_version_help()
            self.assertIn('System Information',message.call_args.args[2])
