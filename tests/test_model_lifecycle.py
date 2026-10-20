"""Fictional data only: sourced observations, tolerance, catalogue, GUI and recovery."""
import contextlib,copy,datetime as dt,json,sqlite3,unittest,zipfile
from unittest.mock import patch
import test_desktop
from PySide6.QtWidgets import QApplication,QDialog
from PySide6.QtCore import QDate,QEvent
from lifecycle import *
from lifecycle_ui import LifecycleEditor,ModelDialog
from source_store import SourceStore
from device_store import DeviceStore
from photo_files import backup_bundle

class ModelLifecycle(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def source(self):
        return SourceStore(self.db).save(dict(kind='observation',title='FICTIONAL verified manufacturer notice',body='Fictional test only',observed_on='2026-10-19',evidence_status='verified'))
    def record(self,**changes):
        return dict(kind='market_release',date='2025-06-15',provider='Example',product='Model 1',version='',applicability='Example variant EU',status='verified',observed_on='2026-10-19',sources=[self.source()],note='FICTIONAL',**changes) if not changes else {**self.record(),**changes}
    def add(self,records=None,**changes):
        data=dict(name='Fictional device',source='FICTIONAL',manufacturer='Example',model='Model 1',purchase_date='2024-06-15',lifecycle=records or []);data.update(changes);self.store.save(data);return self.store.devices()[0]
    def test_exact_tolerance_calendar_leap_boundary_and_latest_purchases(self):
        r=self.record();self.assertIsNone(purchase_check('2024-06-15',[r])[0]);self.assertIsNotNone(purchase_check('2024-06-14',[r])[0]);self.assertEqual(previous_year(dt.date(2024,2,29)),dt.date(2023,2,28));self.assertIsNone(purchase_check('2099-01-01',[r])[0]);self.assertEqual(bounds('2014-Q2'),(dt.date(2014,4,1),dt.date(2014,6,30)))
        for bad in ('2025-02-30','2025-Q5','2025-13','0000','Q2\'14','25-01-01'):
            with self.assertRaises(ValueError):bounds(bad)
    def test_partial_precision_unknown_conflicts_and_applicability(self):
        r=self.record(date='2014-Q2');self.assertIsNotNone(purchase_check('2013-03-31',[r])[0]);self.assertTrue(purchase_check('2013-04-01',[r])[1]);self.assertEqual(purchase_check('2013-06-30',[r]),(None,[]));self.assertEqual(purchase_check(None,[r]),(None,[]));self.assertTrue(purchase_check('2020-01-01',[])[1]);self.assertTrue(purchase_check('2013-01-01',[r,{**r,'date':'2015'}])[1]);self.assertTrue(purchase_check('2013-01-01',[{**r,'status':'uncertain'}])[1]);self.assertTrue(purchase_check('2013-01-01',[r],'Other','Model 1')[1])
    def test_date_validation_requires_sourced_verified_context_not_guessed_day(self):
        r=self.record()
        with contextlib.closing(self.store.connect()) as c:
            for changes in ({'sources':[]},{'observed_on':''},{'provider':''},{'date':'2025-Q7'},{'sources':['missing']},{'kind':'os_security_end','version':''},{'kind':'hardware_service_end','applicability':''},{'kind':'warranty_expiry','applicability':''}):
                with self.assertRaises(ValueError):validate_records(c,[{**r,**changes}])
            a=validate_records(c,[{**r,'status':'uncertain','sources':[],'date':'2014-Q2'}]);self.assertEqual(a[0]['date'],'2014-Q2')
    def test_store_atomic_block_stale_conflict_history_and_legacy_edits(self):
        r=self.record();old=self.add([r]);before=len(list((self.root/'backups').glob('*')))
        with self.assertRaisesRegex(ValueError,'earlier'):self.store.save({**old,'purchase_date':'2024-06-14','lifecycle':old['_lifecycle']},old)
        self.assertEqual(len(list((self.root/'backups').glob('*'))),before)
        self.store.save({**old,'lifecycle':[{**r,'date':'2025-05-15'}]},old)
        with self.assertRaisesRegex(ValueError,'Lifecycle dates changed'):self.store.save({**old,'lifecycle':[r]},old)
        updated=self.store.devices()[0];self.assertEqual(updated['short_id'],old['short_id'])
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM device_lifecycle_history').fetchone()[0],2)
            c.execute("UPDATE devices SET purchase_date='2020-01-01'");c.commit()
        legacy=self.store.devices()[0];self.store.save({**legacy,'name':'Unrelated edit','lifecycle':legacy['_lifecycle']},legacy)
    def test_pre_save_failure_does_not_change_lifecycle(self):
        old=self.add();r=self.record()
        with patch('inventory.exclusive',side_effect=OSError('no backup')):
            with self.assertRaises(OSError):self.store.save({**old,'lifecycle':[r]},old)
        self.assertEqual(self.store.devices()[0]['_lifecycle'],[])
    def profile(self,**changes):
        r=self.record();data=dict(manufacturer='Example',model='Model 1',variant='EU revision A',device_type='firewall appliance',roles=['firewall','router'],lifecycle=[r],sources=r['sources'],note='FICTIONAL verified model, review variant')
        data.update(changes);return data
    def test_profiles_exact_matches_multiple_variants_immutable_revisions(self):
        store=ModelStore(self.db);data=self.profile();ident=store.save(data);rows=store.list(' example ','MODEL  1');self.assertEqual(rows[0]['profile_id'],ident);self.assertEqual(store.list('Example','Model'),[])
        with self.assertRaises(ValueError):store.save(data)
        store.save({**data,'variant':'US revision B'});self.assertEqual(len(store.list('Example','Model 1')),2)
        store.save({**data,'note':'New sourced explanation'},rows[0]);self.assertEqual(len(store.list()),2)
        with self.assertRaisesRegex(ValueError,'changed'):store.save(data,rows[0])
        self.assertEqual(self.store.devices(),[])
        with contextlib.closing(self.store.connect()) as c:self.assertEqual(c.execute('SELECT count(*) FROM model_profiles').fetchone()[0],3)
        with self.assertRaisesRegex(ValueError,'warranty'):store.save({**data,'variant':'Warranty bad','lifecycle':[{**data['lifecycle'][0],'kind':'warranty_expiry'}]})
    def test_model_application_review_cancel_preserves_warranty_pending_and_sources(self):
        w=self.window;w.begin_edit();w.inputs['name'].setText('Fictional');w.begin_edit();w.inputs['source'].setText('FICTIONAL');w.begin_edit();w.inputs['manufacturer'].setText('Example');w.begin_edit();w.inputs['model'].setText('Model 1');w.inputs['purchase_date'].load('2024-06-15')
        data=self.profile();ModelStore(self.db).save(data);w.lifecycle_panel.load([{**data['lifecycle'][0],'kind':'warranty_expiry','date':'2029-12-31','applicability':'Individual contract TEST'}]);before=w.values()
        dialog=ModelDialog(w);self.assertFalse(dialog.apply_button.isEnabled());dialog.list.setCurrentRow(0);self.assertFalse(dialog.apply_button.isEnabled());dialog.confirm.setChecked(True);self.assertTrue(dialog.apply_button.isEnabled());dialog.reject();self.assertEqual(w.values(),before)
        profile=ModelStore(self.db).list()[0];w.apply_model_profile(profile);self.assertEqual(w.role_values,['firewall','router']);self.assertEqual(len(w.lifecycle_panel.value()),2);self.assertEqual(w.inputs['device_type'].currentData(),'firewall appliance');self.assertEqual(self.store.devices(),[]);self.assertTrue(w.save());self.assertEqual(len(self.store.devices()[0]['_lifecycle']),2)
    def test_lifecycle_editor_precision_sources_calendar_and_language(self):
        w=self.window;r=self.record();editor=LifecycleEditor(w.lifecycle_panel,r);self.assertTrue(editor.day.calendarPopup());editor.precision.setCurrentIndex(editor.precision.findData('quarter'));editor.partial.setText('2014-Q2');editor.save();self.assertEqual(editor.result_record['date'],'2014-Q2');w.lifecycle_panel.load([editor.result_record]);before=w.values()
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(w.values(),before)
    def test_expanded_editor_lifecycle_tile_and_save_cancel_round_trip(self):
        row=self.add([self.record()]);w=self.window;w.reload();e=w.open_device_editor(0)
        self.addCleanup(lambda:setattr(e,'skip_close_prompt',True));self.addCleanup(e.deleteLater)
        self.assertIs(e.lifecycle_panel.parentWidget(),e.workspace.cards['lifecycle']);self.assertEqual(e.lifecycle_panel.value(),row['_lifecycle']);e.lifecycle_panel.records[0]['note']='pending';self.assertNotEqual(e.values(),e.baseline)
        with patch.object(e,'discard_ok',return_value=True):e.cancel()
        self.assertEqual(e.lifecycle_panel.value(),row['_lifecycle'])
    def test_migration_24_preserves_devices_sources_ids_without_guessing(self):
        db=self.root/'old24.sqlite3';schema=(test_desktop.BASE/'schema.sql').read_text().split('CREATE TABLE device_lifecycle (')[0]+'PRAGMA user_version=24; COMMIT;'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript(schema);c.execute("INSERT INTO devices(device_id,name,source,manufacturer,model) VALUES('legacy','Old','FICTIONAL','Example','Model 1')");c.commit();before=c.execute('SELECT * FROM devices').fetchall();labels=c.execute('SELECT * FROM device_short_ids').fetchall();c.executescript((test_desktop.BASE/'migrations/025-model-lifecycle.sql').read_text());c.executescript((test_desktop.BASE/'migrations/026-device-tags.sql').read_text());self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before);self.assertEqual(c.execute('SELECT * FROM device_short_ids').fetchall(),labels);self.assertEqual(c.execute('SELECT count(*) FROM device_lifecycle').fetchone()[0],0);self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertEqual(DeviceStore(db).devices()[0]['_lifecycle'],[])
    def test_backup_export_and_delete_preserve_sources_and_history(self):
        r=self.record();row=self.add([r]);bundle=backup_bundle(self.db,self.root/'bundle.zip');export=self.root/'export'
        inventory.main(['--db',str(self.db),'export','--directory',str(export)])
        data=json.loads((export/'inventory.json').read_text());self.assertTrue(data['device_lifecycle']);self.assertTrue(data['device_lifecycle_history'])
        restored=self.root/'restore.sqlite3'
        with contextlib.closing(sqlite3.connect(restored)) as c:c.executescript((export/'inventory.sql').read_text());inventory.check(c)
        self.assertEqual(DeviceStore(restored).devices()[0]['_lifecycle'],row['_lifecycle'])
        self.store.delete(row)
        with contextlib.closing(self.store.connect()) as c:
            snapshot=json.loads(c.execute('SELECT snapshot_json FROM deleted_devices').fetchone()[0]);self.assertTrue(snapshot['device_lifecycle']);self.assertTrue(snapshot['device_lifecycle_history']);self.assertTrue(c.execute('SELECT * FROM source_entries').fetchall());self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_all_properties_and_multiple_software_versions_remain_separate(self):
        release=self.record();records=[release]
        for kind in KINDS:
            if kind!='market_release':records.append({**release,'kind':kind,'date':'2030','version':'Track A','applicability':'Fictional individual/service scope EU'})
        records.append({**release,'kind':'os_security_end','product':'Fictional OS','version':'Track B','date':'2031-06'})
        row=self.add(records);self.assertEqual(len(row['_lifecycle']),7);self.assertEqual(len([r for r in row['_lifecycle'] if r['kind']=='os_security_end']),2)
        self.store.save({**row,'lifecycle':[]},row)
        with contextlib.closing(self.store.connect()) as c:
            history=[json.loads(r[0]) for r in c.execute('SELECT records_json FROM device_lifecycle_history ORDER BY history_id')]
        self.assertEqual(history,[records,[]])
    def test_catalogue_revision_never_changes_existing_device_and_stale_apply_is_rejected(self):
        data=self.profile();catalogue=ModelStore(self.db);catalogue.save(data);profile=catalogue.list()[0];device=self.add(data['lifecycle']);catalogue.save({**data,'lifecycle':[{**data['lifecycle'][0],'date':'2025-07'}]},profile)
        self.assertEqual(self.store.devices()[0]['_lifecycle'],device['_lifecycle'])
        w=self.window;w.reload();w.load(w.rows[0]);before=w.values()
        w.begin_edit()
        with self.assertRaisesRegex(ValueError,'changed'):w.apply_model_profile(profile)
        self.assertEqual(w.values(),before)
    def test_unverified_source_cannot_confirm_a_release_and_stale_delete_is_rejected(self):
        sid=SourceStore(self.db).save(dict(kind='observation',title='Fictional unverified',body='TEST',evidence_status='uncertain'))
        r=self.record(sources=[sid])
        with self.assertRaisesRegex(ValueError,'verified dated'):self.add([r])
        old=self.add();self.store.save({**old,'lifecycle':[{**r,'status':'uncertain'}]},old)
        with self.assertRaisesRegex(ValueError,'changed outside'):self.store.delete(old)
