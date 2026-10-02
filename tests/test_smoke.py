from pathlib import Path

from epirepurpose import __version__
from epirepurpose.cli import main
from epirepurpose.data.download import load_manifest, sha256sum


def test_version():
    assert __version__


def test_cli_runs():
    assert main([]) == 0


def test_manifest_loads():
    manifest = Path(__file__).parents[1] / "data" / "manifest.yaml"
    entries = load_manifest(manifest)
    assert len(entries) > 0
    assert all("name" in e and "filename" in e for e in entries)


def test_sha256(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("hello")
    assert sha256sum(p) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
