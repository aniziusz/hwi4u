"""Test/prod isolation, snapshot failure atomicity and explicit promotion."""
import contextlib,json,os,shutil,sqlite3,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from update_runtime import publish,published,atomic_json,digest
from environments import refresh_test,current_dataset,launch_test,test_lock,record_test_launch,promote_test,validate_test_database
from device_store import DeviceStore
from desktop import Window
from test_desktop import APP,BASE

class Environments(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        for f in BASE.glob('*.py'):shutil.copyfile(f,self.root/f.name)
        shutil.copyfile(BASE/'schema.sql',self.root/'schema.sql');shutil.copyfile(BASE/'LICENSE-desktop.txt',self.root/'LICENSE-desktop.txt')
        shutil.copytree(BASE/'migrations',self.root/'migrations')
        (self.root/'tests').mkdir();(self.root/'tests/test_marker.py').write_text('import unittest\nclass Marker(unittest.TestCase):\n def test_fixture(self): self.assertTrue(True)\n')
        self.prod=self.root/'hardware.sqlite3'
        with contextlib.closing(sqlite3.connect(self.prod)) as c:
            c.executescript((BASE/'schema.sql').read_text());c.execute("INSERT INTO devices(device_id,name,source) VALUES('PROD','production','TEST ONLY')");c.commit()
        self.prod_release=publish(self.root,run_tests=False,channel='production')
        (self.root/'desktop.py').write_text((self.root/'desktop.py').read_text()+'\n# candidate fixture\n')
        self.test_release=publish(self.root,run_tests=False)
    def test_candidate_publication_and_test_edits_do_not_touch_production(self):
        before=self.prod.read_bytes();pointer=(self.root/'.runtime/current.json').read_bytes()
        db=refresh_test(self.root)
        self.assertEqual(published(self.root)[0],self.prod_release);self.assertEqual(published(self.root,'test')[0],self.test_release)
        store=DeviceStore(db);row=store.devices()[0];store.save({**row,'name':'TEST EDIT'},row)
        self.assertEqual(DeviceStore(self.prod).devices()[0]['name'],'production');self.assertEqual(self.prod.read_bytes(),before)
        self.assertEqual((self.root/'.runtime/current.json').read_bytes(),pointer)
        with self.assertRaises(ValueError):refresh_test(self.root)
        fresh=refresh_test(self.root,confirmed=True)
        self.assertNotEqual(fresh,db);self.assertTrue(db.exists());self.assertEqual(DeviceStore(db).devices()[0]['name'],'TEST EDIT')
        self.assertEqual(DeviceStore(fresh).devices()[0]['name'],'production')
    def test_live_production_connection_and_pending_writer(self):
        with contextlib.closing(sqlite3.connect(self.prod)) as browser:
            browser.execute('SELECT * FROM devices').fetchall();db=refresh_test(self.root)
            previous=(self.root/'test-environment/current.json').read_bytes()
            browser.execute('BEGIN IMMEDIATE');browser.execute("UPDATE devices SET name='pending'")
            with self.assertRaises(sqlite3.OperationalError):refresh_test(self.root,confirmed=True)
            self.assertEqual((self.root/'test-environment/current.json').read_bytes(),previous)
            browser.commit();refresh_test(self.root,confirmed=True)
        self.assertEqual(DeviceStore(current_dataset(self.root)/'hardware.sqlite3').devices()[0]['name'],'pending')
    def test_refresh_is_blocked_during_test_session_and_override_refused(self):
        db=refresh_test(self.root)
        with test_lock(self.root):
            with self.assertRaises(ValueError):refresh_test(self.root,confirmed=True)
        with self.assertRaises(ValueError):launch_test(self.root,['--db',str(self.prod)])
        with self.assertRaises(ValueError):launch_test(self.root,['--db='+str(self.prod)])
        with self.assertRaises(ValueError):validate_test_database(self.root,self.prod)
        from update_runtime import supervise as direct_supervise
        with self.assertRaises(ValueError):direct_supervise(self.root,['--db',str(self.prod)],channel='test')
        with patch('environments.supervise',return_value=0) as supervise:
            self.assertEqual(launch_test(self.root,[]),0)
            self.assertEqual(supervise.call_args.kwargs['channel'],'test');self.assertEqual(Path(supervise.call_args.args[1][1]),db)
    def test_attachment_copy_is_independent_and_missing_files_preserve_pointer(self):
        folder=self.root/'manuals'/('a'*32);folder.mkdir(parents=True);content=b'%PDF-1.4 TEST ONLY';file=folder/'document.pdf';file.write_bytes(content)
        with contextlib.closing(sqlite3.connect(self.prod)) as c:
            c.execute("INSERT INTO device_manuals(reference_id,device_id,title,kind,relative_path,original_name,sha256,source) VALUES(?,?,'test','local',?,'test.pdf',?,'TEST ONLY')",('a'*32,'PROD',str(file.relative_to(self.root)),digest(content)));c.commit()
        db=refresh_test(self.root);copied=db.parent/file.relative_to(self.root)
        self.assertEqual(copied.read_bytes(),content);self.assertNotEqual(copied.stat().st_ino,file.stat().st_ino)
        copied.write_bytes(b'test changed');self.assertEqual(file.read_bytes(),content)
        pointer=(self.root/'test-environment/current.json').read_bytes();file.unlink()
        with self.assertRaises(OSError):refresh_test(self.root,confirmed=True)
        self.assertEqual((self.root/'test-environment/current.json').read_bytes(),pointer)
    def test_promotion_requires_acceptance_candidate_launch_and_passed_checks(self):
        db=refresh_test(self.root);ident=self.test_release.name;before=self.prod.read_bytes()
        with self.assertRaises(ValueError):promote_test(self.root,ident)
        with self.assertRaises(FileNotFoundError):promote_test(self.root,ident,accepted=True)
        record_test_launch(self.root,db,ident)
        with patch('environments.subprocess.run',return_value=subprocess.CompletedProcess([],1,stdout='',stderr='TEST FAILURE')):
            with self.assertRaises(ValueError):promote_test(self.root,ident,accepted=True)
        self.assertEqual(published(self.root)[0],self.prod_release)
        # A tiny isolated fixture suite runs here; never recursively run the full suite.
        promote_test(self.root,ident,accepted=True)
        self.assertEqual(published(self.root)[0],self.test_release);self.assertEqual(self.prod.read_bytes(),before)
    def test_test_banner_and_channel_updates_keep_production_pointer_separate(self):
        db=refresh_test(self.root)
        env={'INVENTORY_CHANNEL':'test','INVENTORY_PROJECT_ROOT':str(self.root),'INVENTORY_RELEASE_ID':self.test_release.name}
        with patch.dict(os.environ,env):
            w=Window(DeviceStore(db));self.addCleanup(w.deleteLater)
            self.assertEqual(w.windowTitle(),'HWI4U TEST');self.assertTrue(w.update_button.isHidden())
            atomic_json(self.root/'.runtime/test.json',{'release_id':'candidate-new'})
            w.check_update();self.assertFalse(w.update_button.isHidden())
            values=w.values()
            for code in ('de','hu','en'):w.set_language(code);self.assertEqual(w.values(),values);self.assertEqual(w.windowTitle(),'HWI4U TEST')
    def test_failure_during_copy_migration_keeps_existing_test_dataset(self):
        refresh_test(self.root);pointer=(self.root/'test-environment/current.json').read_bytes()
        with patch('environments.subprocess.run',return_value=subprocess.CompletedProcess([],1,stdout='',stderr='bad migration')):
            with self.assertRaises(ValueError):refresh_test(self.root,confirmed=True)
        self.assertEqual((self.root/'test-environment/current.json').read_bytes(),pointer)

    def test_refresh_copies_source_assets_without_sharing_production_files(self):
        from source_store import SourceStore,asset_path
        pdf=self.root/'source.pdf';pdf.write_bytes(b'%PDF-1.4 TEST ONLY')
        ident=SourceStore(self.prod).save(dict(kind='document',title='test evidence',evidence_status='uncertain'),pdf)
        row=SourceStore(self.prod).list()[0];db=refresh_test(self.root)
        copied=asset_path(db.parent,row['relative_path']);original=asset_path(self.root,row['relative_path'])
        self.assertEqual(copied.read_bytes(),original.read_bytes());self.assertNotEqual(copied.stat().st_ino,original.stat().st_ino)
        copied.write_bytes(b'test change');self.assertTrue(original.read_bytes().startswith(b'%PDF-'))
