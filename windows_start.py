"""First-run wizard for the bundled Windows client; never adopts partial data."""
import argparse
import json
import os
from pathlib import Path
import sys


def workspace_status(target):
    """An existing path is usable only with complete managed-install metadata."""
    target=Path(target)
    if not target.exists():return 'new'
    if target.is_symlink():return 'blocked'
    try:
        marker=json.loads((target/'.hwi4u-workspace.json').read_text())
        installation=json.loads((target/'INSTALLATION.json').read_text())
        if marker.get('format')==installation.get('format')==1 and (target/'hardware.sqlite3').is_file():return 'ready'
    except (OSError,ValueError,TypeError):pass
    return 'blocked'


def selected_workspace(settings,default):
    path=Path(settings)
    if not path.exists():return Path(default)
    value=json.loads(path.read_text())
    target=Path(value['workspace'])
    if value.get('format')!=1 or not target.is_absolute():raise ValueError('Invalid launcher settings; original data was not changed.')
    return target


def startup_plan(source,target,test=False,update=False):
    import manage
    source=Path(source).resolve()
    if Path(target).is_symlink():raise ValueError('Symbolic-link data folders are not supported.')
    target=manage.validate_target(source,target)
    state=workspace_status(target)
    if state=='blocked':raise ValueError('This folder already exists but is not a completed HWI4U installation. It was left unchanged. Choose a NEW folder, or an existing completed workspace.')
    if update:return [[('init' if state=='new' else 'publish'),'--workspace',str(target)],['test','--workspace',str(target)]]
    return [['init','--workspace',str(target)],['test' if test else 'run','--workspace',str(target)]] if state=='new' else [['test' if test else 'run','--workspace',str(target)]]


def child_environment(base=None):
    env=dict(os.environ if base is None else base)
    # An external Python/Qt configuration must not redirect the installed runtime.
    for key in ('PYTHONHOME','PYTHONPATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QT_QPA_PLATFORM','QT_QPA_FONTDIR'):
        env.pop(key,None)
    env.update(PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
    if sys.platform=='win32' and env.get('WINDIR'):
        fonts=Path(env['WINDIR'])/'Fonts'
        if fonts.is_dir():env['QT_QPA_FONTDIR']=str(fonts)
    return env


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('channel',nargs='?',choices=('production','test','update'),default='production')
    parser.add_argument('--workspace',type=Path,help='Advanced explicit data folder; does not persist the launcher setting.')
    args=parser.parse_args(argv)
    source=Path(__file__).resolve().parent
    import manage
    from update_runtime import atomic_json
    from PySide6.QtCore import QProcess,QProcessEnvironment,QTimer
    from PySide6.QtWidgets import QApplication,QDialog,QVBoxLayout,QLabel,QPushButton,QHBoxLayout,QFileDialog,QMessageBox,QProgressBar,QInputDialog
    app=QApplication.instance() or QApplication([])
    settings=manage.default_workspace().parent/'HWI4U-launcher.json'
    try:target=args.workspace or selected_workspace(settings,manage.default_workspace())
    except (OSError,ValueError,KeyError) as exc:
        QMessageBox.critical(None,'HWI4U',str(exc));return 1
    from ui_i18n import install,read_language,tr
    install(read_language(target))
    class StartupDialog(QDialog):
        def busy(self):return any(p.state()!=QProcess.ProcessState.NotRunning for p in self.findChildren(QProcess))
        def reject(self):
            if not self.busy():super().reject();app.quit()
        def closeEvent(self,event):
            if self.busy():event.ignore()
            else:super().closeEvent(event)
    dialog=StartupDialog();dialog.setWindowTitle('HWI4U — startup');dialog.resize(620,260)
    layout=QVBoxLayout(dialog);info=QLabel('');info.setWordWrap(True);layout.addWidget(info)
    location=QLabel(str(target));location.setWordWrap(True);layout.addWidget(location)
    progress=QProgressBar();progress.setRange(0,0);progress.hide();layout.addWidget(progress)
    buttons=QHBoxLayout();layout.addLayout(buttons)
    choose=QPushButton('Open existing inventory…');new=QPushButton('New inventory…');start=QPushButton('Prepare update in TEST' if args.channel=='update' else 'Start HWI4U TEST' if args.channel=='test' else 'Start HWI4U');close=QPushButton('Close')
    for button in (choose,new,start,close):buttons.addWidget(button)
    process=QProcess(dialog);environment=QProcessEnvironment()
    for k,v in child_environment().items():environment.insert(k,v)
    process.setProcessEnvironment(environment);process.setWorkingDirectory(str(source))
    # pythonw is used only for this wizard. Managed subprocesses use bundled python.exe.
    interpreter=Path(sys.executable).with_name('python.exe') if sys.platform=='win32' else Path(sys.executable)
    queue=[];log=None;exit_code=0
    def refresh():
        state=workspace_status(target);location.setText(str(target))
        info.setText(tr('Ready. Production and TEST keep separate databases.' if state=='ready' else 'First start creates an empty inventory and runs the complete checks. It may take a few minutes.' if state=='new' else 'An incomplete or unrecognized folder already exists. It will not be changed. Choose a new folder or a completed workspace.'))
        if state=='ready' and args.channel=='update':info.setText(tr('Prepare this installed version as a TEST update? Production stays pinned and TEST data is preserved. Review TEST before explicit production acceptance.'))
        start.setEnabled(state!='blocked')
    def pick():
        nonlocal target
        name=QFileDialog.getExistingDirectory(dialog,'Open completed HWI4U workspace',str(target.parent))
        if name:target=Path(name);refresh()
    def create():
        nonlocal target
        import datetime
        proposed=manage.default_workspace().with_name('HWI4U-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        name,ok=QInputDialog.getText(dialog,'New inventory folder','New data-folder path:',text=str(proposed))
        if ok and name.strip():target=Path(name.strip()).expanduser();refresh()
    def collect():
        if log:
            data=bytes(process.readAllStandardOutput())+bytes(process.readAllStandardError());log.write(data);log.flush()
    def launch_next():
        if not queue:return
        command=queue.pop(0);process.start(str(interpreter),['-B',str(source/'manage.py'),*command])
    def finished(code,status):
        nonlocal exit_code
        collect()
        if code or status!=QProcess.ExitStatus.NormalExit:
            exit_code=code or 1;progress.hide();choose.setEnabled(True);new.setEnabled(True);close.setEnabled(True);dialog.show();refresh()
            info.setText(tr('Startup stopped. Data and diagnostics were retained. See the startup log beside your chosen data folder. Choose a new folder after a failed first initialization; do not delete the failed folder.'));return
        if queue:
            if not args.workspace:atomic_json(settings,{'format':1,'workspace':str(target.resolve())})
            progress.hide();dialog.hide();launch_next()
        else:dialog.accept();app.quit()
    def run():
        nonlocal log,queue,exit_code
        try:
            queue=startup_plan(source,target,args.channel=='test',args.channel=='update');exit_code=0
            if log:log.close()
            # Logs are outside the inventory, including failed/partial installations.
            target.parent.mkdir(parents=True,exist_ok=True)
            log=(target.parent/(target.name+'-startup.log')).open('ab')
            if not args.workspace and workspace_status(target)=='ready':atomic_json(settings,{'format':1,'workspace':str(target.resolve())})
            choose.setEnabled(False);new.setEnabled(False);start.setEnabled(False);close.setEnabled(False)
            if len(queue)>1:progress.show()
            else:dialog.hide()
            launch_next()
        except Exception as exc:QMessageBox.critical(dialog,'HWI4U',str(exc))
    def reject():
        # Do not terminate initialization or a managed client with pending edits.
        if process.state()!=QProcess.ProcessState.NotRunning:return
        dialog.done(0);app.quit()
    choose.clicked.connect(pick);new.clicked.connect(create);start.clicked.connect(run);close.clicked.connect(reject)
    process.readyReadStandardOutput.connect(collect);process.readyReadStandardError.connect(collect)
    process.finished.connect(finished)
    def failed(error):
        if error==QProcess.ProcessError.FailedToStart:finished(1,QProcess.ExitStatus.CrashExit)
    process.errorOccurred.connect(failed)
    refresh();dialog.show()
    # A completed managed inventory needs no wizard click on subsequent starts.
    if workspace_status(target)=='ready' and args.channel!='update':QTimer.singleShot(0,run)
    app.exec()
    if log:log.close()
    return exit_code

if __name__=='__main__':sys.exit(main())
