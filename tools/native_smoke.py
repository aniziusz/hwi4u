#!/usr/bin/env python3
"""Native Qt/editor/backup smoke on disposable fictional data only."""
import argparse,contextlib,json,os,platform,sqlite3,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def smoke(output):
    system=platform.system();expected={'Windows':'windows','Darwin':'cocoa'}.get(system,'offscreen')
    os.environ['QT_QPA_PLATFORM']=expected
    from PySide6.QtWidgets import QApplication
    import PySide6
    from desktop import Window
    from device_store import DeviceStore
    from photo_files import backup_bundle
    from tools.verify_bundle import restore
    from install_desktop import validate_platform
    from manage import initialize
    validate_platform()
    if system=='Darwin':assert platform.machine().lower()=='arm64'
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    app=QApplication.instance() or QApplication([])
    assert app.platformName()==expected,(app.platformName(),expected)
    source=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='hwi4u-platform-') as tmp:
        root=Path(tmp);workspace=root/'private space';initialize(source,workspace,run_tests=False)
        db=workspace/'hardware.sqlite3';store=DeviceStore(db);store.save(dict(name='Fictional Árvíztűrő Büro',source='FICTIONAL TEST'))
        window=Window(store,language='en');window.show();app.processEvents();window.load(window.rows[0])
        window.table.itemDoubleClicked.emit(window.table.item(0,1));editor=next(iter(window.editors.values()));app.processEvents()
        assert editor.isMaximized() and editor.table.isHidden()
        editor.inputs['name'].setText('Fictional reviewed device');editor.inputs['location'].setText('Földszint / Büro');assert editor.save()
        assert window.inputs['name'].text()=='Fictional reviewed device'
        for code in ('de','hu','en'):window.set_language(code);assert editor.language_actions[code].isChecked()
        assert editor.grab().save(str(output/'device-editor.png'));assert window.grab().save(str(output/'quick-editor.png'))
        bundle=root/'full.zip';backup_bundle(db,bundle);restored=restore(bundle,root/'restore')
        assert DeviceStore(restored/'hardware.sqlite3').devices()[0]['device_id']==store.devices()[0]['device_id']
        # Windows/macOS UTF-8 export must preserve non-ASCII user text.
        import subprocess
        subprocess.run([sys.executable,str(source/'inventory.py'),'--db',str(db),'export','--directory',str(root/'export')],check=True,capture_output=True)
        assert json.loads((root/'export/inventory.json').read_text(encoding='utf-8'))['devices'][0]['location']=='Földszint / Büro'
        editor.close();window.close();app.processEvents()
    report=dict(system=system,machine=platform.machine(),python=platform.python_version(),qt=PySide6.__version__,qt_platform=app.platformName(),native_ui=(system in ('Windows','Darwin')),expanded_editor=True,quick_refresh=True,workspace_initialization=True,full_restore=True,export=True,data='disposable fictional data only')
    (output/'platform-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report));return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();smoke(args.output)
