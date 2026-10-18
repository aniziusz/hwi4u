"""Fresh distribution/workspace setup without touching any user's inventory."""
import contextlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import test_desktop
from manage import initialize,synchronize_source,validate_target
from tools.check_distribution import check
from update_runtime import published

class Collaboration(unittest.TestCase):
    def test_fresh_workspace_empty_separate_and_existing_target_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'private';initialize(test_desktop.BASE,target,run_tests=False)
            with contextlib.closing(sqlite3.connect(target/'hardware.sqlite3')) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM devices').fetchone()[0],0)
                self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],23)
            from environments import current_dataset
            with contextlib.closing(sqlite3.connect(current_dataset(target)/'hardware.sqlite3')) as c:self.assertEqual(c.execute('SELECT count(*) FROM devices').fetchone()[0],0)
            self.assertEqual(published(target)[1]['release_id'],published(target,'test')[1]['release_id'])
            before=(target/'hardware.sqlite3').read_bytes()
            with self.assertRaises(FileExistsError):initialize(test_desktop.BASE,target,run_tests=False)
            self.assertEqual(before,(target/'hardware.sqlite3').read_bytes())
    def test_workspace_path_and_source_changes_protected(self):
        with self.assertRaises(ValueError):validate_target(test_desktop.BASE,test_desktop.BASE/'private')
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'private';initialize(test_desktop.BASE,target,run_tests=False)
            source=target/'inventory.py';source.write_text('# local customization\n')
            with self.assertRaisesRegex(ValueError,'edited'):synchronize_source(test_desktop.BASE,target)
            self.assertEqual(source.read_text(),'# local customization\n')
    def test_distribution_rejects_private_paths(self):
        for path in ('hardware.sqlite3','backups/a.zip','photos/a.png','.runtime/a.py','test-environment/data.json','a.db-wal','ui-settings.json','.env','a.pem'):
            with self.assertRaises(ValueError):check([path])
        check(['schema.sql','migrations/021-location.sql','tests/fixtures/schema-020.sql'])

    def test_portable_bundle_restores_to_new_directory_only(self):
        from photo_files import backup_bundle
        from tools.verify_bundle import restore
        from device_store import DeviceStore
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);db=root/'hardware.sqlite3'
            with contextlib.closing(sqlite3.connect(db)) as con:con.executescript((test_desktop.BASE/'schema.sql').read_text())
            DeviceStore(db).save(dict(name='fictional-device',source='FICTIONAL TEST'))
            bundle=root/'backup.zip';backup_bundle(db,bundle);dest=restore(bundle,root/'restore')
            self.assertEqual(DeviceStore(dest/'hardware.sqlite3').devices()[0]['name'],'fictional-device')
            with self.assertRaises(FileExistsError):restore(bundle,dest)
