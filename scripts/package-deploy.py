"""Package the project with Vercel entry points directly at the archive root."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / 'deliverables/didgar-github-vercel-ready.zip'
EXCLUDED = {'node_modules', '.git', '.vercel', '__pycache__'}

def include(path):
    relative = path.relative_to(ROOT)
    return (path.is_file() and not any(part in EXCLUDED for part in relative.parts)
            and path.suffix != '.pyc'
            and not (path.name.startswith('.env') and path.name != '.env.example'))

files = sorted(path for path in ROOT.rglob('*') if include(path))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
temporary = OUTPUT.with_suffix('.zip.tmp')
with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.write(path, path.relative_to(ROOT).as_posix())

with zipfile.ZipFile(temporary) as archive:
    names = archive.namelist()
    assert len(names) == len(set(names)) == len(files)
    assert all(not name.startswith('/') and '..' not in Path(name).parts for name in names)
    for required in ('index.html', 'package.json', 'vercel.json', 'scripts/build.mjs',
                     'content/routes.json', 'api/consultation.mjs', 'README.md'):
        assert required in names, required
    assert not any(name.startswith('didgar-site/') for name in names)
    assert archive.testzip() is None
    for path in files:
        assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes()
temporary.replace(OUTPUT)
print(json.dumps({'file': str(OUTPUT), 'bytes': OUTPUT.stat().st_size,
                  'entries': len(files), 'root_entry_points': True,
                  'crc_and_exact_files': True,
                  'sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest()}))
