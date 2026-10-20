"""User-facing edit protection, visibility, menus and pending-data preservation."""
from unittest.mock import patch
import unittest
import test_desktop
from PySide6.QtCore import Qt,QDate
from PySide6.QtTest import QTest
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication,QMessageBox,QPushButton
from desktop import Window,OptionalDate
from source_ui import SourceLibrary
from source_store import SourceStore


class EditorModes(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp

    def saved(self):
        self.store.save(dict(name='Fictional protected device',source='FICTIONAL TEST',
                             serial_number='00042',purchase_date='2026-01-02'))
        self.window.reload();self.window.load(self.window.rows[0])
        return self.window

    def editor(self):
        w=self.saved();e=w.open_device_editor(0)
        self.addCleanup(lambda:(setattr(e,'skip_close_prompt',True),e.close()))
        return e

    def test_existing_readonly_then_explicit_edit_save_and_cancel(self):
        w=self.saved();w.show();QApplication.processEvents()
        self.assertFalse(w.editing);self.assertTrue(w.inputs['name'].isReadOnly())
        self.assertFalse(w.inputs['current_state'].isEnabled())
        self.assertFalse(w.actions['save'].isEnabled());self.assertTrue(w.save_button.isHidden())
        before=self.db.read_bytes();w.inputs['name'].setFocus();QTest.keyClicks(w.inputs['name'],'UNWANTED')
        self.assertEqual(w.inputs['name'].text(),'Fictional protected device')
        self.assertFalse(w.save());self.assertEqual(self.db.read_bytes(),before)
        w.edit_button.click();self.assertTrue(w.editing);self.assertFalse(w.inputs['name'].isReadOnly())
        w.inputs['name'].setText('Explicit change');w.save_button.click()
        self.assertFalse(w.editing);self.assertEqual(self.store.devices()[0]['name'],'Explicit change')
        w.begin_edit();w.inputs['name'].setText('Discard this')
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Discard):w.cancel_button.click()
        self.assertFalse(w.editing);self.assertEqual(w.inputs['name'].text(),'Explicit change')

    def test_basic_details_hidden_values_and_failed_save_reveal(self):
        w=self.saved();w.begin_edit()
        self.assertTrue(w.inputs['serial_number'].isHidden())
        w.set_details(True);self.assertFalse(w.inputs['serial_number'].isHidden())
        w.inputs['serial_number'].setText('00099');w.inputs['purchase_price'].setText('12.34')
        before=w.values();w.set_details(False);self.assertEqual(w.values(),before)
        with patch.object(w,'error') as error:self.assertFalse(w.save());error.assert_called_once()
        self.assertTrue(w.editing);self.assertTrue(w.details_mode)
        self.assertEqual(w.inputs['serial_number'].text(),'00099')

    def test_full_window_adaptive_tiles_and_footer(self):
        e=self.editor();self.assertFalse(e.editing);self.assertFalse(e.details_mode)
        self.assertTrue(e.workspace.cards['purchase'].isHidden())
        self.assertFalse(e.workspace.cards['evidence'].isHidden())
        self.assertIs(e.action_bar.parentWidget(),e.centralWidget())
        self.assertIsNot(e.save_button.parentWidget(),e.workspace.footer)
        self.assertTrue(e.workspace.items['network'].isHidden())
        e.actions['details'].trigger();QApplication.processEvents()
        self.assertFalse(e.workspace.cards['purchase'].isHidden())
        self.assertFalse(e.inputs['purchase_date'].isHidden())
        self.assertFalse(e.workspace.items['network'].isHidden())
        self.assertFalse(e.actions['columns'].isEnabled())

    def test_lifecycle_collapse_preserves_data_and_exposes_attention(self):
        w=self.window;w.set_details(True);s=w.lifecycle_section
        w.inputs['purchase_date'].known.setChecked(True);w.inputs['purchase_date'].editor.setDate(QDate(2026,1,2))
        before=w.values();self.assertTrue(s.body.isHidden())
        for language in ('de','hu','en'):
            w.set_language(language);s.header.click();self.assertFalse(s.body.isHidden())
            s.header.click();self.assertTrue(s.body.isHidden());self.assertEqual(w.values(),before)
        w.lifecycle_panel.feedback.setText('Fictional attention');w.lifecycle_panel.warning_changed.emit()
        self.assertIn('attention',s.header.text());w.set_details(False)
        self.assertIn('attention',w.mode_hint.text())

    def test_mutating_attachments_lifecycle_sources_are_protected(self):
        w=self.saved();before=self.db.read_bytes()
        self.assertFalse(w.add_photo_button.isEnabled());self.assertFalse(w.add_manual_button.isEnabled())
        self.assertTrue(w.lifecycle_panel.read_only);self.assertTrue(w.location_panel.read_only)
        with patch('desktop.QFileDialog.getOpenFileName') as picker,patch.object(w.photo_store,'detach') as detach:
            w.add_photo();w.detach_photo();picker.assert_not_called();detach.assert_not_called()
        sid=SourceStore(self.db).save(dict(kind='observation',title='Fictional evidence',body='TEST',evidence_status='user_reported'))
        dialog=SourceLibrary(w.source_store,OptionalDate,[sid],w.original['device_id'],w,read_only=True)
        self.addCleanup(dialog.deleteLater)
        self.assertEqual(dialog.list.count(),1)
        self.assertFalse(dialog.list.item(0).flags() & Qt.ItemIsUserCheckable)
        self.assertTrue(w.source_selectors['device'].button.isEnabled())
        self.assertTrue(w.source_selectors['device'].read_only)
        w.begin_edit();self.assertFalse(w.source_selectors['device'].read_only)

    def test_classic_menus_actions_keyboard_and_language(self):
        w=self.saved();self.assertEqual([a.text() for a in w.menuBar().actions()],['File','Edit','View','Tools','Help'])
        self.assertEqual(w.actions['save'].shortcut().toString(), QKeySequence(QKeySequence.Save).toString())
        self.assertTrue(w.language_menu.menuAction() in w.menuBar().actions()[3].menu().actions())
        before=w.values()
        for language,first in [('de','Datei'),('hu','Fájl'),('en','File')]:
            w.set_language(language);self.assertEqual(w.menuBar().actions()[0].text(),first)
            self.assertFalse(w.actions['save'].isEnabled());self.assertEqual(w.values(),before)
        w.actions['edit'].trigger();self.assertTrue(w.editing)

    def test_new_record_and_explicit_cancel_return_to_view_mode(self):
        w=self.window;self.assertTrue(w.editing)
        w.inputs['name'].setText('Fictional new entry');w.inputs['source'].setText('TEST')
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Cancel):w.cancel()
        self.assertTrue(w.editing);self.assertEqual(w.inputs['name'].text(),'Fictional new entry')
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Discard):w.cancel()
        self.assertFalse(w.editing);self.assertFalse(self.store.devices())
        w.actions['new'].trigger();self.assertTrue(w.editing)


if __name__=='__main__':unittest.main()
