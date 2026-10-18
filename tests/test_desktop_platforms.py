"""Platform launchers, native architecture guards, paths and clean source packaging."""
import contextlib,os,plistlib,shlex,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import test_desktop
from install_desktop import validate_platform,make_mac_launcher,environment_python
from manage import default_workspace
from tools.package_source import package

class DesktopPlatforms(unittest.TestCase):
    def test_architecture_and_python_requirements(self):
        self.assertEqual(validate_platform('Darwin','arm64',(3,14)),'Darwin')
        self.assertEqual(validate_platform('Windows','AMD64',(3,14)),'Windows')
        for system,machine,version in [('Darwin','x86_64',(3,14)),('Windows','x86',(3,14)),('Windows','ARM64',(3,14)),('Darwin','arm64',(3,13))]:
            with self.assertRaises(ValueError):validate_platform(system,machine,version)
    def test_mac_bundle_quotes_paths_and_does_not_copy_data(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/"source space's folder";source.mkdir();dest=Path(t)/'HWI4U TEST.app';make_mac_launcher(source,dest,True)
            info=plistlib.loads((dest/'Contents/Info.plist').read_bytes());self.assertEqual(info['CFBundleIdentifier'],'org.hwi4u.test')
            script=(dest/'Contents/MacOS/hwi4u').read_text();command=shlex.split(script.split('exec ',1)[1]);self.assertEqual(command,[str(environment_python(source,'Darwin')),str(source/'desktop_start.py'),'test'])
            self.assertFalse(list(dest.rglob('*.sqlite3')))
            with self.assertRaises(FileExistsError):make_mac_launcher(source,dest)
    def test_default_data_paths(self):
        self.assertEqual(default_workspace('darwin'),Path.home()/'Library/Application Support/HWI4U')
        with patch.dict(os.environ,{'LOCALAPPDATA':str(Path.home()/'local-app-test')}):self.assertEqual(default_workspace('win32'),Path.home()/'local-app-test/HWI4U')
        # Do not change os.name globally: pathlib selects a concrete path implementation from it.
        self.assertNotEqual(default_workspace().resolve(),test_desktop.BASE.resolve())
    def test_source_package_contains_launchers_and_no_runtime_or_private_files(self):
        with tempfile.TemporaryDirectory() as t:
            dest=package(test_desktop.BASE,Path(t)/'client.zip')
            with zipfile.ZipFile(dest) as archive:
                names=archive.namelist();self.assertIn('HWI4U/Install HWI4U.command',names);self.assertIn('HWI4U/Install HWI4U.cmd',names);self.assertIn('HWI4U/Start HWI4U TEST.cmd',names)
                self.assertFalse(any('/.runtime/' in n or '/.venv/' in n or n.endswith(('.sqlite3','.pdf','.png')) for n in names))
                self.assertEqual(archive.read('HWI4U/Install HWI4U.command').splitlines()[0],b'#!/bin/sh')
            with self.assertRaises(FileExistsError):package(test_desktop.BASE,dest)
    def test_cmd_files_have_real_line_breaks_and_utf8_mode(self):
        for name in ('launch-desktop.cmd','launch-test.cmd','Install HWI4U.cmd','Start HWI4U.cmd','Start HWI4U TEST.cmd'):
            data=(test_desktop.BASE/name).read_bytes();self.assertIn(b'\r\n',data);self.assertNotIn(b'\\r\\n',data);self.assertIn(b'PYTHONUTF8=1',data)
