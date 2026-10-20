#!/usr/bin/env python3
"""Fresh initialization with its full gate, then native managed TEST startup on Windows."""
import argparse,contextlib,json,os,platform,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))


def windows_for_process(parent):
    """Only windows belonging to this smoke process's descendants; never another client."""
    import ctypes
    from ctypes import wintypes as W
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);user=ctypes.WinDLL('user32',use_last_error=True)
    class Entry(ctypes.Structure):
        _fields_=[('dwSize',W.DWORD),('cntUsage',W.DWORD),('th32ProcessID',W.DWORD),('th32DefaultHeapID',ctypes.c_size_t),('th32ModuleID',W.DWORD),('cntThreads',W.DWORD),('th32ParentProcessID',W.DWORD),('pcPriClassBase',W.LONG),('dwFlags',W.DWORD),('szExeFile',W.WCHAR*260)]
    kernel.CreateToolhelp32Snapshot.restype=W.HANDLE;kernel.CreateToolhelp32Snapshot.argtypes=[W.DWORD,W.DWORD]
    kernel.Process32FirstW.argtypes=[W.HANDLE,ctypes.POINTER(Entry)];kernel.Process32NextW.argtypes=kernel.Process32FirstW.argtypes;kernel.CloseHandle.argtypes=[W.HANDLE]
    snapshot=kernel.CreateToolhelp32Snapshot(2,0)
    if snapshot==ctypes.c_void_p(-1).value:raise OSError(ctypes.get_last_error(),'Process snapshot failed')
    parents={};entry=Entry();entry.dwSize=ctypes.sizeof(Entry)
    try:
        valid=kernel.Process32FirstW(snapshot,ctypes.byref(entry))
        while valid:
            parents[entry.th32ProcessID]=entry.th32ParentProcessID;valid=kernel.Process32NextW(snapshot,ctypes.byref(entry))
    finally:kernel.CloseHandle(snapshot)
    descendants={parent}
    while True:
        updated=descendants|{pid for pid,ppid in parents.items() if ppid in descendants}
        if updated==descendants:break
        descendants=updated
    callback=ctypes.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM);found=[]
    user.GetWindowTextW.argtypes=[W.HWND,W.LPWSTR,ctypes.c_int];user.GetWindowThreadProcessId.argtypes=[W.HWND,ctypes.POINTER(W.DWORD)];user.IsWindowVisible.argtypes=[W.HWND];user.EnumWindows.argtypes=[callback,W.LPARAM]
    @callback
    def visit(hwnd,_):
        pid=W.DWORD();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if pid.value in descendants and user.IsWindowVisible(hwnd):
            title=ctypes.create_unicode_buffer(512);user.GetWindowTextW(hwnd,title,512)
            if title.value=='HWI4U TEST':found.append((hwnd,pid.value))
        return True
    user.EnumWindows(visit,0);return found


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    from qt_test_environment import test_environment
    start=time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='hwi4u-windows-startup-') as tmp:
        workspace=Path(tmp)/'new fictional workspace';log=output/'initialization.log'
        result=subprocess.run([sys.executable,str(ROOT/'manage.py'),'init','--workspace',str(workspace)],env=test_environment(),capture_output=True,text=True)
        log.write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,log.read_text(encoding='utf-8')
        from environments import current_dataset
        from update_runtime import published
        db=current_dataset(workspace)/'hardware.sqlite3';selection=published(workspace,'test');assert selection[1]['version']=='0.13.1'
        with contextlib.closing(sqlite3.connect(db)) as c:
            assert c.execute('SELECT count(*) FROM devices').fetchone()[0]==0
            assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert (workspace/'INSTALLATION.json').is_file()
        duplicate=subprocess.run([sys.executable,str(ROOT/'manage.py'),'init','--workspace',str(workspace)],capture_output=True,text=True);assert duplicate.returncode!=0
        os.environ['QT_QPA_PLATFORM']='windows' if sys.platform=='win32' else 'offscreen'
        from PySide6.QtWidgets import QApplication
        app=QApplication.instance() or QApplication([])
        if sys.platform=='win32':
            stdout=output/'managed-test-start.log'
            with stdout.open('w',encoding='utf-8') as handle:
                process=subprocess.Popen([sys.executable,str(ROOT/'manage.py'),'test','--workspace',str(workspace)],env={**os.environ,'QT_QPA_PLATFORM':'windows'},stdout=handle,stderr=subprocess.STDOUT)
                try:
                    deadline=time.monotonic()+30;windows=[]
                    while time.monotonic()<deadline:
                        assert process.poll() is None,'Managed startup exited before showing the TEST window.'
                        windows=windows_for_process(process.pid)
                        if windows:break
                        app.processEvents();time.sleep(0.05) # condition polling, not a fixed startup assumption
                    assert windows,'No native TEST window before the failure deadline.'
                    receipt=json.loads((workspace/'test-environment/last-launch.json').read_text());assert receipt['release_id']==selection[1]['release_id'];assert receipt['dataset']==db.parent.name
                    screenshot=app.primaryScreen().grabWindow(int(windows[0][0]));assert not screenshot.isNull();assert screenshot.save(str(output/'native-test-client.png'))
                    import ctypes
                    from ctypes import wintypes as W
                    user=ctypes.WinDLL('user32',use_last_error=True);user.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
                    assert user.PostMessageW(windows[0][0],0x0010,0,0)
                    assert process.wait(timeout=20)==0
                finally:
                    if process.poll() is None:subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
            assert 'Cannot find font directory' not in stdout.read_text(encoding='utf-8')
            method='manage.py test -> managed supervisor -> native Windows window -> normal WM_CLOSE'
        else:
            # Linux regression uses the same TEST form with the offscreen Qt plugin.
            os.environ.update(INVENTORY_CHANNEL='test',INVENTORY_PROJECT_ROOT=str(workspace),INVENTORY_RELEASE_ID=selection[1]['release_id'])
            from desktop import Window
            from device_store import DeviceStore
            from PySide6.QtCore import QEvent
            window=Window(DeviceStore(db),language='en');window.show();app.processEvents();assert window.isVisible() and window.windowTitle()=='HWI4U TEST'
            assert window.grab().save(str(output/'offscreen-test-client.png'));window.close();window.deleteLater();app.sendPostedEvents(None,QEvent.DeferredDelete)
            method='fresh initialized TEST dataset -> offscreen Window; managed native path is Windows-only'
        report=dict(system=platform.system(),python=platform.python_version(),qt=__import__('PySide6').__version__,fresh_init_full_gate=True,existing_folder_refused=True,test_window=True,method=method,elapsed_seconds=time.perf_counter()-start,data='new empty fictional workspace; user failed installation not accessed')
        (output/'startup.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
    return 0

if __name__=='__main__':sys.exit(main())
