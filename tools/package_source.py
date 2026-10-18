#!/usr/bin/env python3
"""Create an allowlisted source-client ZIP, without private data or a Python runtime."""
import argparse,json,os,stat,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from update_runtime import source_files,digest
from ui_i18n import APP_VERSION

def package(root,output):
    root=Path(root).resolve();output=Path(output).resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    files=source_files(root)
    if any(data.startswith(b'SQLite format 3\x00') for data in files.values()):raise ValueError('Unexpected database in source package.')
    # Exclusive output: never overwrite a package that someone may be reviewing.
    try:
        with output.open('xb') as file,zipfile.ZipFile(file,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in files.items():
                entry=zipfile.ZipInfo('HWI4U/'+name);entry.create_system=3;entry.compress_type=zipfile.ZIP_DEFLATED
                entry.external_attr=((stat.S_IFREG| (0o755 if Path(name).suffix in ('.sh','.command') else 0o644))<<16)
                archive.writestr(entry,data)
            archive.writestr('HWI4U/SOURCE-MANIFEST.json',json.dumps(dict(version=APP_VERSION,sha256={n:digest(b) for n,b in files.items()}),indent=2)+'\n')
    except FileExistsError:raise
    except Exception:
        output.unlink(missing_ok=True);raise
    with zipfile.ZipFile(output) as archive:
        for name,data in files.items():
            if archive.read('HWI4U/'+name)!=data:raise ValueError('Source package verification failed.')
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    print(package(Path(__file__).resolve().parents[1],args.output))
