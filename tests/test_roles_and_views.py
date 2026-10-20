"""Role history and presentation on disposable inventories; UUIDs survive view changes."""
import contextlib,json,sqlite3,unittest
from pathlib import Path
from unittest.mock import patch
import test_desktop
from list_view import values,matches,groups,ChoiceDialog,read_view,KEYS
from location_store import empty_location
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtCore import Qt,QEvent
from PySide6.QtTest import QTest

class RolesAndViews(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def add(self,name,roles=(),kind=None):
        data=dict(name=name,source='FICTIONAL TEST',roles=list(roles),device_type=kind);self.store.save(data)
        return next(r for r in self.store.devices() if r['device_id']==data['device_id'])
    def close_editors(self):
        for e in list(self.window.editors.values()):e.skip_close_prompt=True;e.close()
        QApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    def test_roles_history_conflict_backups_and_ids(self):
        row=self.add('router example',['firewall','router'],'firewall appliance');ids=row['device_id'],row['short_id'];self.assertEqual(row['_roles'],['firewall','router'])
        data={**row,'roles':['backup server']};self.store.save(data,row);updated=self.store.devices()[0];self.assertEqual((updated['device_id'],updated['short_id']),ids);self.assertEqual(updated['device_type'],row['device_type'])
        with self.assertRaisesRegex(ValueError,'Roles changed'):self.store.save({**row,'roles':['server']},row)
        with self.assertRaisesRegex(ValueError,'Unknown role'):self.store.save({**updated,'roles':['invented value']},updated)
        with contextlib.closing(self.store.connect()) as c:
            records=c.execute('SELECT before_json,after_json FROM device_role_history ORDER BY history_id').fetchall();self.assertEqual(json.loads(records[-1][0]),['firewall','router']);self.assertEqual(json.loads(records[-1][1]),['backup server'])
            with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM device_role_history')
        self.assertTrue(list((self.root/'backups').glob('before-device-save-*')))
        with patch('inventory.exclusive',side_effect=OSError('backup unavailable')):
            with self.assertRaises(OSError):self.store.save({**updated,'roles':[]},updated)
        self.assertEqual(self.store.devices()[0]['_roles'],['backup server'])
    def test_role_catalogue_and_delete_snapshot(self):
        self.assertEqual(self.store.add_role('  Custom   PURPOSE '),'custom purpose');self.assertEqual(self.store.add_role('custom purpose'),'custom purpose')
        row=self.add('test',['custom purpose']);self.store.delete(row)
        with contextlib.closing(self.store.connect()) as c:
            snapshot=json.loads(c.execute('SELECT snapshot_json FROM deleted_devices').fetchone()[0]);self.assertEqual(snapshot['device_roles'][0]['role'],'custom purpose');self.assertTrue(snapshot['device_role_history']);self.assertFalse(c.execute('SELECT * FROM device_roles').fetchall())
    def test_migration_22_preserves_devices_and_assigns_no_roles(self):
        # Fresh schema stripped back to the preceding version supplies a real 22→23 upgrade.
        db=self.root/'old.sqlite3';schema=(test_desktop.BASE/'schema.sql').read_text();schema=schema[:schema.index('CREATE TABLE role_choices')]+'PRAGMA user_version=22; COMMIT;'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript(schema);c.execute("INSERT INTO devices(device_id,name,source) VALUES('old','existing','FICTIONAL TEST')");c.commit();before=c.execute('SELECT * FROM devices').fetchall();labels=c.execute('SELECT * FROM device_short_ids').fetchall();c.executescript((test_desktop.BASE/'migrations/023-device-roles.sql').read_text());self.assertEqual(c.execute('SELECT * FROM devices').fetchall(),before);self.assertEqual(c.execute('SELECT * FROM device_short_ids').fetchall(),labels);self.assertEqual(c.execute('SELECT count(*) FROM device_roles').fetchone()[0],0);self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
    def test_filter_or_and_unknown_and_repeated_role_groups(self):
        a=self.add('a',['firewall','router'],'firewall appliance');b=self.add('b',['server'],'server');c=self.add('c')
        self.assertTrue(matches(a,{'roles':['firewall','server'],'type_group':['networking']}));self.assertFalse(matches(b,{'roles':['firewall','server'],'type_group':['networking']}));self.assertTrue(matches(c,{'roles':['']}));self.assertFalse(matches(a,{'roles':[]}));self.assertTrue(matches(a,{}))
        grouped=groups([a,b,c],['roles']);self.assertEqual(len(grouped),4);self.assertEqual(len({r['device_id'] for _,rs in grouped for r in rs}),3)
        location=empty_location();location.update(state='recorded',building='Example',floor='1');a['_location']=location;self.assertEqual(values(a,'building'),['Example'])
        dialog=ChoiceDialog('Filters',[('firewall','firewall'),('router','router')],None,allow_all=True);self.addCleanup(dialog.deleteLater);self.assertIsNone(dialog.selected());dialog.tick(False);self.assertEqual(dialog.selected(),[]);dialog.list.item(0).setCheckState(Qt.Checked);dialog.search.setText('router');self.assertEqual(dialog.selected(),['firewall']);dialog.unrestrict();self.assertIsNone(dialog.selected())
    def test_nested_group_headers_columns_sort_and_editor_uuid(self):
        self.add('z',['router','server']);self.add('a',['server']);w=self.window;w.reload();controller=w.list_controller
        controller.view['groups']=['roles','current_state'];controller.view['hidden']=['short_id'];controller.view['order']=KEYS[1:]+KEYS[:1];controller.render()
        self.assertIn('2 / 2',controller.summary.text());header=w.table.item(0,1);self.assertIn('Roles:',header.text());self.assertIsNone(controller.identity(0));controller.clicked(header);self.assertTrue(any(w.table.isRowHidden(i) for i in range(w.table.rowCount())));controller.clicked(w.table.item(0,1))
        n=next(i for i in range(w.table.rowCount()) if controller.identity(i) and controller.identity(i)['name']=='z');wanted=controller.identity(n)['device_id'];self.addCleanup(self.close_editors);editor=w.open_device_editor(n);self.assertEqual(editor.bound_device_id,wanted)
        editor.begin_edit();editor.inputs['name'].setText('changed');self.assertTrue(editor.save());self.assertEqual(next(r for r in self.store.devices() if r['device_id']==wanted)['name'],'changed')
        controller.persist();saved=read_view(controller.path);self.assertEqual(saved['order'],controller.view['order']);self.assertEqual(saved['groups'],['roles','current_state'])
    def test_workspace_reflow_navigation_language_and_pending_values(self):
        self.add('test',['firewall']);w=self.window;w.reload();self.addCleanup(self.close_editors);e=w.open_device_editor(0);space=e.workspace
        e.begin_edit();e.inputs['name'].setText('unsaved büro');before=e.values();counts=[]
        e.showNormal()
        for width in (900,1400,2300):
            e.resize(width,1000);QApplication.processEvents();QTest.qWait(40);space.tiles.reflow();counts.append(space.tiles.columns);self.assertEqual(e.values(),before)
        self.assertEqual(counts,[1,2,4]);self.assertFalse(w.table.isHidden())
        for key,item in space.items.items():space.tree.setCurrentItem(item);self.assertFalse(space.cards[key].isHidden());self.assertEqual(e.values(),before)
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(e.values(),before)
        self.assertIs(e.role_button.parentWidget(),space.cards['identity']);self.assertTrue(e.save());self.assertEqual(self.store.devices()[0]['_roles'],['firewall'])
