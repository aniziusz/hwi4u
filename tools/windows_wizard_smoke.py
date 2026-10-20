"""Exercise the real first-run wizard with a new fictional workspace on Windows."""
import argparse,ctypes,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    assert sys.platform=='win32' and not args.workspace.exists()
    os.environ.pop('QT_QPA_PLATFORM',None)
    from PySide6.QtWidgets import QApplication,QPushButton
    from PySide6.QtCore import QTimer
    from tools.windows_process_windows import windows_for_process
    import windows_start
    app=QApplication([]);proof={'button_clicked':False,'native_window':False,'error':None};deadline=time.monotonic()+600
    def click():
        try:
            button=next(w for w in app.allWidgets() if isinstance(w,QPushButton) and w.text()=='Start HWI4U TEST')
            assert button.isEnabled();proof['button_clicked']=True;button.click()
        except Exception as exc:proof['error']=repr(exc);app.quit()
    def observe():
        try:
            if time.monotonic()>deadline:raise AssertionError('First-run wizard did not complete full initialization before deadline.')
            windows=windows_for_process(os.getpid())
            if not windows:return
            receipt=json.loads((args.workspace/'test-environment/last-launch.json').read_text());assert receipt['release_id']
            proof['native_window']=True;timer.stop()
            from ctypes import wintypes as W
            user=ctypes.WinDLL('user32',use_last_error=True);user.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
            assert user.PostMessageW(windows[0][0],0x0010,0,0)
        except Exception as exc:proof['error']=repr(exc);timer.stop();app.quit()
    timer=QTimer();timer.setInterval(100);timer.timeout.connect(observe);timer.start();QTimer.singleShot(0,click)
    result=windows_start.main(['test','--workspace',str(args.workspace)])
    assert result==0 and proof['button_clicked'] and proof['native_window'] and proof['error'] is None,proof
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'first-run-wizard.json').write_text(json.dumps(proof,indent=2)+'\n')
    return 0

if __name__=='__main__':sys.exit(main())
