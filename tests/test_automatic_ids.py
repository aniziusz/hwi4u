"""Automatic identity and human-readable name validation, temporary data only."""
import test_desktop
import unittest
from unittest.mock import patch
import subprocess
import sys
import sqlite3
import contextlib

class AutomaticIDs(unittest.TestCase):
    setUp = test_desktop.Desktop.setUp
    def test_auto_id_readonly_save_edit_and_names(self):
        w=self.window
        self.assertTrue(w.inputs['device_id'].isReadOnly())
        w.inputs['name'].setText('backup-server-office-01')
        w.inputs['source'].setText('TEST ONLY')
        w.save()
        first=self.store.devices()[0]
        self.assertRegex(first['device_id'],r'^hw-[0-9a-f]{32}$')
        self.assertEqual(w.inputs['device_id'].text(),first['device_id'])
        w.inputs['name'].setText('archive-server-office-01');w.save()
        self.assertEqual(self.store.devices()[0]['device_id'],first['device_id'])
        duplicate={'name':' ARCHIVE-server-office-01 ','source':'TEST ONLY'}
        with self.assertRaisesRegex(ValueError,'name already exists'):self.store.save(duplicate)
        data={'name':'Árvíz  szerver','source':'TEST ONLY'};self.store.save(data)
        with self.assertRaisesRegex(ValueError,'name already exists'):
            self.store.save({'name':'ÁRVÍZ szerver','source':'TEST ONLY'})
        self.assertNotEqual(data['device_id'],first['device_id'])

    def test_failure_does_not_publish_id_or_write(self):
        data={'name':'test-device','source':'TEST ONLY'}
        with patch('inventory.exclusive',side_effect=OSError('backup unavailable')):
            with self.assertRaises(OSError):self.store.save(data)
        self.assertNotIn('device_id',data)
        self.assertEqual(self.store.devices(),[])

    def test_cli_without_id(self):
        from test_desktop import BASE
        result=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'add-device','--name','cli-device','--source','TEST ONLY'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertRegex(result.stdout,r'Added hw-[0-9a-f]{32}')
        row=self.store.devices()[0]
        with contextlib.closing(sqlite3.connect(self.db)) as c:self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertEqual(row['name'],'cli-device')
