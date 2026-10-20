"""Names, reusable tags, isolation, migration and exports using fictional inventories."""
import contextlib,json,sqlite3,subprocess,sys,unittest,zipfile,shutil
from unittest.mock import patch
import test_desktop
from names import suggested_name,name_key
from tags import tag_label
from device_store import DeviceStore
from desktop import Window
from list_view import values,matches,KEYS,ChoiceDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QApplication,QMessageBox
from photo_files import backup_bundle
from tools.verify_bundle import restore
from update_runtime import publish,prepare_database

class NamesTags(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def add(self,name='Fictional device',tags=()):
        data=dict(name=name,source='FICTIONAL TEST',tags=list(tags));self.store.save(data)
        return next(r for r in self.store.devices() if r['device_id']==data['device_id'])
    def test_name_missing_unicode_long_duplicate_and_id_separation(self):
        self.assertIsNone(suggested_name(None,None,None))
        self.assertEqual(suggested_name('Fictional','Modell','router'),'Fictional Modell — router')
        self.assertEqual(suggested_name(None,'Árvíztűrő',None),'Árvíztűrő')
        self.assertEqual(suggested_name(None,None,'router'),'router')
        base='Árvíztűrő';self.assertEqual(suggested_name(None,base,None,[' ÁRVÍZTŰRŐ ',base+' (2)']),base+' (3)')
        long='ő'*200;result=suggested_name(long,None,'server',['ő'*100]);self.assertEqual(len(result),100);self.assertTrue(result.endswith(' (2)'))
        row=self.add('Fictional Modell — router');self.assertEqual(self.store.suggest_name('Fictional','Modell','router'),'Fictional Modell — router (2)')
        self.assertEqual(self.store.suggest_name('Fictional','Modell','router',row['device_id']),row['name'])
        self.assertEqual(self.store.devices()[0]['device_id'],row['device_id'])
    def test_name_preview_explicit_use_modes_and_language(self):
        w=self.window;w.inputs['name'].setText('Keep original');w.inputs['manufacturer'].setText('Fictional');w.inputs['model'].setText('M1')
        self.assertEqual(w.inputs['name'].text(),'Keep original');self.assertEqual(w.name_preview.text(),'Fictional M1')
        w.inputs['device_type'].setCurrentIndex(w.inputs['device_type'].findData('router'));self.assertEqual(w.name_preview.text(),'Fictional M1 — router')
        w.type_group.setCurrentIndex(w.type_group.findData('storage'));self.assertEqual(w.name_preview.text(),'Fictional M1')
        w.type_group.setCurrentIndex(0)
        w.name_use.click();self.assertEqual(w.inputs['name'].text(),'Fictional M1')
        w.inputs['source'].setText('FICTIONAL');self.assertTrue(w.save());self.assertFalse(w.name_use.isEnabled())
        before=w.values();w.use_name_suggestion();self.assertEqual(w.values(),before)
        w.begin_edit();w.inputs['model'].setText('M2');before=w.values()
        for code in ('de','hu','en'):w.set_language(code);self.assertEqual(w.values(),before)
        self.assertEqual(w.inputs['name'].text(),'Fictional M1')
    def test_tag_normalization_reuse_history_conflict_and_backup_failure(self):
        a=self.add(tags=['  Gäste   Büro  ','GÄSTE BÜRO','安全'])
        self.assertEqual(a['_tags'],['Gäste Büro','安全']);b=self.add('Another',tags=['gäste büro'])
        self.assertEqual(b['_tags'],['Gäste Büro']);self.assertEqual(len(self.store.tags()),2)
        with contextlib.closing(self.store.connect()) as c:ids=[tuple(r) for r in c.execute('SELECT tag_id,label FROM tag_choices')]
        self.store.save({**a,'tags':['安全']},a);updated=next(r for r in self.store.devices() if r['device_id']==a['device_id'])
        with self.assertRaisesRegex(ValueError,'Tags changed'):self.store.save({**a,'tags':[]},a)
        with patch('inventory.exclusive',side_effect=OSError('backup unavailable')):
            with self.assertRaises(OSError):self.store.save({**updated,'tags':['Not committed']},updated)
        self.assertNotIn('Not committed',self.store.tags())
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual([tuple(r) for r in c.execute('SELECT tag_id,label FROM tag_choices')],ids)
            history=json.loads(c.execute('SELECT after_json FROM device_tag_history WHERE device_id=? ORDER BY history_id DESC',(a['device_id'],)).fetchone()[0]);self.assertEqual(history[0]['label'],'安全')
            with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM device_tag_history')
        self.assertEqual(next(r for r in self.store.devices() if r['device_id']==b['device_id'])['_tags'],['Gäste Büro'])
    def test_tag_validation_atomicity_and_canonical_equivalence(self):
        for label in ('',' '*3,'a'*51,'two\nlines','tab\tvalue','bad\x00'):
            with self.assertRaises(ValueError):tag_label(label)
        a=self.add(tags=['Café','Cafe\u0301',' CAFÉ ']);self.assertEqual(a['_tags'],['Café'])
        with self.assertRaises(ValueError):self.store.save({**a,'tags':['bad\nlabel']},a)
        self.assertEqual(self.store.devices()[0]['_tags'],['Café'])
        self.store.save({**a,'name':'Unrelated edit'},a);self.assertEqual(self.store.devices()[0]['_tags'],['Café'])
    def test_tag_pending_cancel_save_quick_and_expanded_modes(self):
        row=self.add();w=self.window;w.reload();w.load(w.rows[0]);self.assertFalse(w.tag_button.isEnabled());self.assertFalse(w.choose_tags())
        w.begin_edit()
        def accept(dialog):
            item=__import__('PySide6.QtWidgets',fromlist=['QListWidgetItem']).QListWidgetItem('Pending',dialog.list);item.setData(Qt.UserRole,'Pending');item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked);return QDialog.Accepted
        with patch.object(ChoiceDialog,'exec',accept):w.choose_tags()
        self.assertEqual(w.tag_values,['Pending']);self.assertEqual(self.store.tags(),[])
        with patch.object(w,'unsaved_choice',return_value=QMessageBox.Discard):w.cancel()
        self.assertEqual(w.tag_values,[]);self.assertEqual(self.store.tags(),[])
        e=w.open_device_editor(0);self.addCleanup(lambda:(setattr(e,'skip_close_prompt',True),e.close()))
        self.assertIs(e.tag_button.parentWidget(),e.workspace.cards['identity']);self.assertFalse(e.tag_button.isHidden())
        e.begin_edit();e.tag_values=['Büro'];e.refresh_tags();before=e.values()
        for lang in ('de','hu','en'):e.set_language(lang);e.set_details(True);e.set_details(False);self.assertEqual(e.values(),before)
        self.assertTrue(e.save());self.assertEqual(self.store.devices()[0]['_tags'],['Büro'])
    def test_tag_creation_dialog_case_duplicate_and_selector_cancel(self):
        from PySide6.QtWidgets import QPushButton
        w=self.window
        def add_twice(dialog):
            button=next(b for b in dialog.findChildren(QPushButton) if b.text()=='Add tag…')
            with patch('PySide6.QtWidgets.QInputDialog.getText',return_value=('  Café  ',True)):button.click()
            dialog.list.item(0).setCheckState(Qt.Unchecked)
            with patch('PySide6.QtWidgets.QInputDialog.getText',return_value=('CAFÉ',True)):button.click()
            self.assertEqual(dialog.list.count(),1);self.assertEqual(dialog.selected(),['Café'])
            return QDialog.Rejected
        with patch.object(ChoiceDialog,'exec',add_twice):w.choose_tags()
        self.assertEqual(w.tag_values,[]);self.assertEqual(self.store.tags(),[])

    def test_tag_search_or_filter_column_and_no_assignment(self):
        a=self.add(tags=['Büro','Critical']);b=self.add('Fictional b',tags=['Spare']);c=self.add('Fictional c');w=self.window;w.reload()
        self.assertIn('tags',KEYS);self.assertEqual(values(c,'tags'),['']);self.assertTrue(matches(a,{'tags':['Spare','Critical']}));self.assertFalse(matches(a,{'tags':['Spare'],'name':['Fictional device']}));self.assertTrue(matches(c,{'tags':['']}))
        w.search.setText('büro');self.assertEqual(sum(not w.table.isRowHidden(i) for i in range(w.table.rowCount())),1)
        w.search.clear();w.list_controller.view['filters']={'tags':['Critical','Spare']};w.list_controller.render();self.assertEqual(sum(not w.table.isRowHidden(i) for i in range(w.table.rowCount())),2)
    def test_tags_full_restore_export_and_delete_snapshot(self):
        a=self.add(tags=['Fictional Büro']);bundle=self.root/'bundle.zip';backup_bundle(self.db,bundle);target=restore(bundle,self.root/'restored')
        self.assertEqual(DeviceStore(target/'hardware.sqlite3').devices()[0]['_tags'],a['_tags'])
        folder=self.root/'export';subprocess.run([sys.executable,str(test_desktop.BASE/'inventory.py'),'--db',str(self.db),'export','--directory',str(folder)],check=True,capture_output=True)
        exported=json.loads((folder/'inventory.json').read_text());self.assertEqual(exported['tag_choices'][0]['label'],'Fictional Büro');self.assertEqual(len(exported['device_tags']),1)
        restored=self.root/'sql.sqlite3'
        with contextlib.closing(sqlite3.connect(restored)) as c:c.executescript((folder/'inventory.sql').read_text())
        self.assertEqual(DeviceStore(restored).devices()[0]['_tags'],a['_tags'])
        self.store.delete(a)
        with contextlib.closing(self.store.connect()) as c:
            snapshot=json.loads(c.execute('SELECT snapshot_json FROM deleted_devices').fetchone()[0]);self.assertEqual(len(snapshot['device_tags']),1);self.assertTrue(snapshot['device_tag_history'])
        self.assertEqual(self.store.tags(),['Fictional Büro'])
    def test_managed_migration_25_preserves_uuid_backup_locks_rollback(self):
        db=self.root/'old.sqlite3';schema=(test_desktop.BASE/'schema.sql').read_text().split('CREATE TABLE tag_choices')[0]+'PRAGMA user_version=25; COMMIT;'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript(schema);c.execute("INSERT INTO devices(device_id,name,source) VALUES('legacy','Fictional existing','FICTIONAL')");c.commit();before=c.execute('SELECT * FROM devices').fetchall();labels=c.execute('SELECT * FROM device_short_ids').fetchall()
        source=self.root/'release-source';source.mkdir()
        for file in ('schema.sql','ui_i18n.py'):shutil.copyfile(test_desktop.BASE/file,source/file)
        shutil.copytree(test_desktop.BASE/'migrations',source/'migrations')
        release=publish(source,run_tests=False)
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.execute('BEGIN IMMEDIATE')
            with self.assertRaises(sqlite3.OperationalError):prepare_database(db,release)
            c.rollback()
        with patch('inventory.check',side_effect=ValueError('forced invariant failure')):
            with self.assertRaises(ValueError):prepare_database(db,release)
        with contextlib.closing(sqlite3.connect(db)) as c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],25)
        backup=prepare_database(db,release)
        with contextlib.closing(sqlite3.connect(db)) as c:
            self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before);self.assertEqual(c.execute('SELECT * FROM device_short_ids').fetchall(),labels);self.assertEqual(c.execute('SELECT count(*) FROM tag_choices').fetchone()[0],0)
        with zipfile.ZipFile(backup) as z:
            old=self.root/'backup.sqlite3';old.write_bytes(z.read('hardware.sqlite3'))
        with contextlib.closing(sqlite3.connect(old)) as c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],25)
        self.assertEqual(DeviceStore(db).devices()[0]['_tags'],[])
