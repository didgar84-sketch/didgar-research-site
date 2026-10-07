"""Regenerate and package the reproducible teaching project."""
from pathlib import Path
import subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'examples/research-demo'
subprocess.run([sys.executable,str(PROJECT/'research.py')],check=True)
subprocess.run([sys.executable,str(PROJECT/'test_examples.py')],check=True)
target=ROOT/'assets/downloads/common/research-examples.zip'
target.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for file in sorted(PROJECT.rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.suffix!='.pyc':
            info=zipfile.ZipInfo('research-demo/'+file.relative_to(PROJECT).as_posix(),date_time=(2026,10,6,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,file.read_bytes())
with zipfile.ZipFile(target) as archive: assert archive.testzip() is None
print(f'Created {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes).')
