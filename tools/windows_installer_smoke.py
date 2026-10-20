"""Install, run and uninstall the actual Windows EXE with fictional data only."""
import argparse,contextlib,hashlib,json,os,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.windows_process_windows import windows_for_process


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--installer',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if sys.platform!='win32':raise ValueError('Actual Windows installer verification requires Windows.')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='hwi4u-exe-smoke-') as temp:
        root=Path(temp).resolve();installed=root/'installed HWI4U Ω';data=root/'fictional inventory';sentinel=root/'failed installation';sentinel.mkdir();(sentinel/'original.png').write_bytes(b'fictional retained diagnostic')
        env={k:v for k,v in os.environ.items() if k not in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QT_QPA_PLATFORM')}
        # Runtime launch must not find development Python/pip on PATH.
        env.update(PATH=str(Path(os.environ['WINDIR'])/'System32')+os.pathsep+os.environ['WINDIR'],PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PIP_NO_INDEX='1')
        command='"'+str(args.installer.resolve())+'" /S /D='+str(installed)
        subprocess.run(command,env=env,check=True,timeout=120)
        manifest=json.loads((installed/'INSTALL-MANIFEST.json').read_text())
        for name,digest in manifest['sha256'].items():assert hashlib.sha256((installed/name).read_bytes()).hexdigest()==digest,name
        unknown=installed/'leave-my-note.txt';unknown.write_text('fictional user file must survive uninstall')
        python=installed/'python/python.exe';app=installed/'app'
        probe=json.loads(subprocess.check_output([str(python),'-E','-s','-B','-c','import sys,json,PySide6;print(json.dumps([sys.prefix,PySide6.__file__]))'],cwd=app,env=env,text=True))
        assert Path(probe[0]).resolve()==installed/'python' and Path(probe[1]).resolve().is_relative_to(installed/'python')
        with (out/'bundled-full-tests.log').open('w',encoding='utf-8') as log:
            subprocess.run([str(python),'-E','-s','-B','-m','unittest','discover','-s','tests'],cwd=app,env={**env,'QT_QPA_PLATFORM':'offscreen','QT_QPA_FONTDIR':str(Path(os.environ['WINDIR'])/'Fonts')},stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        # Init uses every bundled test again through the real managed publication gate.
        with (out/'bundled-initialization.log').open('w',encoding='utf-8') as log:
            subprocess.run([str(python),'-E','-s','-B',str(app/'tools/windows_wizard_smoke.py'),'--workspace',str(data),'--output',str(out)],cwd=app,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        from windows_start import startup_plan
        try:startup_plan(app,sentinel)
        except ValueError:pass
        else:raise AssertionError('Partial installation was accepted')
        with contextlib.closing(sqlite3.connect(data/'hardware.sqlite3')) as c:
            assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not c.execute('PRAGMA foreign_key_check').fetchall()
            assert c.execute('SELECT count(*) FROM devices').fetchone()[0]==0
        db_hash=hashlib.sha256((data/'hardware.sqlite3').read_bytes()).hexdigest()
        with (out/'native-client.log').open('w',encoding='utf-8') as log:
            process=subprocess.Popen([str(installed/'python/pythonw.exe'),'-E','-s','-B',str(app/'windows_start.py'),'test','--workspace',str(data)],cwd=app,env=env,stdout=log,stderr=subprocess.STDOUT)
            try:
                windows=[];deadline=time.monotonic()+60
                while time.monotonic()<deadline:
                    assert process.poll() is None,'Bundled launcher exited before native TEST window.'
                    windows=windows_for_process(process.pid)
                    if windows:break
                    time.sleep(.05)
                assert windows,'No native TEST window from installed launcher.'
                assert (data/'test-environment/last-launch.json').is_file()
                import ctypes
                from ctypes import wintypes as W
                user=ctypes.WinDLL('user32',use_last_error=True);user.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
                assert user.PostMessageW(windows[0][0],0x0010,0,0)
                assert process.wait(timeout=30)==0
            finally:
                if process.poll() is None:subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
        # Running the uninstaller in-place spawns a temp copy; _?= makes this test
        # wait for the actual uninstall process before checking retained files.
        subprocess.run('"'+str(installed/'Uninstall.exe')+'" /S _?='+str(installed),env=env,check=True,timeout=120)
        assert not python.exists() and not (app/'windows_start.py').exists()
        assert unknown.read_text()=='fictional user file must survive uninstall'
        assert hashlib.sha256((data/'hardware.sqlite3').read_bytes()).hexdigest()==db_hash
        assert (sentinel/'original.png').read_bytes()==b'fictional retained diagnostic'
        report={'status':'passed','installer':args.installer.name,'version':manifest['version'],'actual_exe_install':True,'bundled_python_qt':True,'external_python_removed_from_PATH':True,'full_suite':'bundled-full-tests.log','fresh_init_full_gate':True,'actual_first_run_wizard_button':True,'native_TEST_from_installed_pythonw':True,'normal_close_exit':0,'actual_uninstall':True,'inventory_and_unknown_files_retained':True,'partial_installation_retained':True,'elapsed_seconds':time.monotonic()-start,'data':'disposable fictional only; no user inventory accessed','physical_Windows11_acceptance':'pending; hosted Windows2025 verification'}
        (out/'installer-smoke.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
