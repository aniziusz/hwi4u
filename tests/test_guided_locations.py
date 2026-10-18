"""Guided location isolation, history, managed migration and genuine Qt form behavior."""
import contextlib,json,sqlite3,unittest,zipfile,shutil
from unittest.mock import patch
import test_desktop
from location_store import empty_location,validate_location,load_location,location_summary,PLACE_FIELDS
from location_ui import LocationDialog
from device_store import DeviceStore
from update_runtime import publish,prepare_database
from photo_files import backup_bundle
from tools.verify_bundle import restore
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

def placement(**changes):
    return {**empty_location(),'state':'recorded','building':'Fictional home','floor':'Ground floor','room':'Living room','position':'Northwest wall','height_m':'1,8','height_reference':'finished_floor',**changes}

class GuidedLocations(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def create(self,name='test',details=None):
        data=dict(name=name,source='FICTIONAL TEST',location='  Existing / text  ')
        if details is not None:data['location_details']=details
        self.store.save(data)
        return next(r for r in self.store.devices() if r['device_id']==data['device_id'])
    def test_roundtrip_height_history_place_reuse_and_move_isolation(self):
        first=self.create(details=placement());second=self.create('other',placement())
        self.assertEqual(first['_location']['height_m'],'1.8');self.assertEqual(len(self.store.places()),1)
        self.store.save(dict(first,location_details=dict(first['_location'],room='Office',position='Desk')),first)
        rows=self.store.devices();other=next(r for r in rows if r['device_id']==second['device_id'])
        self.assertEqual(other['_location']['room'],'Living room');self.assertEqual(len(self.store.places()),2)
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM device_location_history').fetchone()[0],3)
            self.assertEqual(c.execute('SELECT verification FROM device_location_history LIMIT 1').fetchone()[0],'user_reported')
            for query in ('UPDATE location_places SET room=\'wrong\'','DELETE FROM location_places','DELETE FROM device_location_history','UPDATE device_location_history SET source=\'wrong\''):
                with self.assertRaises(sqlite3.IntegrityError):c.execute(query)
    def test_height_validation_optional_levels_and_unknown(self):
        for value in ('-1','NaN','Infinity','1e99999','1e-999999','10001','one','1,2.3'):
            with self.assertRaises(ValueError):validate_location(placement(height_m=value))
        for value,expected in [('0','0'),('1,80','1.8'),('1.8','1.8'),('10000','10000')]:self.assertEqual(validate_location(placement(height_m=value))['height_m'],expected)
        with self.assertRaises(ValueError):validate_location(placement(height_reference=None))
        with self.assertRaises(ValueError):validate_location(placement(height_reference='other'))
        self.assertEqual(validate_location(placement(height_reference='other',notes='Above mounting rail'))['height_reference'],'other')
        self.assertEqual(validate_location(dict(empty_location(),state='recorded',position='Shelf'))['position'],'Shelf')
        for state in ('unknown','not_applicable'):self.assertEqual(validate_location(dict(empty_location(),state=state))['state'],state)
        with self.assertRaises(ValueError):validate_location(dict(empty_location(),room='bad'))
        with self.assertRaises(ValueError):validate_location(placement(room='x'*201))
        with self.assertRaises(ValueError):validate_location(placement(room='a\nb'))
    def test_conflict_rejected_and_backup_failure_atomic(self):
        first=self.create(details=placement())
        self.store.save(dict(first,location_details=dict(first['_location'],room='Changed')),first)
        with self.assertRaisesRegex(ValueError,'Location changed'):self.store.save(dict(first,location_details=placement(room='stale')),first)
        current=self.store.devices()[0]
        with patch('inventory.exclusive',side_effect=OSError('test failure')):
            with self.assertRaises(OSError):self.store.save(dict(current,location_details=placement(room='Never saved')),current)
        self.assertNotIn('Never saved',[p['room'] for p in self.store.places()])
        self.assertEqual(self.store.devices()[0]['_location']['room'],'Changed')
    def test_ui_preview_pending_cancel_language_search(self):
        row=self.create();w=self.window;w.reload();w.load(row)
        self.assertEqual(w.location_panel.value(),empty_location());self.assertEqual(w.location_panel.summary.textFormat(),Qt.PlainText);before=w.values()
        d=LocationDialog(self.store,empty_location(),w);self.addCleanup(d.deleteLater)
        self.assertEqual(d.preview.textFormat(),Qt.PlainText)
        d.state.setCurrentIndex(d.state.findData('recorded'))
        for k,v in [('building','Ház'),('floor','Földszint'),('room','Nappali'),('height_m','1,8')]:d.inputs[k].setText(v)
        self.assertFalse(d.use.isEnabled());d.reference.setCurrentIndex(d.reference.findData('finished_floor'));self.assertTrue(d.use.isEnabled())
        self.assertIn('1.8 m',d.preview.text());d.accept_location();w.location_panel.load(d.result_location)
        self.assertEqual(self.store.devices()[0]['_location'],empty_location());pending=w.values()
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(w.values(),pending)
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Discard):w.cancel()
        self.assertEqual(w.values(),before)
        w.location_panel.load(d.result_location);self.assertTrue(w.save());self.assertEqual(self.store.devices()[0]['location'],'Existing / text')
        w.search.setText('Nappali');self.assertFalse(w.table.isRowHidden(0));w.search.setText('Elsewhere');self.assertTrue(w.table.isRowHidden(0))
    def test_reuse_preserves_shared_place_and_clears_old_device_position(self):
        self.create(details=placement());dialog=LocationDialog(self.store,validate_location(placement(room='Other')),self.window);self.addCleanup(dialog.deleteLater)
        dialog.reuse.setCurrentIndex(2)
        self.assertEqual(dialog.inputs['room'].text(),'Living room');self.assertEqual(dialog.inputs['position'].text(),'');self.assertEqual(dialog.inputs['height_m'].text(),'')
        dialog.inputs['room'].setText('Changed only here');dialog.reject()
        self.assertEqual(self.store.places()[0]['room'],'Living room')
        for lang in ('de','hu','en'):
            self.window.set_language(lang)
            d=LocationDialog(self.store,empty_location(),self.window);self.addCleanup(d.deleteLater);self.assertTrue(d.use.toolTip());self.assertNotEqual(d.windowTitle(),'')
    def test_delete_retains_location_history_and_full_restore(self):
        row=self.create(details=placement());bundle=self.root/'full.zip';backup_bundle(self.db,bundle)
        dest=restore(bundle,self.root/'restored');restored=DeviceStore(dest/'hardware.sqlite3').devices()[0]
        self.assertEqual(restored['_location'],row['_location'])
        self.store.delete(row);self.assertEqual(self.store.devices(),[])
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM device_location_history').fetchone()[0],1)
            tomb=json.loads(c.execute('SELECT snapshot_json FROM deleted_devices').fetchone()[0]);self.assertIn('device_location_history',tomb)
    def test_managed_migration_preserves_verbatim_old_location_and_ids(self):
        old=self.root/'old.sqlite3'
        # Fresh schema through 21, excluding new tables.
        schema=(test_desktop.BASE/'schema.sql').read_text().split('CREATE TABLE location_places')[0]+'PRAGMA user_version=21;\nCOMMIT;'
        with contextlib.closing(sqlite3.connect(old)) as c:
            c.executescript(schema);c.execute("INSERT INTO devices(device_id,name,source,location) VALUES('old','Old device','TEST','  Legacy / text  ')");c.commit()
            before=c.execute('SELECT * FROM devices').fetchall();label=c.execute('SELECT * FROM device_short_ids').fetchall()
        stage=self.root/'stage';stage.mkdir()
        for name in ('schema.sql','ui_i18n.py','LICENSE-desktop.txt'):shutil.copyfile(test_desktop.BASE/name,stage/name)
        shutil.copytree(test_desktop.BASE/'migrations',stage/'migrations')
        release=publish(stage,run_tests=False);backup=prepare_database(old,release)
        with contextlib.closing(sqlite3.connect(old)) as c:
            self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before);self.assertEqual(c.execute('SELECT * FROM device_short_ids').fetchall(),label)
            self.assertEqual(c.execute('SELECT count(*) FROM device_locations').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM location_places').fetchone()[0],0)
        with zipfile.ZipFile(backup) as z:self.assertIn('hardware.sqlite3',z.namelist())
        self.assertEqual(DeviceStore(old).devices()[0]['_location'],empty_location())
