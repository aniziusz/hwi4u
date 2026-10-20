#!/usr/bin/env python3
"""Run real assertions and preserve Qt/resource diagnostics; no user data is opened."""
import argparse,gc,json,os,platform,sys,time,unittest,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from qt_test_environment import test_environment

TARGETS=(
 'test_automatic_ids.AutomaticIDs.test_cli_without_id',
 'test_lowercase.Lowercase.test_migration_and_constraints',
 'test_network_identity.NetworkIdentity.test_busy_name_check_warns_without_writing',
 'test_environments.Environments.test_attachment_copy_is_independent_and_missing_files_preserve_pointer',
 'test_photos.Photos.test_invalid_imports_and_cleanup',
 'test_network_identity.NetworkIdentity.test_live_name_uniqueness_unicode_and_length',
 'test_resource_lifetimes.ResourceLifetimes',
)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--phase',choices=('targeted','full'),required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);os.environ.update(test_environment())
    from PySide6.QtCore import qInstallMessageHandler,QEvent
    import PySide6
    messages=[]
    def handler(kind,context,message):
        messages.append(dict(kind=str(kind),message=message));print(message,file=sys.stderr)
    previous=qInstallMessageHandler(handler);start=time.perf_counter()
    with warnings.catch_warnings(record=True) as observed:
        warnings.simplefilter('always',ResourceWarning)
        suite=(unittest.defaultTestLoader.loadTestsFromNames(TARGETS) if args.phase=='targeted' else unittest.defaultTestLoader.discover(str(ROOT/'tests')))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        from PySide6.QtWidgets import QApplication
        app=QApplication.instance()
        if app:app.sendPostedEvents(None,QEvent.DeferredDelete);app.processEvents()
        gc.collect()
    qInstallMessageHandler(previous)
    resources=[str(w.message) for w in observed if issubclass(w.category,ResourceWarning)]
    font_warnings=[m['message'] for m in messages if 'Cannot find font directory' in m['message']]
    report=dict(phase=args.phase,system=platform.system(),python=platform.python_version(),qt=PySide6.__version__,tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),elapsed_seconds=time.perf_counter()-start,resource_warnings=resources,missing_font_directory_warnings=font_warnings,qt_messages=messages,font_directory=os.environ.get('QT_QPA_FONTDIR'),data='disposable fictional inventories only')
    (args.output/(args.phase+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='qt_messages'},ensure_ascii=False))
    return 0 if result.wasSuccessful() and not resources and not font_warnings and not result.skipped else 1

if __name__=='__main__':sys.exit(main())
