"""Sources, migration, evidence retention, scope conflicts and file recovery."""
import contextlib,json,sqlite3,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
import test_desktop
from source_store import SourceStore,SCOPES,load_links,asset_path
from source_ui import SourceLibrary,SourceEditor
from device_store import DeviceStore
from manual_store import ManualStore
from photo_files import backup_bundle,sha256
from desktop import OptionalDate
import inventory

BASE=test_desktop.BASE
class Sources(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def entry(self,title='observation'):
        return SourceStore(self.db).save(dict(kind='observation',title=title,body='I read the actual label. TEST ONLY',evidence_status='user_reported'))
    def links(self,**values):return {k:values.get(k,[]) for k in SCOPES}
    def test_multi_scope_reuse_generates_real_citations_and_keeps_legacy_notes(self):
        w=self.window;one=self.entry('label');two=SourceStore(self.db).save(dict(kind='website',title='manufacturer reference',url='https://example.org/model',evidence_status='uncertain'))
        w.inputs['name'].setText('test device');w.source_selectors['device'].load([one,two]);w.source_selectors['software'].load([one])
        w.software_panel.os_status.setCurrentIndex(w.software_panel.os_status.findData('recorded'));w.software_panel.name.setText('TEST OS')
        self.assertTrue(w.save());row=self.store.devices()[0];self.assertIn('[source:'+one+']',row['source']);self.assertEqual(row['_sources']['device'],sorted([one,two]));self.assertIn(one,row['_software']['source'])
        original=row;data={**row,'source':'Preserved original text','sources':self.links(device=[two])};self.store.save(data,original)
        row=self.store.devices()[0];self.assertEqual(row['source'],'Preserved original text')
        self.store.save(dict(name='other device',source='TEST ONLY',sources=self.links(device=[one])))
        self.assertEqual(len(SourceStore(self.db).list()),2)
    def test_immutable_revisions_and_assignment_history_conflicts(self):
        ident=self.entry();self.store.save(dict(name='one',source='TEST ONLY',sources=self.links(device=[ident])))
        original=self.store.devices()[0];old=SourceStore(self.db).list()[0]
        revised=SourceStore(self.db).save({**old,'title':'corrected title'},original=old)
        self.assertNotEqual(revised,ident);self.assertEqual(self.store.devices()[0]['_sources']['device'],[ident])
        self.store.save({**original,'sources':self.links(device=[revised])},original)
        with self.assertRaisesRegex(ValueError,'Source assignments changed'):self.store.save({**original,'sources':self.links(device=[ident])},original)
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM source_link_history').fetchone()[0],2)
            with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM source_entries WHERE source_id=?',(ident,))
            with self.assertRaises(sqlite3.IntegrityError):c.execute("UPDATE source_entries SET title='overwrite' WHERE source_id=?",(ident,))
    def test_local_sources_reuse_revision_and_portable_backup_restore(self):
        store=SourceStore(self.db);pdf=self.root/'invoice.pdf';pdf.write_bytes(b'%PDF-1.4 TEST ONLY')
        doc=store.save(dict(kind='document',title='invoice',evidence_status='uncertain'),pdf)
        image=self.root/'label.png';pic=QImage(12,8,QImage.Format_RGB32);pic.fill(Qt.white);pic.save(str(image))
        photo=store.save(dict(kind='photo',title='label',evidence_status='user_reported'),image)
        self.store.save(dict(name='device',source='TEST ONLY',sources=self.links(device=[doc,photo])))
        old=next(r for r in store.list() if r['source_id']==doc);new=store.save({**old,'title':'invoice revision'},original=old)
        self.assertEqual(next(r for r in store.list() if r['source_id']==new)['relative_path'],old['relative_path'])
        output=self.root/'full.zip';backup_bundle(self.db,output)
        restored=self.root/'restore'
        with zipfile.ZipFile(output) as z:z.extractall(restored)
        with contextlib.closing(inventory.connect(restored/'hardware.sqlite3')) as c:inventory.check(c)
        for row in store.list():self.assertEqual(sha256(asset_path(restored,row['relative_path'])),row['sha256'])
        asset_path(self.root,old['relative_path']).write_bytes(b'changed')
        with self.assertRaises(ValueError):backup_bundle(self.db,self.root/'bad.zip')
    def test_reuse_existing_manual_keeps_one_file_and_provenance(self):
        self.store.save(dict(name='one',source='TEST ONLY'));device=self.store.devices()[0]['device_id']
        pdf=self.root/'manual.pdf';pdf.write_bytes(b'%PDF-1.4 TEST ONLY');ManualStore(self.db).save(device,'local',dict(title='M'*240,source='manufacturer TEST ONLY'),pdf)
        kind,row=SourceStore(self.db).reusable(device)[0];ident=SourceStore(self.db).import_existing(kind,row)
        self.assertEqual(SourceStore(self.db).import_existing(kind,row),ident)
        entry=SourceStore(self.db).list()[0];self.assertEqual(entry['relative_path'],row['relative_path']);self.assertEqual(entry['source_note'],row['source']);self.assertIsNone(entry['observed_on']);self.assertEqual(entry['evidence_status'],'uncertain')
        self.assertEqual(len(entry['title']),200);self.assertIn('M'*240,entry['body'])
        revision=SourceStore(self.db).save({**entry,'title':'revised manual'},original=entry)
        self.assertNotEqual(revision,ident)
        self.assertFalse((self.root/'sources').exists())
        ManualStore(self.db).detach(row);backup_bundle(self.db,self.root/'still-backed-up.zip')
    def test_migration_preserves_exact_text_and_every_old_table(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((BASE/'tests/fixtures/schema-018.sql').read_text())
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('one','one',?),('two','two',?)",('Árvíz\nOriginal SOURCE','Árvíz\nOriginal SOURCE'));c.commit()
            tables=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")];before={t:c.execute('SELECT * FROM '+t).fetchall() for t in tables}
            c.executescript((BASE/'migrations/019-source-library.sql').read_text())
            c.executescript((BASE/'migrations/020-network-links.sql').read_text())
            c.executescript((BASE/'migrations/021-location.sql').read_text());c.executescript((BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((BASE/'migrations/023-device-roles.sql').read_text())
            for table,rows in before.items():self.assertEqual([tuple(r[:-1]) if table=='devices' else r for r in c.execute('SELECT * FROM '+table).fetchall()],rows,table)
            self.assertEqual(c.execute('SELECT body FROM source_entries').fetchall(),[('Árvíz\nOriginal SOURCE',)])
            self.assertEqual(c.execute('SELECT kind FROM source_entries').fetchone()[0],'legacy_text')
            self.assertEqual(c.execute('SELECT observed_on,evidence_status FROM source_entries').fetchall(),[(None,'uncertain')]);self.assertEqual(c.execute('SELECT count(*) FROM source_links').fetchone()[0],2)
            inventory.check(c)
    def test_bad_evidence_fails_atomically_and_files_are_cleaned(self):
        store=SourceStore(self.db)
        for data in [dict(kind='website',title='bad',url='https://user:password@example.org',evidence_status='uncertain'),dict(kind='observation',title='empty',body='',evidence_status='uncertain'),dict(kind='observation',title='bad verified',body='TEST',evidence_status='verified')]:
            with self.assertRaises(ValueError):store.save(data)
        pdf=self.root/'test.pdf';pdf.write_bytes(b'%PDF-1.4 TEST ONLY')
        with patch.object(store,'_backup',side_effect=OSError('backup failure')):
            with self.assertRaises(OSError):store.save(dict(kind='document',title='test',evidence_status='uncertain'),pdf)
        self.assertEqual(store.list(),[]);self.assertEqual(list((self.root/'sources').iterdir()),[])
        with self.assertRaises(ValueError):self.store.save(dict(name='no save',source='TEST',sources=self.links(device=['missing'])))
        self.assertEqual(self.store.devices(),[])
        with self.assertRaises(ValueError):asset_path(self.root,'sources/../secret')
    def test_selector_languages_cancel_and_filter_keep_values(self):
        ident=self.entry('New device');w=self.window;w.inputs['name'].setText('unchanged');w.source_selectors['device'].load([ident]);before=w.values()
        for lang in ('de','hu','en'):w.set_language(lang);self.assertEqual(w.values(),before);self.assertEqual(w.source_selectors['device'].summary.text(),'New device')
        library=SourceLibrary(SourceStore(self.db),OptionalDate,[ident]);self.addCleanup(library.deleteLater);library.search.setText('not present');self.assertEqual(library.selection(),[ident])
        with patch('source_ui.SourceLibrary.exec',return_value=0):w.source_selectors['device'].choose()
        self.assertEqual(w.values(),before)
    def test_deletion_archives_links_but_retains_shared_library(self):
        ident=self.entry();self.store.save(dict(name='one',source='TEST',sources=self.links(device=[ident])));row=self.store.devices()[0];self.store.delete(row)
        self.assertEqual(len(SourceStore(self.db).list()),1)
        with contextlib.closing(self.store.connect()) as c:
            archive=json.loads(c.execute('SELECT snapshot_json FROM deleted_devices').fetchone()[0]);self.assertEqual(len(archive['source_links']),1);self.assertEqual(len(archive['source_link_history']),1);self.assertEqual(c.execute('SELECT count(*) FROM source_links').fetchone()[0],0)

    def test_attachment_hash_checks_open_and_locked_snapshot(self):
        from source_ui import open_source
        from update_runtime import full_snapshot_locked
        pdf=self.root/'source.pdf';pdf.write_bytes(b'%PDF-1.4 TEST ONLY');store=SourceStore(self.db)
        store.save(dict(kind='document',title='evidence',evidence_status='uncertain'),pdf);row=store.list()[0]
        with patch('source_ui.QDesktopServices.openUrl',return_value=True) as opened:open_source(self.window,store,row);self.assertTrue(opened.call_args[0][0].isLocalFile())
        with contextlib.closing(self.store.connect()) as c:
            c.execute('BEGIN IMMEDIATE');output=self.root/'locked.zip';full_snapshot_locked(self.db,output);c.rollback()
        with zipfile.ZipFile(output) as z:self.assertIn(row['relative_path'],z.namelist())
        asset_path(self.root,row['relative_path']).write_bytes(b'tampered')
        with patch('source_ui.QDesktopServices.openUrl') as opened,patch('source_ui.QMessageBox.warning') as warning:
            open_source(self.window,store,row);opened.assert_not_called();warning.assert_called_once()
        with self.assertRaises(ValueError):full_snapshot_locked(self.db,self.root/'bad-locked.zip')
    def test_source_based_connectivity_and_network_keep_verification_rules(self):
        w=self.window;ident=self.entry();w.inputs['name'].setText('source based');w.source_selectors['device'].load([ident])
        panel=w.connection_panels['interface'];panel.supported.setCurrentIndex(panel.supported.findData('none'));panel.usage.setCurrentIndex(panel.usage.findData('none'));w.source_selectors['interface'].load([ident]);panel.update_warning();self.assertEqual(panel.warning.text(),'')
        w.network_panel.hostname.setText('device.example');w.source_selectors['network'].load([ident]);w.network_panel.evidence.setCurrentIndex(w.network_panel.evidence.findData('verified'))
        with patch('desktop.QMessageBox.warning'):self.assertFalse(w.save())
        w.network_panel.evidence.setCurrentIndex(w.network_panel.evidence.findData('user_reported'));self.assertTrue(w.save())
        row=self.store.devices()[0];self.assertIn(ident,row['_network']['source']);self.assertIn(ident,row['_connectivity']['interface']['source'])

    def test_editor_buttons_are_explicit_in_all_languages_and_save_observation(self):
        from ui_i18n import install
        for code,expected in [('en','Save source'),('de','Quelle speichern'),('hu','Forrás mentése')]:
            install(code);editor=SourceEditor(SourceStore(self.db),OptionalDate);self.addCleanup(editor.deleteLater)
            self.assertEqual(editor.save_button.text(),expected)
            editor.kind.setCurrentIndex(editor.kind.findData('observation'));editor.title.setText('Actual observation '+code);editor.body.setPlainText('TEST ONLY observation');editor.save_button.click();self.assertIsNotNone(editor.saved_id)
        install('en');self.assertEqual(len(SourceStore(self.db).list()),3)
