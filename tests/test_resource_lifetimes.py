"""Assert closure even while an exception traceback still retains local variables."""
import contextlib,sqlite3,unittest
from unittest.mock import patch
import test_desktop
from device_store import DeviceStore
import inventory
from source_store import SourceStore
from photo_store import PhotoStore
from PySide6.QtGui import QImage

class ResourceLifetimes(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_busy_connection_setup_closes_before_error_is_released(self):
        real_connect=sqlite3.connect;created=[]
        def tracking(*args,**kwargs):
            c=real_connect(*args,**kwargs);created.append(c);return c
        with contextlib.closing(real_connect(self.db)) as writer:
            writer.execute('BEGIN EXCLUSIVE')
            with patch('inventory.sqlite3.connect',side_effect=tracking):
                with self.assertRaises(sqlite3.OperationalError):inventory.connect(self.db,readonly=True,timeout=0)
            self.assertEqual(len(created),1)
            with self.assertRaisesRegex(sqlite3.ProgrammingError,'closed'):created[0].execute('SELECT 1')
            writer.rollback()
    def test_wrong_schema_closes_before_exception_leaves_scope(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:c.execute('PRAGMA user_version=1')
        real_connect=sqlite3.connect;created=[]
        def tracking(*args,**kwargs):
            c=real_connect(*args,**kwargs);created.append(c);return c
        with patch('inventory.sqlite3.connect',side_effect=tracking):
            with self.assertRaisesRegex(ValueError,'Unsupported schema'):inventory.connect(db)
        with self.assertRaisesRegex(sqlite3.ProgrammingError,'closed'):created[0].execute('SELECT 1')
        db.unlink();self.assertFalse(db.exists())
    def test_photo_failure_preserves_foreign_key_error_and_releases_files(self):
        source=self.root/'input.png';image=QImage(16,16,QImage.Format_RGB32);image.fill(0x77bbcc);self.assertTrue(image.save(str(source)))
        try:PhotoStore(self.db).add('MISSING',source,'','FICTIONAL TEST')
        except sqlite3.IntegrityError as error:
            # Error/reader frames are still alive. Windows must permit deletion now.
            self.assertIn('FOREIGN KEY',str(error));source.unlink()
            self.assertEqual(list((self.root/'photos').iterdir()),[])
        else:self.fail('Expected the original FOREIGN KEY error.')
    def test_source_photo_backup_failure_releases_both_readers(self):
        source=self.root/'input.png';image=QImage(16,16,QImage.Format_RGB32);image.fill(0x77bbcc);self.assertTrue(image.save(str(source)))
        store=SourceStore(self.db)
        try:
            with patch.object(store,'_backup',side_effect=OSError('forced backup failure')):
                store.save(dict(kind='photo',title='FICTIONAL',evidence_status='uncertain'),source)
        except OSError as error:
            self.assertIn('forced backup',str(error));source.unlink()
            self.assertEqual(list((self.root/'sources').iterdir()),[])
        else:self.fail('Expected backup failure.')

    def test_offscreen_font_directory_uses_existing_os_fonts_only(self):
        from qt_test_environment import test_environment
        fonts=self.root/'Fonts';fonts.mkdir()
        base={'WINDIR':str(self.root),'KEEP':'unchanged'}
        with patch('qt_test_environment.sys.platform','win32'):
            result=test_environment(base);self.assertEqual(result['QT_QPA_FONTDIR'],str(fonts))
            custom=test_environment({**base,'QT_QPA_FONTDIR':'chosen/fonts'});self.assertEqual(custom['QT_QPA_FONTDIR'],'chosen/fonts')
        self.assertEqual(base,{'WINDIR':str(self.root),'KEEP':'unchanged'})
