"""Assembly integrity checks on temporary databases only."""
from pathlib import Path
import json
import contextlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]

class Assemblies(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root/'test.sqlite3'
        self.cli('init')
        for ident in ('SERVER','OTHER','BOARD','DISK','RAM'):
            self.cli('add-device','--id',ident,'--name',ident,'--source','TEST ONLY')

    def cli(self,*args,ok=True):
        r=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),*args],capture_output=True,text=True)
        self.assertEqual(r.returncode == 0,ok,r.stderr)
        return r.stdout

    def install(self,parent,component,date='2020-01-01',position=None,ok=True):
        args=['install-component','--parent',parent,'--component',component,'--source','TEST ONLY']
        if date: args+=['--installed-on',date]
        if position: args+=['--position',position]
        return self.cli(*args,ok=ok)

    def test_history_and_validation(self):
        self.install('SERVER','DISK',position='Bay 1')
        self.install('OTHER','DISK',ok=False)
        self.install('SERVER','RAM',position='Bay 1',ok=False)
        self.install('DISK','SERVER',ok=False)
        self.install('SERVER','SERVER',ok=False)
        self.install('MISSING','RAM',ok=False)
        self.install('SERVER','RAM',date='2026-02-30',ok=False)
        self.cli('remove-component','--installation','1','--removed-on','2019-01-01','--source','TEST ONLY',ok=False)
        self.cli('remove-component','--installation','1','--removed-on','2021-01-01','--source','TEST ONLY')
        self.install('OTHER','DISK',date='2021-01-01')
        self.install('SERVER','RAM',date='2021-01-01',position='Bay 1')
        self.assertEqual(len(json.loads(self.cli('assembly','SERVER','--history'))['components']),2)
        self.assertEqual(len(json.loads(self.cli('assembly','SERVER'))['components']),1)
        # Updates cannot bypass overlap checks; ordinary SQL validates calendar dates too.
        with contextlib.closing(sqlite3.connect(self.db)) as c, c:
            with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE component_installations SET removed_on=NULL WHERE installation_id=1")
            with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE component_installations SET installed_on='2020-02-30' WHERE installation_id=1")

    def test_nested_cycles_and_unknown_dates(self):
        self.install('SERVER','BOARD')
        self.install('BOARD','RAM')
        self.install('RAM','SERVER',ok=False)
        self.install('OTHER','DISK',date=None)
        self.install('SERVER','DISK',date='2010-01-01',ok=False)
        self.cli('remove-component','--installation','1','--removed-on','2021-01-01','--source','TEST ONLY')
        # Reversing an old link in a later, nonoverlapping period is valid.
        self.install('BOARD','SERVER',date='2022-01-01')

    def test_export_backup(self):
        self.install('SERVER','DISK')
        self.cli('export','--directory',str(self.root/'export'))
        self.cli('backup','--output',str(self.root/'backup.sqlite3'))
        with contextlib.closing(sqlite3.connect(self.root/'restored.sqlite3')) as c, c:
            c.executescript((self.root/'export/inventory.sql').read_text())
            self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],21)
            self.assertEqual(c.execute('SELECT count(*) FROM component_installations').fetchone()[0],1)
            self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute("INSERT INTO component_installations(parent_device,component_device,source) VALUES('DISK','SERVER','TEST ONLY')")

    def test_migration(self):
        # Build the previous schema without reading the working database.
        sql=(BASE/'schema.sql').read_text()
        old=sql[:sql.index('CREATE TABLE component_installations')]+ 'PRAGMA user_version=7;\nCOMMIT;\n'
        with contextlib.closing(sqlite3.connect(self.root/'old.sqlite3')) as c, c:
            c.executescript(old)
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('OLD','Old','TEST ONLY')")
            c.execute("INSERT INTO facts(device_id,field,value,source) VALUES('OLD','model','Example','TEST ONLY')")
            c.commit()
            before=c.execute('SELECT * FROM devices').fetchall()
            c.executescript((BASE/'migrations/008-assemblies.sql').read_text())
            self.assertEqual(before,c.execute('SELECT * FROM devices').fetchall())
            self.assertEqual(c.execute('SELECT count(*) FROM facts').fetchone()[0],1)
            self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())

if __name__ == '__main__': unittest.main()
