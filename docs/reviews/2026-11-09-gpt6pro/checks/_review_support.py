"""Small I/O and provenance helpers for the independent review checks."""
from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import sys

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'source_provenance.json'
COMMIT = 'f48f0e2c728739a97fb90fb795eddb54c98c2dc3'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict:
    value = json.loads(MANIFEST.read_text())
    require(value['reviewed_commit'] == COMMIT, 'Unexpected provenance commit.')
    return value


def verify_repo(repo: Path, paths: tuple[str, ...]) -> dict[str, str]:
    """Check every selected source file before any repository module is imported."""
    repo = repo.expanduser().resolve(strict=True)
    pins = provenance()['source_sha256']
    checked = {}
    for name in paths:
        path = repo / name
        require(path.is_file(), f'Missing pinned source file: {path}')
        actual = sha256(path)
        require(actual == pins[name],
                f'SHA-256 MISMATCH for {name}: expected {pins[name]}, got {actual}. '
                'Refusing to import or use modified/unreviewed source; nothing is fetched.')
        checked[name] = actual
    return checked


def public_input() -> tuple[dict, str]:
    path = HERE / 'public_block_aggregates.json'
    actual = sha256(path)
    expected = provenance()['public_input_sha256'][path.name]
    require(actual == expected, 'Bundled public aggregate input SHA-256 mismatch.')
    return json.loads(path.read_text()), actual


def load_verified_module(name: str, path: Path, package: bool = False):
    """Caller must verify the file first. This never invokes a script's main()."""
    require(name not in sys.modules, f'Module already loaded before pinned import: {name}')
    kwargs = {'submodule_search_locations': [str(path.parent)]} if package else {}
    spec = importlib.util.spec_from_file_location(name, path, **kwargs)
    require(spec is not None and spec.loader is not None, f'Cannot load module: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    require(Path(module.__file__).resolve() == path.resolve(), 'Unexpected module origin.')
    return module


def environment() -> dict:
    return {'python': platform.python_version(),
            'numpy': importlib.metadata.version('numpy'),
            'scipy': importlib.metadata.version('scipy')}


def write_output(path: Path, payload: dict, repo: Path | None = None) -> None:
    path = path.expanduser().resolve()
    if repo is not None:
        require(not path.is_relative_to(repo.expanduser().resolve()),
                'Choose an output outside the reviewed repository; source is read-only.')
    protected = {p.resolve() for p in HERE.iterdir() if p.is_file()}
    require(path not in protected, 'Output cannot overwrite a supplied check or input file.')
    require(path.parent.is_dir(), 'Output directory must already exist; no other files/directories are written.')
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': 'completed', 'output': str(path)}, indent=2))
