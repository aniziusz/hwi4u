"""Inline update actions preserve form values and use the managed restart path."""
import json,os,unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QMessageBox
from desktop import Window
from update_runtime import UPDATE_EXIT
import test_desktop

class UpdateNotice(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def prepare_pointer(self):
        folder=self.root/'.runtime';folder.mkdir(exist_ok=True);self.pointer=folder/'current.json';self.pointer.write_text(json.dumps({'release_id':'new'}))
        return {'INVENTORY_PROJECT_ROOT':str(self.root),'INVENTORY_RELEASE_ID':'old','INVENTORY_CHANNEL':'production'}
    def test_abort_keeps_edits_hides_same_candidate_and_manual_check_restores_actions(self):
        w=self.window;w.begin_edit();w.inputs['name'].setText('UNSAVED');before=w.values()
        with patch.dict(os.environ,self.prepare_pointer()),patch.object(QApplication,'exit') as exit_call:
            w.check_update();self.assertFalse(w.update_notice.isHidden());self.assertEqual(w.footer_apply.text(),'Apply update');self.assertEqual(w.footer_abort.text(),'Abort')
            w.footer_abort.click();self.assertTrue(w.update_notice.isHidden());self.assertEqual(w.values(),before);self.assertEqual(self.store.devices(),[]);exit_call.assert_not_called()
            w.check_update();self.assertTrue(w.update_notice.isHidden());self.assertFalse(w.update_button.isHidden())
            w.show_update_status();self.assertFalse(w.update_notice.isHidden())
            w.footer_abort.click();self.pointer.write_text(json.dumps({'release_id':'newer'}));w.check_update();self.assertFalse(w.update_notice.isHidden())
            self.pointer.write_text(json.dumps({'release_id':'old'}));w.check_update();self.assertTrue(w.update_notice.isHidden())
    def test_apply_button_honors_unsaved_cancel_then_save_and_translates(self):
        w=self.window;w.begin_edit();w.inputs['name'].setText('pending');w.begin_edit();w.inputs['source'].setText('TEST ONLY');before=w.values()
        with patch.dict(os.environ,self.prepare_pointer()),patch.object(QApplication,'exit') as exit_call:
            w.check_update()
            with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Cancel):w.footer_apply.click();exit_call.assert_not_called();self.assertEqual(w.values(),before)
            for lang,label in [('de','Abbrechen'),('hu','Megszakítás'),('en','Abort')]:
                w.set_language(lang);self.assertEqual(w.footer_abort.text(),label);self.assertEqual(w.values(),before)
            with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Save):w.footer_apply.click()
            exit_call.assert_called_once_with(UPDATE_EXIT);self.assertEqual(self.store.devices()[0]['name'],'pending')
