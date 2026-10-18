#!/usr/bin/env python3
"""Managed launcher: run, publish a tested release, or prepare an update."""
from pathlib import Path
import sys
from update_runtime import publish,prepare_database,supervise

def main():
    root=Path(__file__).resolve().parent
    if sys.argv[1:2]==['publish']:
        print('Published TEST candidate:',publish(root,channel='test'));return 0
    if sys.argv[1:2]==['prepare']:
        if len(sys.argv)!=4 or sys.argv[2]!='--db':raise ValueError('prepare requires --db PATH')
        backup=prepare_database(Path(sys.argv[3]),root)
        if backup:print('Verified pre-update backup:',backup)
        return 0
    if sys.argv[1:2]==['test']:
        from environments import launch_test
        return launch_test(root,sys.argv[2:])
    if sys.argv[1:2]==['refresh-test']:
        from environments import refresh_test,maintenance_dialog
        if '--gui' in sys.argv:return maintenance_dialog(root,'refresh')
        print('Test database:',refresh_test(root,confirmed='--confirm-replace-test-data' in sys.argv));return 0
    if sys.argv[1:2]==['promote-test']:
        from environments import promote_test,maintenance_dialog
        if '--gui' in sys.argv:return maintenance_dialog(root,'promote')
        from update_runtime import published
        candidate=published(root,'test')
        if not candidate:raise ValueError('No test candidate is published')
        print('Promoted release:',promote_test(root,candidate[1]['release_id'],accepted='--accept-test-release' in sys.argv));return 0
    return supervise(root,sys.argv[1:])

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        print('Update deferred; database was not overwritten. '+str(exc),file=sys.stderr);sys.exit(1)
