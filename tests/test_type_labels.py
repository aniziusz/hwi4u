"""Type-prefix random labels, collision handling, aliases and custom codes."""
import contextlib
import sqlite3
import subprocess
import sys
import unittest
import test_desktop
from device_store import DeviceStore

BASE=test_desktop.BASE
class TypeLabels(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_random_collision_and_reclassification_aliases(self):
        with contextlib.closing(self.store.connect()) as c:
            c.create_function('random',0,lambda:12)
            c.execute("INSERT INTO devices(device_id,name,source,device_type) VALUES('A','first','TEST ONLY','wireless access point'),('B','second','TEST ONLY','wireless access point')")
            c.commit()
            self.assertEqual([r[0] for r in c.execute('SELECT short_id FROM device_short_ids ORDER BY short_id')],['AP00012','AP00013'])
            c.execute("UPDATE devices SET device_type='firewall appliance' WHERE device_id='A'");c.commit()
            self.assertEqual(c.execute("SELECT short_id FROM device_short_ids WHERE device_id='A'").fetchone()[0],'FW00012')
            self.assertEqual(c.execute("SELECT device_id FROM device_label_aliases WHERE short_id='AP00012'").fetchone()[0],'A')
            with self.assertRaises(sqlite3.IntegrityError):c.execute("DELETE FROM device_short_labels WHERE device_id='A'")
        result=subprocess.run([sys.executable,str(BASE/'inventory.py'),'--db',str(self.db),'show','AP00012'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertIn('FW00012',result.stdout)
    def test_custom_code_auto_and_explicit_and_no_false_standard(self):
        self.store.save_type('test widget','custom',prefix='TW')
        self.store.save_type('test sensor','custom')
        rows=self.store.types();self.assertEqual(next(r for r in rows if r['type_name']=='test widget')['prefix'],'TW')
        self.assertEqual(len({r['prefix'] for r in rows}),len(rows))
        with self.assertRaises(ValueError):self.store.save_type('other widget','custom',prefix='TW')
        item=next(r for r in self.store.types() if r['type_name']=='test widget')
        self.store.save_type('renamed widget','custom',item)
        self.assertEqual(next(r for r in self.store.types() if r['type_name']=='renamed widget')['prefix'],'TW')
    def test_migration_assigns_distinct_codes_to_multiple_custom_types(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((BASE/'tests/fixtures/schema-014.sql').read_text())
            c.execute("INSERT INTO device_types(type_name,group_name) VALUES('custom one','other'),('custom two','other')")
            c.execute("INSERT INTO devices(device_id,name,source,device_type) VALUES('A','first','TEST ONLY','custom one'),('B','second','TEST ONLY','custom two')");c.commit()
            c.executescript((BASE/'migrations/015-usability-refinements.sql').read_text())
            c.executescript((BASE/'migrations/016-type-random-short-labels.sql').read_text())
            c.executescript((BASE/'migrations/017-network-identities.sql').read_text())
            c.executescript((BASE/'migrations/018-hwi4u.sql').read_text())
            c.executescript((BASE/'migrations/019-source-library.sql').read_text())
            c.executescript((BASE/'migrations/020-network-links.sql').read_text())
            c.executescript((BASE/'migrations/021-location.sql').read_text());c.executescript((BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((BASE/'migrations/023-device-roles.sql').read_text());c.executescript((BASE/'migrations/024-device-identification.sql').read_text());c.executescript((test_desktop.BASE/'migrations/025-model-lifecycle.sql').read_text())
            self.assertEqual(c.execute('SELECT count(DISTINCT prefix) FROM device_type_codes').fetchone()[0],57)
        self.assertEqual(len(DeviceStore(db).devices()),2)
