"""Staged-release isolation and live SQLite lock/rollback protection."""
import contextlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
import zipfile
from unittest.mock import patch
import test_desktop
from update_runtime import publish,published,verify_release,prepare_database,UPDATE_EXIT
from PySide6.QtWidgets import QApplication,QMessageBox
from desktop import Window
from device_store import DeviceStore

BASE=test_desktop.BASE
class Releases(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('desktop.py','ui_i18n.py','schema.sql','inventory.py','connectivity.py','software.py','manual_store.py','update_runtime.py','LICENSE-desktop.txt'):
            shutil.copyfile(BASE/name,self.root/name)
        shutil.copytree(BASE/'migrations',self.root/'migrations')
        self.old=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.old)) as c:
            c.executescript((BASE/'tests/fixtures/schema-014.sql').read_text())
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('REAL-TEST','preserve','TEST ONLY')");c.commit()
    def stage(self):return publish(self.root,run_tests=False,channel='production')
    def test_publishing_isolated_immutable_and_no_database_write(self):
        release=self.stage();before=self.old.read_bytes()
        (self.root/'desktop.py').write_text('# next release\n')
        self.assertNotEqual((release/'desktop.py').read_bytes(),(self.root/'desktop.py').read_bytes())
        self.assertEqual(self.old.read_bytes(),before)
        next_release=self.stage();self.assertNotEqual(release,next_release)
        self.assertEqual(published(self.root)[0],next_release)
        (next_release/'desktop.py').write_text('# unexpected tampering')
        with self.assertRaises(ValueError):verify_release(next_release)
    def test_bad_source_cannot_replace_published_release(self):
        first=self.stage();(self.root/'desktop.py').write_text('bad syntax !')
        with self.assertRaises(SyntaxError):self.stage()
        self.assertEqual(published(self.root)[0],first)
    def test_db_browser_open_read_connection_does_not_require_close(self):
        release=self.stage()
        with contextlib.closing(sqlite3.connect(self.old)) as browser:
            self.assertEqual(browser.execute('SELECT count(*) FROM devices').fetchone()[0],1)
            backup=prepare_database(self.old,release)
            self.assertEqual(browser.execute('PRAGMA user_version').fetchone()[0],24)
            self.assertEqual(browser.execute('SELECT name FROM devices').fetchone()[0],'preserve')
        with zipfile.ZipFile(backup) as z:
            snapshot=self.root/'before.sqlite3';snapshot.write_bytes(z.read('hardware.sqlite3'))
            with contextlib.closing(sqlite3.connect(snapshot)) as c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],14)
        self.assertRegex(DeviceStore(self.old).devices()[0]['short_id'],r'^UN[0-9]{5}$')
    def test_busy_writer_defers_and_retry_preserves_edits(self):
        release=self.stage()
        with contextlib.closing(sqlite3.connect(self.old)) as browser:
            browser.execute('BEGIN IMMEDIATE');browser.execute("UPDATE devices SET name='pending edit'")
            with self.assertRaises(sqlite3.OperationalError):prepare_database(self.old,release)
            self.assertEqual(browser.execute('PRAGMA user_version').fetchone()[0],14)
            browser.commit()
            prepare_database(self.old,release)
            self.assertEqual(browser.execute('SELECT name FROM devices').fetchone()[0],'pending edit')
    def test_failed_migration_rolls_back_without_overwrite(self):
        migration=self.root/'migrations/015-usability-refinements.sql'
        migration.write_text(migration.read_text().replace('PRAGMA user_version=15;','INSERT INTO no_such_table VALUES(1);\nPRAGMA user_version=15;'))
        release=self.stage()
        with self.assertRaises(sqlite3.OperationalError):prepare_database(self.old,release)
        with contextlib.closing(sqlite3.connect(self.old)) as c:
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],14)
            self.assertEqual(c.execute('SELECT name FROM devices').fetchone()[0],'preserve')
            self.assertFalse(c.execute("SELECT name FROM sqlite_master WHERE name='device_numbers'").fetchall())
    def test_missing_attachment_prevents_migration(self):
        release=self.stage()
        with contextlib.closing(sqlite3.connect(self.old)) as c:
            c.execute("INSERT INTO device_manuals(reference_id,device_id,title,kind,relative_path,original_name,sha256,source) VALUES('abcd','REAL-TEST','missing','local','manuals/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/document.pdf','missing.pdf','0000000000000000000000000000000000000000000000000000000000000000','TEST ONLY')");c.commit()
        with self.assertRaises(OSError):prepare_database(self.old,release)
        with contextlib.closing(sqlite3.connect(self.old)) as c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],14)

    def test_open_read_transaction_defers_without_losing_schema(self):
        release=self.stage()
        with contextlib.closing(sqlite3.connect(self.old)) as browser:
            browser.execute('BEGIN');browser.execute('SELECT * FROM devices').fetchall()
            with self.assertRaises(sqlite3.OperationalError):prepare_database(self.old,release)
            self.assertEqual(browser.execute('PRAGMA user_version').fetchone()[0],14)
            browser.rollback()
            prepare_database(self.old,release)
            self.assertEqual(browser.execute('PRAGMA user_version').fetchone()[0],24)
    def test_migration_backup_includes_local_manual_and_hashes(self):
        import hashlib
        release=self.stage();folder=self.root/'manuals'/('a'*32);folder.mkdir(parents=True)
        data=b'%PDF-1.4 TEST ONLY';(folder/'document.pdf').write_bytes(data)
        with contextlib.closing(sqlite3.connect(self.old)) as c:
            c.execute("INSERT INTO device_manuals(reference_id,device_id,title,kind,relative_path,original_name,sha256,source) VALUES(?,?,'test','local',?,'test.pdf',?,'TEST ONLY')",('a'*32,'REAL-TEST','manuals/'+('a'*32)+'/document.pdf',hashlib.sha256(data).hexdigest()));c.commit()
        backup=prepare_database(self.old,release)
        with zipfile.ZipFile(backup) as z:
            manifest=json.loads(z.read('MANIFEST.json'))['sha256']
            for name,expected in manifest.items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),expected)
            self.assertEqual(z.read('manuals/'+('a'*32)+'/document.pdf'),data)

class UpdateUI(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_update_available_save_cancel_and_exit_request(self):
        w=self.window;root=self.root
        folder=root/'.runtime';folder.mkdir();(folder/'current.json').write_text(json.dumps({'release_id':'new'}))
        with patch.dict(os.environ,{'INVENTORY_PROJECT_ROOT':str(root),'INVENTORY_RELEASE_ID':'old'}):
            w.check_update();self.assertFalse(w.update_button.isHidden())
            w.inputs['name'].setText('pending');w.inputs['source'].setText('TEST ONLY')
            with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Cancel),patch.object(QApplication,'exit') as exit_call:
                w.apply_update();exit_call.assert_not_called()
            with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Save),patch.object(QApplication,'exit') as exit_call:
                w.apply_update();exit_call.assert_called_once_with(UPDATE_EXIT)
            self.assertEqual(self.store.devices()[0]['name'],'pending')

class Supervision(unittest.TestCase):
    setUp=Releases.setUp
    stage=Releases.stage
    def test_launcher_returns_to_old_release_when_update_is_busy(self):
        from update_runtime import supervise,atomic_json
        import subprocess
        old=self.stage();(self.root/'desktop.py').write_text('# tested next version\n');new=self.stage()
        # Run the old published release first, then publish the next one during its session.
        atomic_json(self.root/'.runtime/current.json',{'release_id':old.name})
        launches=[]
        def run(command,**kwargs):
            if command[1].endswith('run_desktop.py'):
                if str(new) in command[1]:return subprocess.CompletedProcess(command,1,stderr='database is locked',stdout='')
                return subprocess.CompletedProcess(command,0,stderr='',stdout='')
            launches.append(command)
            if len(launches)==1:
                atomic_json(self.root/'.runtime/current.json',{'release_id':new.name})
                return subprocess.CompletedProcess(command,UPDATE_EXIT)
            self.assertIn('database is locked',kwargs['env']['INVENTORY_UPDATE_ERROR'])
            return subprocess.CompletedProcess(command,0)
        with patch('update_runtime.subprocess.run',side_effect=run):
            self.assertEqual(supervise(self.root,[]),0)
        self.assertIn(str(old),launches[0][1]);self.assertIn(str(old),launches[1][1])
