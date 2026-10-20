#!/usr/bin/env python3
"""Run measured full checks or a focused development check; records stay private."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import os
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validation import run_full
from update_runtime import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--pattern', help='Focused unittest filename pattern; never accepted as release proof')
    parser.add_argument('--fresh', action='store_true', help='Force a new full run')
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    if args.pattern:
        start = time.perf_counter()
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', args.pattern],
                                cwd=root, env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'})
        report = {'kind': 'targeted', 'pattern': args.pattern, 'returncode': result.returncode,
                  'elapsed_seconds': time.perf_counter() - start, 'release_evidence': False}
        atomic_json(args.evidence / 'targeted-last.json', report)
        print(json.dumps(report)); return result.returncode
    report = run_full(root, args.evidence, reuse=not args.fresh)
    print(json.dumps({key: report[key] for key in ('result', 'tests_run', 'elapsed_seconds', 'reused')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
