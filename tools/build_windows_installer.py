"""Build a per-user offline NSIS installer from an allowlisted source + Python runtime.

Run with CPython3.14.8 x64 and PySide6 6.11.2 on Windows. No private data copied.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def nsis_quote(value):
    value=str(value)
    if any(c in value for c in '\r\n\0'):raise ValueError('Unsafe NSIS value')
    return value.replace('$','$$').replace('"','$\\"')


def build_payload(source,output):
    from update_runtime import source_files
    if sys.platform!='win32' or platform.machine().lower() not in ('amd64','x86_64') or sys.version_info[:3]!=(3,14,8):raise ValueError('Build on Windows x64 with Python3.14.8.')
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    app=output/'app';app.mkdir()
    files=source_files(source)
    for name,content in files.items():
        if content.startswith(b'SQLite format 3\0'):raise ValueError('Database found in source allowlist')
        p=app/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    runtime=output/'python';base=Path(sys.base_prefix).resolve()
    # Full Windows CPython layout keeps subprocess -m unittest and managed releases
    # portable without frozen-executable dispatch or external Python/registry state.
    def omit(directory,names):
        ignored={'__pycache__','site-packages','test','tests','idlelib','turtledemo','ensurepip','sitecustomize.py','usercustomize.py'}
        return [x for x in names if x in ignored or x.endswith(('.pyc','.pyo'))]
    runtime.mkdir()
    for name in ('python.exe','pythonw.exe','python3.dll','python314.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt'):
        p=base/name
        if p.exists():shutil.copy2(p,runtime/name)
    for name in ('Lib','DLLs'):
        shutil.copytree(base/name,runtime/name,ignore=omit)
    for required in ('python.exe','pythonw.exe','python314.dll','Lib/os.py','Lib/unittest/__init__.py','DLLs/_sqlite3.pyd'):
        if not (runtime/required).is_file():raise ValueError('Incomplete bundled Python: '+required)
    site=runtime/'Lib/site-packages';site.mkdir()
    subprocess.run([sys.executable,'-m','pip','install','--no-deps','--only-binary=:all:','--no-compile','--target',str(site),'PySide6-Essentials==6.11.2','shiboken6==6.11.2'],check=True)
    # Site customization imports are deliberately not copied from the build machine.
    # Use normal Windows Lib/os.py landmark discovery, then prove paths at runtime.
    code='import json,sys,sqlite3,PySide6;from PySide6.QtCore import qVersion;print(json.dumps(dict(prefix=sys.prefix,python=sys.version,qt=qVersion(),pyside=PySide6.__file__)))'
    env={k:v for k,v in os.environ.items() if k not in ('PYTHONHOME','PYTHONPATH')};env['PYTHONDONTWRITEBYTECODE']='1'
    proof=json.loads(subprocess.check_output([str(runtime/'python.exe'),'-I','-c',code],env=env,text=True))
    if Path(proof['prefix']).resolve()!=runtime or not Path(proof['pyside']).resolve().is_relative_to(runtime):raise ValueError('Bundled Python escaped its installation')
    version=next(ast.literal_eval(x.value) for x in ast.parse((app/'ui_i18n.py').read_text()).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='APP_VERSION' for t in x.targets))
    manifest={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()}
    (output/'INSTALL-MANIFEST.json').write_text(json.dumps({'version':version,'sha256':manifest,'runtime':proof},indent=2)+'\n')
    return version


def installer_script(payload,destination,version):
    payload=Path(payload).resolve();destination=Path(destination).resolve()
    manifest=json.loads((payload/'INSTALL-MANIFEST.json').read_text())['sha256']
    # Exact file deletion, never recursive removal of a user-data directory.
    paths=[*manifest,'INSTALL-MANIFEST.json']
    removals='\n'.join('  Delete "$INSTDIR\\'+nsis_quote(p.replace('/','\\'))+'"' for p in paths)
    dirs=sorted({parent.as_posix() for p in paths for parent in Path(p).parents if str(parent)!='.'},key=lambda x:(-x.count('/'),x),reverse=False)
    removals+='\n'+'\n'.join('  RMDir "$INSTDIR\\'+nsis_quote(p.replace('/','\\'))+'"' for p in dirs)
    return r'''Unicode True
!include "MUI2.nsh"
!include "x64.nsh"
Name "HWI4U @VERSION@ (TEST installer)"
OutFile "@DEST@"
InstallDir "$LOCALAPPDATA\Programs\HWI4U\@VERSION@"
RequestExecutionLevel user
SetCompressor /SOLID lzma
ShowInstDetails show
ShowUninstDetails show
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TEXT "Installs HWI4U with Python and Qt for this user. No separate Python, PowerShell or internet connection is needed. Inventory data is kept separately and is preserved on uninstall. This is a TEST installer candidate."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "@PAYLOAD@\app\LICENSE"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Hungarian"
Function .onInit
  SetShellVarContext current
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "HWI4U requires Windows x64."
    Abort
  ${EndIf}
  IfFileExists "$INSTDIR\INSTALL-MANIFEST.json" 0 +3
    MessageBox MB_ICONINFORMATION "This version is already installed. Use its Start-menu shortcut, or uninstall the program first. Inventory data will be preserved."
    Abort
FunctionEnd
Section "HWI4U" SEC_APP
  SetOutPath "$INSTDIR"
  File /r "@PAYLOAD@\*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\HWI4U @VERSION@"
  SetOutPath "$INSTDIR\app"
  CreateShortcut "$SMPROGRAMS\HWI4U @VERSION@\HWI4U.lnk" "$INSTDIR\python\pythonw.exe" '-E -s -B "$INSTDIR\app\windows_start.py" production'
  CreateShortcut "$SMPROGRAMS\HWI4U @VERSION@\HWI4U TEST.lnk" "$INSTDIR\python\pythonw.exe" '-E -s -B "$INSTDIR\app\windows_start.py" test'
  CreateShortcut "$SMPROGRAMS\HWI4U @VERSION@\Prepare update in TEST.lnk" "$INSTDIR\python\pythonw.exe" '-E -s -B "$INSTDIR\app\windows_start.py" update'
  CreateShortcut "$SMPROGRAMS\HWI4U @VERSION@\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@" "DisplayName" "HWI4U @VERSION@ (TEST installer)"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@" "DisplayVersion" "@VERSION@"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@" "NoRepair" 1
SectionEnd
Section "Uninstall"
  SetShellVarContext current
@REMOVE@
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  Delete "$SMPROGRAMS\HWI4U @VERSION@\HWI4U.lnk"
  Delete "$SMPROGRAMS\HWI4U @VERSION@\HWI4U TEST.lnk"
  Delete "$SMPROGRAMS\HWI4U @VERSION@\Prepare update in TEST.lnk"
  Delete "$SMPROGRAMS\HWI4U @VERSION@\Uninstall.lnk"
  RMDir "$SMPROGRAMS\HWI4U @VERSION@"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\HWI4U-@VERSION@"
SectionEnd
'''.replace('@VERSION@',nsis_quote(version)).replace('@DEST@',nsis_quote(destination)).replace('@PAYLOAD@',nsis_quote(payload)).replace('@REMOVE@',removals)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--makensis',type=Path,required=True);args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    version=build_payload(ROOT,output/'payload');exe=output/f'HWI4U-{version}-windows-x64-setup.exe'
    nsi=output/'installer.nsi';nsi.write_text(installer_script(output/'payload',exe,version),encoding='utf-8-sig')
    subprocess.run([str(args.makensis),str(nsi)],check=True)
    checksum=hashlib.sha256(exe.read_bytes()).hexdigest();(output/'SHA256SUMS.txt').write_text(checksum+'  '+exe.name+'\n')
    print(exe)

if __name__=='__main__':main()
