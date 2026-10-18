"""Real Qt widgets offscreen; temporary databases only."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtCore import QDate
from desktop import Window
from device_store import DeviceStore

APP=QApplication.instance() or QApplication([])
BASE=Path(__file__).resolve().parents[1]

class Desktop(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.db=self.root/'hardware.sqlite3'
        with sqlite3.connect(self.db) as c:
            self.addCleanup(c.close)
            c.executescript((BASE/'schema.sql').read_text())
        self.store=DeviceStore(self.db);self.window=Window(self.store)
        self.addCleanup(self.window.deleteLater)
    def fill(self):
        for k,v in [('device_id','TEST-01'),('name','Árvíztűrő server'),('source','TEST ONLY')]:self.window.inputs[k].setText(v)
    def test_calendar_save_edit_search_and_backup(self):
        w=self.window;self.fill()
        self.assertIsNone(w.values()['purchase_date'])
        date=w.inputs['purchase_date'];self.assertTrue(date.editor.calendarPopup())
        date.known.setChecked(True);date.editor.setDate(QDate(2020,2,29))
        w.inputs['current_state'].setCurrentIndex(w.inputs['current_state'].findData('in use'))
        w.inputs['physical_condition'].setCurrentIndex(w.inputs['physical_condition'].findData('working'))
        w.inputs['purchase_price'].setText('129.90');w.inputs['purchase_currency'].setCurrentText('EUR')
        w.save();self.assertEqual(len(self.store.devices()),1)
        row=self.store.devices()[0];self.assertEqual(row['purchase_date'],'2020-02-29')
        backups=list((self.root/'backups').glob('*.sqlite3'));self.assertEqual(len(backups),1)
        with sqlite3.connect(backups[0]) as c:
            self.addCleanup(c.close)
            self.assertEqual(c.execute('SELECT count(*) FROM devices').fetchone()[0],0)
        self.assertTrue(w.inputs['device_id'].isReadOnly())
        date.known.setChecked(False);w.inputs['name'].setText('Edited');w.save()
        self.assertIsNone(self.store.devices()[0]['purchase_date'])
        self.assertEqual(self.store.devices()[0]['name'],'Edited')
        self.assertEqual(len(list((self.root/'backups').glob('*.sqlite3'))),2)
        w.search.setText('nonexistent');self.assertTrue(w.table.isRowHidden(0))
        w.search.setText('edited');self.assertFalse(w.table.isRowHidden(0))
    def test_validation_and_conflict(self):
        self.fill();data=self.window.values()
        for change in ({'name':''},{'device_id':'bad id'},{'purchase_date':'2026-02-30'}, {'purchase_price':'2'}, {'purchase_price':'-1','purchase_currency':'EUR'}, {'current_state':'In use'}):
            with self.assertRaises(ValueError):self.store.save({**data,**change})
        self.store.save(data);original=self.store.devices()[0]
        with self.assertRaises(ValueError):self.store.save(data)
        with sqlite3.connect(self.db) as c:
            self.addCleanup(c.close)
            c.execute("UPDATE devices SET name='External change'")
        with self.assertRaises(ValueError):self.store.save({**data,'name':'Overwrite'},original)
        self.assertEqual(self.store.devices()[0]['name'],'External change')
    def test_unsaved_changes(self):
        self.fill()
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Cancel):
            self.window.new();self.assertEqual(self.window.inputs['device_id'].text(),'TEST-01')
        with patch.object(Window,'unsaved_choice',return_value=QMessageBox.Discard):
            self.window.new();self.assertEqual(self.window.inputs['device_id'].text(),'')
    def test_backup_failure_prevents_write(self):
        self.fill()
        with patch('inventory.exclusive',side_effect=OSError('backup unavailable')):
            with self.assertRaises(OSError):self.store.save(self.window.values())
        self.assertEqual(self.store.devices(),[])

if __name__=='__main__':unittest.main()
