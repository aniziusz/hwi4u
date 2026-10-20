"""Measured full regression with locally authenticated, exact-input evidence reuse.

Receipts are local engineering evidence, never a substitute for platform CI,
backup/migration validation, or explicit user acceptance.
"""
import datetime as dt
import hashlib
import hmac
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import secrets
import sqlite3
import subprocess
import sys
import time
import uuid


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def fingerprint(root, env):
    from update_runtime import source_files
    dependencies = {}
    for name in ('PySide6', 'PySide6_Essentials', 'PySide6_Addons', 'shiboken6'):
        try:
            distribution = importlib.metadata.distribution(name)
            # Hash installed files, not just the advertised version or RECORD.
            entries = {}
            for file in distribution.files or []:
                if str(file).endswith(('.pyc', '.pyo')) or '__pycache__' in str(file):
                    continue
                path = distribution.locate_file(file)
                if path.is_file():
                    entries[str(file)] = sha(path.read_bytes())
            dependencies[name] = {'version': distribution.version, 'files': sha(canonical(entries))}
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    # Distribution metadata is absent in some OS-packaged Qt installations.
    # Include actual module/Qt library and plugin bytes in that case as well.
    module_hashes={}
    for module_name in ('PySide6','shiboken6'):
        module=importlib.import_module(module_name)
        base=Path(module.__file__).resolve().parent
        module_hashes[module_name]={str(path.relative_to(base)):sha(path.read_bytes()) for path in sorted(base.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc','.pyo')}
    from PySide6.QtCore import QLibraryInfo,qVersion
    qt_external={}
    for location in (QLibraryInfo.LibraryPath.LibrariesPath,QLibraryInfo.LibraryPath.PluginsPath):
        base=Path(QLibraryInfo.path(location))
        paths=base.glob('*Qt6*') if location==QLibraryInfo.LibraryPath.LibrariesPath else base.rglob('*')
        qt_external[str(base)]={str(path.relative_to(base)):sha(path.read_bytes()) for path in sorted(paths) if path.is_file()}
    dependencies['actual_modules_sha256']=sha(canonical(module_hashes))
    dependencies['qt_external_sha256']=sha(canonical(qt_external))
    dependencies['qt_version']=qVersion()
    return {
        'format': 1,
        'source': {name: sha(data) for name, data in source_files(Path(root)).items()},
        'python': sys.version,
        'executable': str(Path(sys.executable).resolve()),
        'executable_sha256': sha(Path(sys.executable).read_bytes()),
        'platform': platform.platform(), 'machine': platform.machine(),
        'sqlite': sqlite3.sqlite_version, 'dependencies': dependencies,
        # Values may contain credentials: persist only one digest, never the values.
        'environment_sha256': sha(canonical(env)),
        'command': ['-m', 'unittest', 'discover', '-s', 'tests'],
    }


def private_key(folder):
    folder = Path(folder)
    if folder.is_symlink():
        raise ValueError('Validation directory must not be a symlink')
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = folder / 'receipt.key'
    if path.is_symlink():
        raise ValueError('Validation key must not be a symlink')
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(fd, 'wb') as file:
            file.write(secrets.token_bytes(32))
    key = path.read_bytes()
    if len(key) != 32:
        raise ValueError('Invalid validation key; preserve evidence and investigate')
    return key


def run_full(root, evidence, reuse=True):
    """Reuse only signed PASS for identical source, dependencies, OS and environment."""
    from update_runtime import atomic_json
    root = Path(root).resolve(); evidence = Path(evidence)
    if not list((root / 'tests').rglob('test_*.py')):
        raise ValueError('Candidate has no automated test suite')
    # Qt initializes its enum policy in os.environ on first import. Capture the
    # effective environment after that one-time setup, not a pre-import snapshot.
    importlib.import_module('PySide6.QtCore')
    env = {**os.environ, 'QT_QPA_PLATFORM': 'offscreen', 'PYTHONDONTWRITEBYTECODE': '1'}
    started = time.perf_counter()
    inputs = fingerprint(root, env)
    ident = sha(canonical(inputs)); key = private_key(evidence)
    receipt = evidence / (ident + '.json')
    if reuse and receipt.is_file() and not receipt.is_symlink():
        try:
            envelope = json.loads(receipt.read_text())
            record = envelope['record']
            signature = hmac.new(key, canonical(record), 'sha256').hexdigest()
            if (hmac.compare_digest(signature, envelope['signature']) and record['inputs'] == inputs
                    and record['result'] == 'passed' and record['tests_run'] > 0
                    and not (evidence/(ident+'.log')).is_symlink()
                    and sha((evidence/(ident+'.log')).read_bytes())==record['output_sha256']):
                atomic_json(evidence / ('reuse-' + uuid.uuid4().hex + '.json'), {
                    'fingerprint': ident, 'receipt': receipt.name, 'result': 'reused',
                    'tests_run_previously': record['tests_run'],
                    'elapsed_seconds': time.perf_counter() - started,
                    'observed_at': dt.datetime.now(dt.timezone.utc).isoformat()})
                return {**record, 'reused': True, 'elapsed_seconds': time.perf_counter() - started}
        except (OSError, ValueError, TypeError, KeyError):
            pass  # Damaged, stale or unsigned evidence always runs the suite again.
    # Invalidate older PASS before a forced rerun; interruption must not revive it.
    atomic_json(receipt, {'record': {'result':'running'}, 'signature':''})
    try:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
                                cwd=root, env=env, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('Full regression timed out; no passing evidence retained') from exc
    output = result.stdout + result.stderr
    count = re.search(r'Ran (\d+) tests? in ', output)
    ran = int(count.group(1)) if count else 0
    if fingerprint(root, env) != inputs:
        raise RuntimeError('Validation inputs changed during checks; freeze the candidate and retry')
    record = {'inputs': inputs, 'result': 'passed' if result.returncode == 0 and ran > 0 else 'failed',
              'tests_run': ran, 'elapsed_seconds': time.perf_counter() - started,
              'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'output_sha256': sha(output.encode()), 'reused': False}
    log = evidence / (ident + '.log')
    if log.is_symlink() or receipt.is_symlink():
        raise ValueError('Unsafe validation receipt path')
    log.write_bytes(output.encode('utf-8'))
    atomic_json(receipt, {'record': record, 'signature': hmac.new(key, canonical(record), 'sha256').hexdigest()})
    if record['result'] != 'passed':
        raise RuntimeError('Full regression failed:\n' + output)
    return record
