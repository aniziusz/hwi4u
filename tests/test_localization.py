"""Language changes preserve unsaved values and database records."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import contextlib
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication,QPushButton,QMessageBox
from PySide6.QtCore import QDate,Qt,QLocale
from desktop import Window,ConnectionDialog,TypeDialog
from device_store import DeviceStore
from ui_i18n import tr,apply,read_language,APP_VERSION

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]
class Localization(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.db=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.db)) as c:c.executescript((BASE/'schema.sql').read_text())
        self.store=DeviceStore(self.db);self.w=Window(self.store,language='en');self.addCleanup(self.w.deleteLater)
    def test_switch_preserves_unsaved_data(self):
        for k,v in (('device_id','TEST'),('name','New device'),('source','Unknown')):self.w.inputs[k].setText(v)
        self.w.inputs['purchase_date'].known.setChecked(True);self.w.inputs['purchase_date'].editor.setDate(QDate(2020,2,29))
        self.w.inputs['current_state'].setCurrentIndex(self.w.inputs['current_state'].findData('in use'))
        panel=self.w.connection_panels['interface'];panel.supported.setCurrentIndex(panel.supported.findData('recorded'));panel.source.setText('Name')
        panel.table.item(panel.options.index('wi-fi'),1).setCheckState(Qt.Checked)
        before=self.w.values()
        for code,title,lang in [('de','HWI4U',QLocale.German),('hu','HWI4U',QLocale.Hungarian),('en','HWI4U',QLocale.English)]:
            self.w.set_language(code)
            self.assertEqual(self.w.windowTitle(),title)
            self.assertEqual(self.w.values(),before)
            self.assertEqual(self.w.inputs['purchase_date'].editor.locale().language(),lang)
            self.assertEqual(read_language(self.root),code)
            self.assertTrue(self.w.language_actions[code].isChecked())
        self.w.save();saved=self.store.devices()[0]
        self.assertEqual(saved['name'],'New device');self.assertEqual(saved['source'],'Unknown');self.assertEqual(saved['current_state'],'in use')
        self.assertEqual(saved['_connectivity']['interface']['supported'],['wi-fi'])
    def test_about_help_dialogs_and_dynamic_labels(self):
        self.w.set_language('de');self.assertEqual(self.w.form_title.text(),'Neues Gerät')
        self.assertIn('eindeutige',self.w.inputs['device_id'].toolTip())
        self.assertIn('gemeinsamen',next(b for b in self.w.findChildren(QPushButton) if b.property('_i18n_source_text')=='Manage connection choices…').toolTip().lower())
        self.assertIn(APP_VERSION,self.w.about_text());self.assertIn(str(self.db),self.w.about_text());self.assertIn('Datenbankschema',self.w.about_text())
        self.assertIn('gültiges',tr('Purchase date: choose a valid calendar date.'))
        for cls,expected in ((ConnectionDialog,'Verbindungsauswahl verwalten'),(TypeDialog,'Gerätetypen verwalten')):
            dialog=cls(self.store,self.w);self.addCleanup(dialog.deleteLater);dialog.show();APP.processEvents()
            self.assertEqual(dialog.windowTitle(),expected)
            self.assertTrue(dialog.name.toolTip())
            dialog.hide()
        self.w.status.setText('Saved TEST. Pre-save backup: example.sqlite3');apply(self.w)
        self.assertIn('gespeichert',self.w.status.text())
        self.w.set_language('hu');self.assertIn('mentve',self.w.status.text())
        self.w.set_language('en');self.assertIn('Saved TEST',self.w.status.text())
    def test_real_button_click_and_preference_restart(self):
        self.w.set_language('hu')
        button=next(b for b in self.w.findChildren(QPushButton) if b.property('_i18n_source_text')=='New device')
        button.click();self.assertEqual(self.w.form_title.text(),'Új eszköz')
        other=Window(self.store);self.addCleanup(other.deleteLater)
        self.assertEqual(other.windowTitle(),'HWI4U')
        with patch('desktop.QDesktopServices.openUrl',return_value=True) as openurl:
            other.open_guide();self.assertTrue(openurl.call_args[0][0].toLocalFile().endswith('GUIDE.hu.md'))
    def test_missing_and_bad_preferences(self):
        (self.root/'ui-settings.json').write_text('not valid json')
        self.assertEqual(read_language(self.root),'en')
        self.w.set_language('de')
        with self.assertRaises(ValueError):self.w.set_language('xx')

if __name__=='__main__':unittest.main()
