"""Manifest-driven data download with checksum verification.

Entries in data/manifest.yaml with url set to "TODO" are skipped, so the
manifest can be filled in step by step (verify each URL and release first).
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import yaml


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path: Path) -> list[dict]:
    with open(path) as f:
        return (yaml.safe_load(f) or {}).get("files", [])


def download_all(manifest_path: Path, raw_dir: Path) -> list[str]:
    """Download every manifest entry with a real URL. Returns names fetched."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    fetched = []
    for entry in load_manifest(manifest_path):
        url = entry.get("url", "TODO")
        if not url or url == "TODO":
            print(f"[skip] {entry['name']}: url not set yet")
            continue
        dest = raw_dir / entry["filename"]
        if not dest.exists():
            print(f"[get ] {entry['name']} -> {dest}")
            urllib.request.urlretrieve(url, dest)
        expected = entry.get("sha256")
        if expected:
            actual = sha256sum(dest)
            if actual != expected:
                raise ValueError(f"Checksum mismatch for {dest}: {actual} != {expected}")
        else:
            print(f"[warn] {entry['name']}: no sha256 recorded; computed {sha256sum(dest)}")
        fetched.append(entry["name"])
    return fetched
