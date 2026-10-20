"""Bundled installer data isolation and exact uninstall scope."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from windows_start import workspace_status,selected_workspace,startup_plan,child_environment
from tools.build_windows_installer import installer_script,nsis_quote,build_payload

class WindowsInstaller(unittest.TestCase):
    def test_partial_workspace_is_retained_and_not_adopted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source';source.mkdir();target=root/'failed';target.mkdir();original=target/'original.png';original.write_bytes(b'fictional diagnostic')
            self.assertEqual(workspace_status(target),'blocked')
            with self.assertRaisesRegex(ValueError,'left unchanged'):startup_plan(source,target)
            self.assertEqual(original.read_bytes(),b'fictional diagnostic')
            self.assertFalse((target/'INSTALLATION.json').exists())

    def test_new_inventory_plan_runs_full_initialization_then_channel(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source';source.mkdir();target=root/'new'
            self.assertEqual(startup_plan(source,target,True),[['init','--workspace',str(target.resolve())],['test','--workspace',str(target.resolve())]])
            self.assertFalse(target.exists())

    def test_existing_workspace_never_syncs_publishes_or_promotes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source';source.mkdir();target=root/'inventory';target.mkdir()
            for name in ('.hwi4u-workspace.json','INSTALLATION.json'):(target/name).write_text('{"format":1}')
            (target/'hardware.sqlite3').write_bytes(b'fictional sentinel')
            self.assertEqual(workspace_status(target),'ready')
            self.assertEqual(startup_plan(source,target),[['run','--workspace',str(target.resolve())]])
            self.assertEqual((target/'hardware.sqlite3').read_bytes(),b'fictional sentinel')
            with self.assertRaises(ValueError):startup_plan(source,source/'inventory')

    def test_explicit_update_stages_only_test_and_preserves_production(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source';source.mkdir();target=root/'inventory';target.mkdir()
            for name in ('.hwi4u-workspace.json','INSTALLATION.json'):(target/name).write_text('{"format":1}')
            (target/'hardware.sqlite3').write_bytes(b'fictional sentinel')
            plan=startup_plan(source,target,update=True)
            self.assertEqual([x[0] for x in plan],['publish','test'])
            self.assertNotIn('promote',repr(plan));self.assertNotIn('refresh-test',repr(plan))

    def test_settings_missing_invalid_and_absolute_selection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);settings=root/'settings.json';target=root/'chosen'
            self.assertEqual(selected_workspace(settings,target),target)
            settings.write_text(json.dumps({'format':1,'workspace':str(target)}))
            self.assertEqual(selected_workspace(settings,root/'other'),target)
            settings.write_text('{"format":1,"workspace":"relative"}')
            with self.assertRaises(ValueError):selected_workspace(settings,target)
            settings.write_text('{')
            with self.assertRaises(ValueError):selected_workspace(settings,target)

    def test_external_environment_does_not_escape_bundle(self):
        env={'PATH':'keep','PYTHONHOME':'external','PYTHONPATH':'other','QT_PLUGIN_PATH':'other','QT_QPA_PLATFORM':'offscreen'}
        result=child_environment(env)
        self.assertEqual(env['PYTHONHOME'],'external')
        for key in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM'):self.assertNotIn(key,result)
        self.assertEqual(result['PYTHONNOUSERSITE'],'1');self.assertEqual(result['PATH'],'keep');self.assertEqual(result['PYTHONDONTWRITEBYTECODE'],'1')

    def test_uninstaller_deletes_manifest_files_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'INSTALL-MANIFEST.json').write_text(json.dumps({'sha256':{'app/main.py':'x','python/Lib/os.py':'x'}}))
            script=installer_script(root,root/'setup.exe','0.21.1')
            self.assertIn('RequestExecutionLevel user',script)
            self.assertIn('Delete "$INSTDIR\\app\\main.py"',script)
            self.assertNotIn('RMDir /r',script);self.assertNotIn('Delete "$LOCALAPPDATA',script)
            self.assertIn('pythonw.exe',script);self.assertIn('-E -s -B',script)
            self.assertNotIn('ExecWait',script)

    def test_nsis_injection_and_platform_guard(self):
        self.assertEqual(nsis_quote('x$y'),'x$$y')
        with self.assertRaises(ValueError):nsis_quote('x\nDelete something')
        with patch('sys.platform','linux'):
            with self.assertRaisesRegex(ValueError,'Windows x64'):build_payload('.',Path('never-created'))
