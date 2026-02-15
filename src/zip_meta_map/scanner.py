"""File system and ZIP archive scanning."""

from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath


@dataclass
class ScannedFile:
    path: str
    size_bytes: int
    sha256: str
    content: bytes | None = None


def _should_ignore(path: str, ignore_globs: list[str]) -> bool:
    """Check if a path matches any ignore glob."""
    posix = PurePosixPath(path)
    for glob in ignore_globs:
        if fnmatch(str(posix), glob):
            return True
        # Also check each component for directory globs like "__pycache__/**"
        for part in posix.parts:
            if fnmatch(part, glob.split("/")[0]) and glob.endswith("/**"):
                return True
    return False


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_directory(root: Path, ignore_globs: list[str]) -> list[ScannedFile]:
    """Scan a directory and return a list of ScannedFile entries."""
    files: list[ScannedFile] = []
    root = root.resolve()

    for fpath in sorted(root.rglob("*")):
        if not fpath.is_file():
            continue
        rel = fpath.relative_to(root).as_posix()
        if _should_ignore(rel, ignore_globs):
            continue
        data = fpath.read_bytes()
        files.append(
            ScannedFile(
                path=rel,
                size_bytes=len(data),
                sha256=_sha256(data),
            )
        )

    return files


def scan_zip(zip_path: Path, ignore_globs: list[str]) -> list[ScannedFile]:
    """Scan a ZIP archive and return a list of ScannedFile entries."""
    files: list[ScannedFile] = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in sorted(zf.infolist(), key=lambda i: i.filename):
            if info.is_dir():
                continue
            rel = info.filename
            if _should_ignore(rel, ignore_globs):
                continue
            data = zf.read(info.filename)
            files.append(
                ScannedFile(
                    path=rel,
                    size_bytes=info.file_size,
                    sha256=_sha256(data),
                )
            )

    return files
