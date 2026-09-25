"""Install the portable Codex workflow, without overwriting existing files."""
import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def unpack_checked(name, target):
    digest = json.loads((ROOT / 'checksums.json').read_text())[name]
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
        raise ValueError('Archive checksum mismatch')
    target = Path(target).resolve()
    with zipfile.ZipFile(ROOT / name) as archive:
        for member in archive.infolist():
            resolved = (target / member.filename).resolve()
            if target not in resolved.parents:
                raise ValueError('Unsafe archive path')
        archive.extractall(target)

def install(destination):
    destination = Path(destination).expanduser().resolve()
    skill = destination / 'skills/china-law-agent'
    agent = destination / 'agents/china_legal.toml'
    if skill.exists() or agent.exists():
        raise FileExistsError('Existing skill or agent found; choose a fresh --dest. Nothing overwritten.')
    with tempfile.TemporaryDirectory() as tmp:
        unpack_checked('workflow-bundle.zip', tmp)
        role = (ROOT / 'china_legal.toml').read_text().replace('__SKILL_PATH__', (skill / 'SKILL.md').as_posix())
        skill.parent.mkdir(parents=True, exist_ok=True)
        agent.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(Path(tmp) / 'china-law-agent', skill)
        try:
            with agent.open('x') as handle:
                handle.write(role)
        except Exception:
            shutil.rmtree(skill)
            raise
    return skill, agent

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', required=True, help='Codex config directory, e.g. ~/.codex or ./demo-config')
    args = parser.parse_args()
    for path in install(args.dest): print(path)
