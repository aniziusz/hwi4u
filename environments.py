"""Independent test datasets and deliberate candidate promotion. Local files only."""
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import uuid
import zipfile
from update_runtime import atomic_json,digest,full_snapshot_locked,published,publish_pointer,supervise,verify_release


def area(root):
    root=Path(root).resolve();base=root/'test-environment'
    if base.is_symlink():raise ValueError('Test folder must not be a symlink')
    base.mkdir(mode=0o700,exist_ok=True)
    datasets=base/'datasets'
    if datasets.is_symlink():raise ValueError('Test datasets must not be symlinks')
    datasets.mkdir(mode=0o700,exist_ok=True)
    return base


@contextlib.contextmanager
def test_lock(root,exclusive=False):
    path=area(root)/'session.lock'
    if path.is_symlink():raise ValueError('Unsafe test lock')
    with path.open('a') as handle:
        if os.name=='nt':
            import msvcrt
            handle.seek(0,2)
            if handle.tell()==0:handle.write('0');handle.flush()
            handle.seek(0)
            try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
            except OSError:raise ValueError('Test environment is in use. Finish the test session before refreshing its data.')
            try:yield
            finally:handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
        else:
            import fcntl
            try:fcntl.flock(handle, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)|fcntl.LOCK_NB)
            except BlockingIOError:raise ValueError('Test environment is in use. Finish the test session before refreshing its data.')
            try:yield
            finally:fcntl.flock(handle,fcntl.LOCK_UN)


def current_dataset(root):
    base=area(root);pointer=base/'current.json'
    if not pointer.exists():raise ValueError('No test dataset. Use refresh-test-data.sh to create one.')
    if pointer.is_symlink():raise ValueError('Unsafe test data pointer')
    name=json.loads(pointer.read_text())['dataset']
    if not re.fullmatch('[0-9a-f]{32}',name):raise ValueError('Invalid test dataset identity')
    folder=base/'datasets'/name
    if folder.is_symlink() or not folder.is_dir():raise ValueError('Test dataset is unavailable')
    return folder


def validate_test_database(root,db):
    expected=current_dataset(root)/'hardware.sqlite3';db=Path(db)
    if db.is_symlink() or expected.is_symlink() or db.resolve()!=expected.resolve():
        raise ValueError('TEST client refuses a database outside its selected test dataset')
    if not expected.is_file():raise ValueError('Test database is missing')
    return expected


def refresh_test(root,confirmed=False):
    """Snapshot production into a NEW generation; never replace existing data files."""
    root=Path(root).resolve();base=area(root)
    with test_lock(root,exclusive=True):
        if (base/'current.json').exists() and not confirmed:
            raise ValueError('Refresh replaces the selected test data. Explicit confirmation is required; the previous copy is retained.')
        selection=published(root,'test')
        if not selection:raise ValueError('Publish a test candidate first')
        release,meta=selection;source=root/'hardware.sqlite3'
        if source.is_symlink():raise ValueError('Production database must not be a symlink')
        with tempfile.TemporaryDirectory(prefix='refresh-',dir=base/'datasets') as tmp:
            tmp=Path(tmp);bundle=tmp/'snapshot.zip';stage=tmp/'data';stage.mkdir(mode=0o700)
            with contextlib.closing(sqlite3.connect(source.as_uri()+'?mode=rw',uri=True,timeout=2)) as con:
                # A write reservation keeps committed metadata stable during copying.
                # No statement writes to the production database.
                con.execute('BEGIN IMMEDIATE')
                try:full_snapshot_locked(source,bundle)
                finally:con.rollback()
            with zipfile.ZipFile(bundle) as archive:
                checks=json.loads(archive.read('MANIFEST.json'))['sha256']
                for name,expected in checks.items():
                    part=Path(name)
                    if part.is_absolute() or '..' in part.parts or (name!='hardware.sqlite3' and (len(part.parts)!=3 or part.parts[0] not in ('photos','manuals','sources'))):
                        raise ValueError('Unsafe snapshot member')
                    content=archive.read(name)
                    if digest(content)!=expected:raise ValueError('Snapshot checksum mismatch')
                    file=stage/part;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(content);file.chmod(0o600)
            preferences=root/'ui-settings.json'
            if preferences.is_file():
                code=json.loads(preferences.read_text()).get('language')
                if code in ('en','de','hu'):atomic_json(stage/'ui-settings.json',{'language':code})
            checked=subprocess.run([sys.executable,str(release/'run_desktop.py'),'prepare','--db',str(stage/'hardware.sqlite3')],capture_output=True,text=True)
            if checked.returncode:raise ValueError('Test migration failed: '+(checked.stderr or checked.stdout))
            audit=subprocess.run([sys.executable,str(release/'inventory.py'),'--db',str(stage/'hardware.sqlite3'),'check'],capture_output=True,text=True)
            if audit.returncode:raise ValueError('Test copy validation failed: '+(audit.stderr or audit.stdout))
            ident=uuid.uuid4().hex;destination=base/'datasets'/ident
            atomic_json(stage/'SNAPSHOT.json',{'source':'production hardware.sqlite3','copied_at':dt.datetime.now(dt.timezone.utc).isoformat(),'release_id':meta['release_id'],'source_sha256':checks,'note':'Committed production data; later production changes are not synchronized.'})
            os.replace(stage,destination)
            atomic_json(base/'current.json',{'dataset':ident})
        return destination/'hardware.sqlite3'


def record_test_launch(root,db,release_id):
    validate_test_database(root,db)
    atomic_json(area(root)/'last-launch.json',{'release_id':release_id,'dataset':current_dataset(root).name,'launched_at':dt.datetime.now(dt.timezone.utc).isoformat()})


def launch_test(root,args):
    if any(arg=='--db' or arg.startswith('--db=') for arg in args):raise ValueError('The TEST launcher does not accept a database override')
    with test_lock(root):
        db=current_dataset(root)/'hardware.sqlite3';validate_test_database(root,db)
        return supervise(root,['--db',str(db),*args],channel='test')


def promote_test(root,release_id,accepted=False):
    if not accepted:raise ValueError('Explicit acceptance of the tested release is required')
    root=Path(root).resolve();selection=published(root,'test')
    if not selection or selection[1]['release_id']!=release_id:raise ValueError('Test candidate changed. Review the current candidate before promotion.')
    release,meta=selection
    receipt=json.loads((area(root)/'last-launch.json').read_text())
    if receipt.get('release_id')!=release_id or receipt.get('dataset')!=current_dataset(root).name:
        raise ValueError('Launch and review this candidate with the current test dataset first')
    if not list((release/'tests').rglob('test_*.py')):raise ValueError('Candidate has no automated test suite')
    env={**os.environ,'QT_QPA_PLATFORM':'offscreen','PYTHONDONTWRITEBYTECODE':'1'}
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(release/'tests')],cwd=release,env=env,capture_output=True,text=True)
    if result.returncode:raise ValueError('Promotion tests failed: '+result.stdout+result.stderr)
    verify_release(release)
    if published(root,'test')[1]['release_id']!=release_id:raise ValueError('Test candidate changed during validation; production remains unchanged')
    prior=published(root)
    publish_pointer(root,release_id,'production')
    atomic_json(root/'.runtime'/('promotion-'+uuid.uuid4().hex+'.json'),{'release_id':release_id,'previous_release_id':prior[1]['release_id'] if prior else None,'accepted_at':dt.datetime.now(dt.timezone.utc).isoformat(),'note':'Explicit acceptance; release only. No test data copied to production.'})
    return release


def maintenance_dialog(root,action):
    """Human-readable entry points for refresh and acceptance; no terminal needed."""
    from PySide6.QtWidgets import QApplication,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton
    from ui_i18n import install,tr,read_language
    app=QApplication.instance() or QApplication([]);install(read_language(root))
    dialog=QDialog();dialog.setWindowTitle('HWI4U TEST');layout=QVBoxLayout(dialog)
    text='Refresh test data from production? Current test edits will be replaced by a new copy. The previous test copy is retained. Production is unchanged. Finish the TEST session first.' if action=='refresh' else 'Accept this tested release for production? Only software and migrations are promoted. Test records are never copied back. Production applies the update through Apply update.'
    selection=published(root,'test');expected=selection[1]['release_id'] if selection else None
    if selection:label_id=QLabel(selection[1]['release_id'][:16]);layout.addWidget(label_id)
    label=QLabel(tr(text));label.setWordWrap(True);label.setMinimumWidth(420);layout.addWidget(label)
    if selection:layout.addWidget(QLabel(tr('Application version')+': '+selection[1]['version']))
    status=QLabel();status.setWordWrap(True);layout.addWidget(status);buttons=QHBoxLayout();layout.addLayout(buttons)
    run=QPushButton(tr('Refresh test data' if action=='refresh' else 'Accept tested release'));run.setAutoDefault(False);buttons.addWidget(run)
    cancel=QPushButton(tr('Cancel'));cancel.setDefault(True);cancel.clicked.connect(dialog.reject);buttons.addWidget(cancel)
    def execute():
        run.setEnabled(False);status.setText(tr('Working…'));app.processEvents()
        try:
            result=refresh_test(root,confirmed=True) if action=='refresh' else promote_test(root,expected,accepted=True)
            status.setText(tr('Completed: ')+str(result));run.hide();cancel.setText(tr('Close'))
        except Exception as exc:status.setText(str(exc));run.setEnabled(True)
    run.clicked.connect(execute);dialog.exec();return 0
