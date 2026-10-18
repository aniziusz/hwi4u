"""Source-based desktop installation with an isolated Python environment.

Requires Python 3.14 (native arm64 on Apple Silicon). Never adopts existing data.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import plistlib
import shlex
import subprocess
import sys
import venv

def validate_platform(system=None,machine=None,version=None):
    system=system or platform.system();machine=(machine or platform.machine()).lower()
    version=version or sys.version_info[:2]
    if tuple(version)!=(3,14):raise ValueError('Install Python 3.14 first; this installer uses the tested Python 3.14 runtime.')
    if system=='Darwin' and machine not in ('arm64','aarch64'):raise ValueError('FR-029 targets native Apple Silicon. Use the ARM64 Python runtime, not Rosetta/Intel Python.')
    if system=='Windows' and machine not in ('amd64','x86_64'):raise ValueError('This Windows package targets x64 Python.')
    if system not in ('Windows','Darwin','Linux'):raise ValueError('Unsupported desktop platform.')
    return system

def environment_python(root,system=None):
    return Path(root)/'.venv'/('Scripts/python.exe' if (system or platform.system())=='Windows' else 'bin/python')

def make_mac_launcher(source,destination,test=False):
    """Create a launcher only, never a bundled runtime or a copied inventory."""
    source=Path(source).resolve();destination=Path(destination)
    if destination.exists():raise FileExistsError('Launcher already exists: '+str(destination))
    destination.mkdir(parents=True)
    contents=destination/'Contents';binary=contents/'MacOS';binary.mkdir(parents=True)
    ident='org.hwi4u.test' if test else 'org.hwi4u.desktop'
    with (contents/'Info.plist').open('wb') as file:
        plistlib.dump(dict(CFBundleName='HWI4U TEST' if test else 'HWI4U',CFBundleIdentifier=ident,CFBundleExecutable='hwi4u',CFBundlePackageType='APPL',CFBundleVersion='1',LSMinimumSystemVersion='14.0',NSHighResolutionCapable=True),file)
    command=[str(environment_python(source,'Darwin')),str(source/'desktop_start.py')]
    if test:command.append('test')
    script=binary/'hwi4u';script.write_text('#!/bin/sh\nexec '+shlex.join(command)+'\n');script.chmod(0o700)
    return destination

def install(source,skip_pip=False):
    system=validate_platform();source=Path(source).resolve();python=environment_python(source,system)
    if not python.exists():venv.EnvBuilder(with_pip=True).create(source/'.venv')
    subprocess.run([str(python),'-c','import platform,sys;from install_desktop import validate_platform;validate_platform();print(platform.platform(),platform.machine(),sys.version)'],cwd=source,check=True)
    if not skip_pip:subprocess.run([str(python),'-m','pip','install','-r',str(source/'requirements.txt')],check=True)
    # Existing generated workspaces retain data; source sync detects manual modifications.
    from manage import default_workspace,MARKER
    target=default_workspace()
    if not target.exists():subprocess.run([str(python),str(source/'manage.py'),'init'],check=True)
    elif not (target/'INSTALLATION.json').is_file() or not (target/MARKER).is_file():
        raise ValueError('Existing data folder is not a managed workspace. It was not changed. Choose a separate new workspace using manage.py; never overwrite it.')
    else:subprocess.run([str(python),str(source/'manage.py'),'publish'],check=True)
    if system=='Darwin':
        # Keep launchers with this installation so reinstalling never overwrites unrelated apps.
        for test,name in ((False,'HWI4U.app'),(True,'HWI4U TEST.app')):
            destination=source/name
            if destination.exists():
                info=destination/'Contents/Info.plist'
                if not info.is_file() or plistlib.loads(info.read_bytes()).get('CFBundleIdentifier')!=('org.hwi4u.test' if test else 'org.hwi4u.desktop'):
                    raise ValueError('Unrecognized existing launcher; not overwritten: '+str(destination))
                # Source folder is unchanged; keep its existing launcher intact.
            else:make_mac_launcher(source,destination,test)
    print('HWI4U installed. Data:',target)
    print('Use Start HWI4U.cmd on Windows or HWI4U.app on macOS. Keep this source folder in place.')
    return target

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--skip-pip',action='store_true',help='Offline use only when the exact requirements are already installed in .venv')
    args=parser.parse_args()
    try:install(Path(__file__).resolve().parent,args.skip_pip);return 0
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:print('Installation stopped:',exc,file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
