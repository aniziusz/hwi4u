"""Deletion safety and explicit UI actions; temporary databases only."""
import contextlib,json,sqlite3,zipfile
from unittest.mock import patch
from test_desktop import Desktop,APP,BASE
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import QMessageBox,QPushButton
from ui_i18n import install
from device_store import DeviceStore

class HWI4U(Desktop):
    def test_delete_preserves_other_devices_history_labels_and_backup(self):
        self.store.save(dict(device_id='P',name='parent',source='TEST ONLY',purchased_at='amazon'))
        self.store.save(dict(device_id='C',name='component',source='TEST ONLY'))
        with contextlib.closing(self.store.connect()) as c:
            c.execute("INSERT INTO component_installations(parent_device,component_device,source) VALUES('P','C','TEST ONLY')")
            c.execute("INSERT INTO network_observations(device_id,profile_json) VALUES('P','{}')")
            c.commit()
        original=next(r for r in self.store.devices() if r['device_id']=='P');label=original['short_id']
        backup=self.store.delete(original)
        self.assertEqual([r['device_id'] for r in self.store.devices()],['C'])
        with contextlib.closing(self.store.connect()) as c:
            archive=json.loads(c.execute('SELECT snapshot_json FROM deleted_devices').fetchone()[0])
            self.assertEqual(len(archive['component_installations']),1)
            self.assertEqual(len(archive['network_observations']),1)
            self.assertEqual(c.execute('SELECT count(*) FROM device_short_labels').fetchone()[0],2)
            self.assertFalse(c.execute('SELECT 1 FROM device_label_aliases WHERE short_id=?',(label,)).fetchone())
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        with zipfile.ZipFile(backup) as z:
            restored=self.root/'restore.sqlite3';restored.write_bytes(z.read('hardware.sqlite3'))
        self.assertEqual(len(DeviceStore(restored).devices()),2)
        with self.assertRaises(sqlite3.IntegrityError):self.store.save(dict(device_id='P',name='reuse',source='TEST ONLY'))
    def test_delete_failure_and_stale_edit_leave_records(self):
        self.fill();self.window.save();original=self.store.devices()[0]
        with patch('update_runtime.full_snapshot_locked',side_effect=OSError('TEST backup failure')):
            with self.assertRaises(OSError):self.store.delete(original)
        self.assertEqual(len(self.store.devices()),1)
        with contextlib.closing(self.store.connect()) as c:c.execute("UPDATE devices SET name='changed'");c.commit()
        with self.assertRaises(ValueError):self.store.delete(original)
    def test_expansion_typo_and_explicit_dialog_actions(self):
        w=self.window;install('en')
        self.assertEqual(w.windowTitle(),'HWI4U')
        w.begin_edit();w.inputs['purchased_at'].setText('amzaon');self.assertEqual(w.merchant_suggestion,'amazon')
        self.assertEqual(w.values()['purchased_at'],'amzaon');w.merchant_fix.click();self.assertEqual(w.values()['purchased_at'],'amazon')
        before=w.values()
        for section in w.sections:
            self.assertTrue(section.body.isHidden());section.header.click();self.assertFalse(section.body.isHidden());section.header.click()
        self.assertEqual(w.values(),before)
        for label,expected in [('Save changes',QMessageBox.Save),('Discard unsaved changes',QMessageBox.Discard),('Keep editing',QMessageBox.Cancel)]:
            def click(label=label):
                box=APP.activeModalWidget();buttons={b.text():b for b in box.findChildren(QPushButton)}
                self.assertEqual(set(buttons),{'Save changes','Discard unsaved changes','Keep editing'})
                self.assertTrue(all(b.toolTip() for b in buttons.values()));buttons[label].click()
            QTimer.singleShot(0,click);self.assertEqual(w.unsaved_choice(),expected)
    def test_schema17_upgrade_reserves_deleted_labels(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((BASE/'tests/fixtures/schema-017.sql').read_text());c.execute("INSERT INTO devices(device_id,name,source) VALUES('OLD','old','TEST ONLY')");c.commit()
            labels=c.execute('SELECT * FROM device_short_labels').fetchall()
            c.executescript((BASE/'migrations/018-hwi4u.sql').read_text())
            c.executescript((BASE/'migrations/019-source-library.sql').read_text())
            c.executescript((BASE/'migrations/020-network-links.sql').read_text())
            c.executescript((BASE/'migrations/021-location.sql').read_text());c.executescript((BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((BASE/'migrations/023-device-roles.sql').read_text());c.executescript((BASE/'migrations/024-device-identification.sql').read_text());c.executescript((BASE/'migrations/025-model-lifecycle.sql').read_text())
            self.assertEqual(labels,c.execute('SELECT * FROM device_short_labels').fetchall())
        self.assertIsNone(DeviceStore(db).devices()[0]['purchased_at'])

    def test_delete_confirmation_cancel_and_accept(self):
        from PySide6.QtWidgets import QDialog
        self.fill();w=self.window;w.save()
        def click(text):
            box=APP.activeModalWidget()
            next(b for b in box.findChildren(QPushButton) if b.text()==text).click()
        w.begin_edit();install('en');QTimer.singleShot(0,lambda:click('Keep device'));w.delete_device()
        self.assertEqual(len(self.store.devices()),1)
        QTimer.singleShot(0,lambda:click('Delete device'));w.delete_device()
        self.assertEqual(self.store.devices(),[])
    def test_explicit_choices_translation_preserves_data(self):
        self.fill();w=self.window;before=w.values()
        for code,labels in [('de',['Änderungen speichern','Ungespeicherte Änderungen verwerfen','Weiter bearbeiten']),('hu',['Módosítások mentése','Nem mentett módosítások elvetése','Szerkesztés folytatása'])]:
            w.set_language(code)
            def click(labels=labels):
                buttons={b.text():b for b in APP.activeModalWidget().findChildren(QPushButton)}
                self.assertEqual(set(buttons),set(labels));buttons[labels[2]].click()
            QTimer.singleShot(0,click);self.assertEqual(w.unsaved_choice(),QMessageBox.Cancel)
            self.assertEqual(w.values(),before)
        w.set_language('en')
