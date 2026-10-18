"""One-device windows share save validation but never overwrite another view's edits."""
import os,unittest
from unittest.mock import patch
import test_desktop
from desktop import Window
from PySide6.QtCore import QEvent,Qt
from PySide6.QtWidgets import QApplication,QMessageBox

class ExpandedEditor(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def prepare(self):
        self.store.save(dict(name='alpha',source='FICTIONAL TEST'));self.store.save(dict(name='zulu',source='FICTIONAL TEST'))
        self.window.reload();self.window.load(self.window.rows[0]);self.addCleanup(self.cleanup_editors)
        return self.window
    def cleanup_editors(self):
        for editor in list(self.window.editors.values()):editor.skip_close_prompt=True;editor.close()
        QApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    def test_double_click_opens_one_device_maximized_and_retains_quick_edit(self):
        w=self.prepare();w.table.itemDoubleClicked.emit(w.table.item(0,1));editor=w.editors[w.rows[0]['device_id']]
        self.assertTrue(editor.isMaximized());self.assertTrue(editor.table.isHidden());self.assertTrue(editor.filter_bar.isHidden());self.assertFalse(w.table.isHidden())
        self.assertEqual(editor.original['device_id'],w.original['device_id']);self.assertIs(w.open_device_editor(0),editor)
        editor.inputs['name'].setText('edited in big window');self.assertTrue(editor.save());self.assertEqual(w.inputs['name'].text(),'edited in big window')
        self.assertEqual(len(w.editors),1);before=editor.original['device_id'];editor.refresh();self.assertEqual(editor.original['device_id'],before)
    def test_pending_quick_edits_preserved_and_stale_save_rejected(self):
        w=self.prepare();editor=w.open_device_editor(0)
        w.inputs['name'].setText('unsaved quick edit');pending=w.values();editor.inputs['name'].setText('saved big edit');self.assertTrue(editor.save())
        self.assertEqual(w.values(),pending)
        with patch.object(w,'error') as error:self.assertFalse(w.save());error.assert_called_once()
        self.assertEqual(self.store.devices()[0]['name'],'saved big edit')
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Discard):w.refresh()
        w.load(next(r for r in w.rows if r['device_id']==editor.bound_device_id));self.assertEqual(w.inputs['name'].text(),'saved big edit')
    def test_open_cancel_then_saved_row_reordering_matches_uuid(self):
        w=self.prepare();wanted=w.rows[0]['device_id'];w.inputs['name'].setText('zzzz')
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Cancel):self.assertIsNone(w.open_device_editor(0))
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Save):editor=w.open_device_editor(0)
        self.assertEqual(editor.bound_device_id,wanted);self.assertEqual(editor.inputs['name'].text(),'zzzz')
    def test_close_main_or_update_checks_every_editor(self):
        w=self.prepare();editor=w.open_device_editor(0);editor.inputs['name'].setText('pending in editor')
        with patch.object(editor,'unsaved_choice',return_value=QMessageBox.Cancel):
            self.assertFalse(w.close());self.assertIn(editor.bound_device_id,w.editors)
            with patch.dict(os.environ,{'INVENTORY_RELEASE_ID':'old'}),patch.object(QApplication,'exit') as exit_call:
                w.apply_update();exit_call.assert_not_called()
        with patch.object(editor,'unsaved_choice',return_value=QMessageBox.Save):self.assertTrue(editor.close())
        self.assertEqual(next(r for r in self.store.devices() if r['device_id']==editor.bound_device_id)['name'],'pending in editor')
    def test_delete_elsewhere_disables_expanded_form_instead_of_creating_device(self):
        w=self.prepare();editor=w.open_device_editor(0);row=dict(w.original);self.store.delete(row);w.device_changed.emit(row['device_id'])
        self.assertFalse(editor.form_scroll.isEnabled());self.assertFalse(editor.toolbar_buttons['Save device'].isEnabled());self.assertEqual(len(self.store.devices()),1)
    def test_language_change_keeps_both_pending_forms(self):
        w=self.prepare();editor=w.open_device_editor(0);editor.inputs['name'].setText('Őrült büro');pending=editor.values()
        for lang in ('de','hu','en'):
            w.set_language(lang);self.assertEqual(editor.values(),pending);self.assertTrue(editor.language_actions[lang].isChecked())
    def test_reopen_before_old_deletion_does_not_remove_new_editor(self):
        w=self.prepare();old=w.open_device_editor(0);ident=old.bound_device_id;self.assertTrue(old.close());new=w.open_device_editor(0)
        QApplication.sendPostedEvents(None,QEvent.DeferredDelete);self.assertIs(w.editors[ident],new)
