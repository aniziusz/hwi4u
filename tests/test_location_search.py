import contextlib,sqlite3,unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import test_desktop
from ui_i18n import install

class LocationSearch(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_location_roundtrip_search_unicode_language_and_validation(self):
        w=self.window;w.begin_edit();w.inputs['name'].setText('test device');w.begin_edit();w.inputs['source'].setText('TEST ONLY');w.begin_edit();w.inputs['location'].setText('  Büro / földszint  ');self.assertTrue(w.save());row=self.store.devices()[0];self.assertEqual(row['location'],'Büro / földszint')
        w.search.setText('földszint');self.assertFalse(w.table.isRowHidden(0));w.search.setText('elsewhere');self.assertTrue(w.table.isRowHidden(0))
        w.begin_edit();w.inputs['location'].setText('unsaved location');before=w.values()
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(w.values(),before)
        self.assertIn('200',w.inputs['location'].toolTip())
        for value in ('x'*201,'room\nother',42):
            with self.assertRaises(ValueError):self.store.save(dict(row,location=value),row)
        self.store.save(dict(row,location=''),row);self.assertIsNone(self.store.devices()[0]['location'])
    def test_contains_completion_commits_existing_choices_and_keeps_wheel_protection(self):
        w=self.window;combo=w.group_filter;self.assertTrue(combo.isEditable());before=combo.currentData();combo.lineEdit().setText('NET');completer=combo.completer();completer.setCompletionPrefix('NET');model=completer.completionModel();matches=[model.index(n,0).data() for n in range(model.rowCount())];self.assertIn('networking',matches);self.assertEqual(combo.currentData(),before)
        combo.choose_completion('networking');self.assertEqual(combo.currentData(),'networking');self.assertGreater(w.type_filter.count(),2)
        combo.choose_completion('does not exist');self.assertEqual(combo.currentData(),'networking')
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(combo.currentData(),'networking')
        combo.setCurrentIndex(0);self.assertIsNone(combo.currentData());self.assertFalse(combo.insertPolicy()!=__import__('PySide6.QtWidgets',fromlist=['QComboBox']).QComboBox.NoInsert)
        from test_topology import Wheel
        Wheel.send(self,combo.lineEdit());self.assertIsNone(combo.currentData())
    def test_location_migration_old_values_preserved_and_unknown_not_invented(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((test_desktop.BASE/'tests/fixtures/schema-020.sql').read_text());c.execute("INSERT INTO devices(device_id,name,source) VALUES('test','test','TEST ONLY')");c.commit();before=c.execute('SELECT * FROM devices').fetchone();c.executescript((test_desktop.BASE/'migrations/021-location.sql').read_text());after=c.execute('SELECT * FROM devices').fetchone();self.assertEqual(after[:-1],before);self.assertIsNone(after[-1])
