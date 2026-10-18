"""Lowercase-choice migration checks; temporary databases only."""
from pathlib import Path
import sqlite3
import contextlib
import tempfile
import unittest

BASE=Path(__file__).resolve().parents[1]

class Lowercase(unittest.TestCase):
    def test_migration_and_constraints(self):
        with tempfile.TemporaryDirectory() as t:
            with contextlib.closing(sqlite3.connect(':memory:')) as source, contextlib.closing(sqlite3.connect(Path(t)/'test.sqlite3')) as c:
                source.executescript((BASE/'tests/fixtures/schema-008.sql').read_text())
                self.addCleanup(source.close)
                self.addCleanup(c.close)
                source.backup(c)
                c.execute("INSERT INTO devices(device_id,name,source,current_state,physical_condition) VALUES('PARENT','Keep Name','TEST ONLY','In use','Working')")
                c.execute("INSERT INTO devices(device_id,name,source) VALUES('CHILD','Keep Child','TEST ONLY')")
                c.execute("INSERT INTO facts(device_id,field,value,source) VALUES('PARENT','note','Keep Capitals','TEST ONLY')")
                c.execute("INSERT INTO component_installations(parent_device,component_device,source) VALUES('PARENT','CHILD','TEST ONLY')")
                c.commit()
                c.executescript((BASE/'migrations/009-lowercase-values.sql').read_text())
                self.assertEqual(c.execute("SELECT name,current_state,physical_condition FROM devices WHERE device_id='PARENT'").fetchone(),('Keep Name','in use','working'))
                self.assertEqual(c.execute("SELECT current_state,physical_condition FROM devices WHERE device_id='CHILD'").fetchone(),(None,None))
                self.assertEqual(c.execute('SELECT value FROM facts').fetchone()[0],'Keep Capitals')
                self.assertEqual(c.execute('SELECT count(*) FROM component_installations').fetchone()[0],1)
                self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
                for table in ('device_states','physical_conditions'):
                    self.assertFalse(c.execute(f'SELECT value FROM {table} WHERE value != lower(value)').fetchall())
                with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE devices SET current_state='In use'")
                with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE devices SET physical_condition='Working'")
                with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO component_installations(parent_device,component_device,source) VALUES('CHILD','PARENT','TEST ONLY')")
                self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')

if __name__=='__main__':unittest.main()
