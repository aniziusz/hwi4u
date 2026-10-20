"""English presentation and client routing preserve data and canonical translations."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QLabel,QPushButton
import test_desktop
from ui_i18n import tr,apply

class CompactUI(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_network_section_preserves_values_and_language(self):
        w=self.window;s=w.network_section
        w.begin_edit();w.inputs['name'].setText('New device');w.begin_edit();w.inputs['source'].setText('Unknown')
        w.network_panel.hostname.setText('my-server.example');w.network_panel.add_row(dict(label='WAN',mac_address='02:00:00:00:00:01',addresses=['192.0.2.1']))
        before=w.values();self.assertTrue(s.body.isHidden())
        for lang,title in [('en','Network identity'),('de','Netzwerkidentität'),('hu','Hálózati azonosítók'),('en','Network identity')]:
            w.set_language(lang);self.assertEqual(s.header.text(),title)
            s.header.click();self.assertFalse(s.body.isHidden());s.header.click();self.assertTrue(s.body.isHidden())
            self.assertEqual(w.values(),before)
        self.assertEqual(w.inputs['name'].text(),'New device');self.assertEqual(w.network_panel.table.item(0,0).text(),'WAN')
    def test_restored_english_casing_preserves_sentences_and_values(self):
        w=self.window;w.set_language('en')
        self.assertEqual(w.form_title.text(),'New device')
        self.assertEqual(w.table.horizontalHeaderItem(0).text(),'Short ID')
        self.assertEqual(w.network_panel.table.horizontalHeaderItem(1).text(),'MAC address')
        self.assertEqual(w.network_panel.table.horizontalHeaderItem(2).text(),'IP addresses')
        self.assertEqual(w.menuBar().actions()[0].text(),'File')
        self.assertTrue(tr('TEST ENVIRONMENT — changes affect only the test copy.').startswith('TEST ENVIRONMENT'))
        self.assertEqual(tr('Save changes'),'Save changes');self.assertEqual(tr('About HWI4U…'),'About HWI4U…')
        sentence='Save writes the form to the database. Discard leaves the saved database record unchanged. Keep editing returns to the form.'
        self.assertEqual(tr(sentence),sentence)
        self.assertEqual(tr('Unknown — or amount such as 129.90'),'Unknown — or amount such as 129.90')
        self.assertEqual(tr('/home/Me/Name.sqlite3'),'/home/Me/Name.sqlite3')
        self.assertEqual(w.inputs['name'].toolTip()[0],'R')
        for lang in ('de','hu','en'):w.set_language(lang)
        self.assertEqual(w.form_title.text(),'New device')
    def test_client_button_routes_without_saving_or_db_override(self):
        w=self.window;w.begin_edit();w.inputs['name'].setText('NOT SAVED');before=w.values()
        for channel,expected in [('production',['test']),('test',[])]:
            with patch.dict(os.environ,{'INVENTORY_PROJECT_ROOT':str(self.root),'INVENTORY_CHANNEL':channel}),patch('desktop.QProcess.startDetached',return_value=(True,123)) as launch:
                w.open_other_client()
                args=launch.call_args.args
                self.assertEqual(args[1],[str(self.root/'run_desktop.py'),*expected]);self.assertNotIn('--db',args[1])
                self.assertEqual(w.values(),before);self.assertEqual(self.store.devices(),[])
        with patch('desktop.QProcess.startDetached',return_value=(False,0)),patch('desktop.QMessageBox.warning') as error:
            w.open_other_client();error.assert_called_once()
