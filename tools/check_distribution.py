#!/usr/bin/env python3
"""Check tracked source for excluded runtime data; never inspect private workspace files."""
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'backups','exports','photos','manuals','sources','.runtime','test-environment','.venv','__pycache__'}

def check(paths):
    problems=[]
    for relative in paths:
        p=Path(relative)
        if p.is_absolute() or '..' in p.parts or FORBIDDEN.intersection(p.parts):problems.append(str(p));continue
        name=p.name.lower()
        if re.search(r'\.(?:sqlite3?|db|kdbx|pem|key|p12|pfx)(?:-.*)?$',name) or name.startswith('.env') and name!='.env.example' or name in ('ui-settings.json','.hwi4u-workspace.json','installation.json','snapshot.json'):problems.append(str(p))
        path=ROOT/p
        if path.is_symlink():problems.append(str(p)+' (symlink)')
        if path.is_file() and path.read_bytes()[:16]==b'SQLite format 3\x00':problems.append(str(p)+' (SQLite binary)')
    if problems:raise ValueError('Private/runtime paths in distribution: '+', '.join(problems))

def main():
    result=subprocess.run(['git','ls-files','-z'],cwd=ROOT,check=True,capture_output=True)
    paths=[n for n in result.stdout.decode().split('\0') if n]
    if not paths:raise ValueError('No tracked/staged source files to inspect.')
    check(paths);print('Checked',len(paths),'tracked source files; no forbidden runtime paths or SQLite binaries.')

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as exc:print(str(exc),file=sys.stderr);sys.exit(1)
