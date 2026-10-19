"""Optional hardware labels: migration, exact serial text and both editor positions."""
import contextlib,json,sqlite3,unittest
from unittest.mock import patch
import test_desktop
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent
from device_store import DeviceStore
from list_view import KEYS,read_view

class Identification(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def close_editors(self):
        for e in list(self.window.editors.values()):e.skip_close_prompt=True;e.close()
        QApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    def test_exact_serial_blank_limits_conflict_and_backup(self):
        data=dict(name='Fictional device',source='FICTIONAL TEST',manufacturer=' Example GmbH ',model=' Modell Ü-4 ',serial_number=' 000aB  019 ');self.store.save(data);row=self.store.devices()[0]
        self.assertEqual((row['manufacturer'],row['model'],row['serial_number']),('Example GmbH','Modell Ü-4','000aB  019'));ident=row['device_id'],row['short_id']
        self.store.save({**data,'manufacturer':'changed'},row);updated=self.store.devices()[0]
        with self.assertRaisesRegex(ValueError,'changed outside'):self.store.save({**data,'model':'stale'},row)
        self.assertEqual((updated['device_id'],updated['short_id']),ident)
        for value in ('x'*201,'line\nbreak','tab\tlabel','bad\x00label'):
            for key in ('manufacturer','model','serial_number'):
                with self.assertRaises(ValueError):self.store.save({**updated,key:value},updated)
        with patch('inventory.exclusive',side_effect=OSError('backup unavailable')):
            with self.assertRaises(OSError):self.store.save({**updated,'serial_number':'different'},updated)
        self.assertEqual(self.store.devices()[0]['serial_number'],'000aB  019')
        self.store.save({**updated,'manufacturer':' ','model':'','serial_number':None},updated);self.assertTrue(all(self.store.devices()[0][key] is None for key in ('manufacturer','model','serial_number')))
        self.assertTrue(list((self.root/'backups').glob('before-device-save-*')))
    def test_migration_preserves_rows_and_does_not_guess_hardware_labels(self):
        schema=(test_desktop.BASE/'schema.sql').read_text();schema=schema[:schema.index('ALTER TABLE devices ADD COLUMN manufacturer')]+'PRAGMA user_version=23; COMMIT;';db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript(schema);c.execute("INSERT INTO devices(device_id,name,source) VALUES('old','Example vendor/model in name','FICTIONAL TEST')");c.commit();columns=[r[1] for r in c.execute('PRAGMA table_info(devices)')];before=c.execute('SELECT * FROM devices').fetchall();labels=c.execute('SELECT * FROM device_short_ids').fetchall();c.executescript((test_desktop.BASE/'migrations/024-device-identification.sql').read_text());c.executescript((test_desktop.BASE/'migrations/025-model-lifecycle.sql').read_text());self.assertEqual(c.execute('SELECT '+','.join(columns)+' FROM devices').fetchall(),before);self.assertEqual(c.execute('SELECT * FROM device_short_ids').fetchall(),labels);self.assertEqual(c.execute('SELECT manufacturer,model,serial_number FROM devices').fetchone(),(None,None,None));self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertIsNone(DeviceStore(db).devices()[0]['manufacturer'])
    def test_field_order_both_editors_languages_search_and_optional_columns(self):
        w=self.window;order=['manufacturer','model','serial_number','location'];form=w.inputs['location'].parentWidget().layout();indices=[form.getWidgetPosition(w.inputs[k])[0] for k in order];self.assertEqual(indices,sorted(indices));self.assertEqual(len(set(indices)),4)
        w.inputs['name'].setText('Fictional device');w.inputs['source'].setText('FICTIONAL TEST')
        for k,v in [('manufacturer','Fictional maker'),('model','Model-x'),('serial_number','00007aB')]:w.inputs[k].setText(v)
        self.assertTrue(w.save());w.search.setText('00007AB');self.assertFalse(w.table.isRowHidden(0));self.assertIn('manufacturer',KEYS)
        self.addCleanup(self.close_editors);e=w.open_device_editor(0);form=e.workspace.forms['location'];indices=[form.getWidgetPosition(e.inputs[k])[0] for k in order];self.assertEqual(indices,sorted(indices));before=e.values()
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(e.values(),before)
        self.assertEqual(e.inputs['serial_number'].text(),'00007aB');self.assertIn('200',e.inputs['serial_number'].toolTip());self.assertTrue(e.save())
    def test_existing_column_preferences_are_preserved_when_fields_added(self):
        old=KEYS[:-3];path=self.root/'view.json';path.write_text(json.dumps(dict(order=list(reversed(old)),hidden=['roles'],groups=['device_type'],filters={'name':['Example']},widths={'name':233})))
        view=read_view(path);self.assertEqual(view['order'][:-3],list(reversed(old)));self.assertEqual(view['order'][-3:],['manufacturer','model','serial_number']);self.assertEqual(view['widths'],{'name':233});self.assertEqual(view['filters'],{'name':['Example']});self.assertTrue(set(KEYS[-3:])<=set(view['hidden']))
