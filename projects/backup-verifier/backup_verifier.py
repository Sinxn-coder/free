"""Create and verify portable SHA-256 manifests for directory backups."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn

MANIFEST_VERSION = 1
HASH_CHUNK_SIZE = 1024 * 1024
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_WINDOWS_DRIVE_PATTERN = re.compile(r"[A-Za-z]:")


class VerifierError(Exception):
    """An expected input, manifest, or filesystem error."""


class ScanError(VerifierError):
    """An error encountered while reading the selected directory tree."""


class InputError(VerifierError):
    """An invalid or inaccessible command-line path."""


class ManifestError(VerifierError):
    """An invalid, unreadable, or unwritable manifest."""


def _resolve_root(root_argument: str | Path) -> Path:
    root = Path(root_argument).expanduser()
    try:
        resolved = root.resolve(strict=True)
    except OSError as error:
        raise ScanError(f"cannot access root directory '{root}': {error}") from error
    if not resolved.is_dir():
        raise ScanError(f"root is not a directory: '{root}'")
    return resolved


def _manifest_location(root: Path, manifest_argument: str | Path) -> Path:
    supplied_path = Path(manifest_argument).expanduser().absolute()
    try:
        parent = supplied_path.parent.resolve(strict=True)
    except OSError as error:
        raise InputError(
            f"cannot access manifest directory '{supplied_path.parent}': {error}"
        ) from error
    if not parent.is_dir():
        raise InputError(f"manifest parent is not a directory: '{parent}'")

    destination = parent / supplied_path.name
    try:
        destination.relative_to(root)
    except ValueError:
        pass
    else:
        raise InputError(
            f"manifest must be outside the scanned root: '{destination}'"
        )

    try:
        destination_stat = destination.lstat()
    except FileNotFoundError:
        return destination
    except OSError as error:
        raise InputError(f"cannot inspect manifest path '{destination}': {error}") from error

    if stat.S_ISLNK(destination_stat.st_mode):
        raise InputError(f"manifest path must not be a symbolic link: '{destination}'")
    return destination


def _raise_walk_error(error: OSError) -> NoReturn:
    raise ScanError(f"cannot scan '{error.filename or 'directory'}': {error}") from error


def _regular_files(root: Path) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []

    for current_text, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False, onerror=_raise_walk_error
    ):
        current = Path(current_text)
        kept_directories: list[str] = []
        for directory_name in sorted(directory_names):
            directory = current / directory_name
            try:
                item_stat = directory.lstat()
            except OSError as error:
                raise ScanError(f"cannot inspect '{directory}': {error}") from error
            if not stat.S_ISLNK(item_stat.st_mode):
                kept_directories.append(directory_name)
        directory_names[:] = kept_directories

        for file_name in sorted(file_names):
            file_path = current / file_name
            try:
                item_stat = file_path.lstat()
            except OSError as error:
                raise ScanError(f"cannot inspect '{file_path}': {error}") from error
            if stat.S_ISREG(item_stat.st_mode):
                relative_path = file_path.relative_to(root).as_posix()
                found.append((relative_path, file_path))

    found.sort(key=lambda item: item[0])
    return found


def _hash_file(path: Path) -> str:
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise ScanError(f"file changed type while scanning: '{path}'")

        open_flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        open_flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, open_flags)
        with os.fdopen(descriptor, "rb") as file_handle:
            opened = os.fstat(file_handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or (
                before.st_dev,
                before.st_ino,
            ) != (opened.st_dev, opened.st_ino):
                raise ScanError(f"file changed while scanning: '{path}'")

            digest = hashlib.sha256()
            while True:
                chunk = file_handle.read(HASH_CHUNK_SIZE)
                if not chunk:
                    break
                digest.update(chunk)

            after = os.fstat(file_handle.fileno())
            if (opened.st_size, opened.st_mtime_ns) != (
                after.st_size,
                after.st_mtime_ns,
            ):
                raise ScanError(f"file changed while scanning: '{path}'")
            return digest.hexdigest()
    except VerifierError:
        raise
    except OSError as error:
        raise ScanError(f"cannot read file '{path}': {error}") from error


def _collect_files(root: Path) -> list[dict[str, str]]:
    return [
        {"path": relative_path, "sha256": _hash_file(path)}
        for relative_path, path in _regular_files(root)
    ]


def _encode_manifest(files: list[dict[str, str]]) -> bytes:
    document = {"version": MANIFEST_VERSION, "files": files}
    return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def create_manifest(root_argument: str | Path, manifest_argument: str | Path) -> int:
    """Write a sorted manifest atomically and return the number of files included."""
    root = _resolve_root(root_argument)
    destination = _manifest_location(root, manifest_argument)

    # Complete the scan before creating any output, preserving an old manifest on failure.
    entries = _collect_files(root)
    contents = _encode_manifest(entries)
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(contents)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    except OSError as error:
        raise ManifestError(f"cannot write manifest '{destination}': {error}") from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass

    return len(entries)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON object key: '{key}'")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> NoReturn:
    raise ManifestError(f"invalid JSON constant: '{value}'")


def _validate_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError("manifest file path must be a non-empty string")
    if "\x00" in value or "\\" in value or value.startswith("/"):
        raise ManifestError(f"invalid manifest path: '{value}'")
    if _WINDOWS_DRIVE_PATTERN.match(value):
        raise ManifestError(f"absolute manifest path is not allowed: '{value}'")

    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value:
        raise ManifestError(f"manifest path is not a normalized relative POSIX path: '{value}'")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ManifestError(f"unsafe manifest path: '{value}'")
    return value


def _read_manifest(manifest_path: Path) -> dict[str, str]:
    try:
        manifest_stat = manifest_path.lstat()
    except OSError as error:
        raise ManifestError(f"cannot inspect manifest '{manifest_path}': {error}") from error
    if not stat.S_ISREG(manifest_stat.st_mode):
        raise ManifestError(f"manifest is not a regular file: '{manifest_path}'")

    try:
        with manifest_path.open("r", encoding="utf-8") as manifest_file:
            document = json.load(
                manifest_file,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_nonstandard_constant,
            )
    except ManifestError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManifestError(f"cannot read manifest '{manifest_path}': {error}") from error

    if not isinstance(document, dict) or set(document) != {"version", "files"}:
        raise ManifestError("manifest must contain exactly 'version' and 'files'")
    if type(document["version"]) is not int or document["version"] != MANIFEST_VERSION:
        raise ManifestError(f"unsupported manifest version: {document['version']!r}")
    entries = document["files"]
    if not isinstance(entries, list):
        raise ManifestError("manifest 'files' must be a list")

    expected: dict[str, str] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ManifestError(
                f"manifest file record {index} must contain exactly 'path' and 'sha256'"
            )
        relative_path = _validate_relative_path(entry["path"])
        digest = entry["sha256"]
        if not isinstance(digest, str) or not _SHA256_PATTERN.fullmatch(digest):
            raise ManifestError(f"invalid SHA-256 digest for '{relative_path}'")
        if relative_path in expected:
            raise ManifestError(f"duplicate manifest path: '{relative_path}'")
        expected[relative_path] = digest
    return expected


@dataclass(frozen=True)
class VerificationResult:
    missing: list[str]
    changed: list[str]
    unexpected: list[str]

    @property
    def clean(self) -> bool:
        return not (self.missing or self.changed or self.unexpected)


def verify_manifest(
    root_argument: str | Path, manifest_argument: str | Path
) -> VerificationResult:
    """Verify a directory against a validated manifest."""
    root = _resolve_root(root_argument)
    manifest_path = _manifest_location(root, manifest_argument)
    expected = _read_manifest(manifest_path)
    actual_entries = _collect_files(root)
    actual = {entry["path"]: entry["sha256"] for entry in actual_entries}

    missing = sorted(expected.keys() - actual.keys())
    changed = sorted(
        path for path in expected.keys() & actual.keys() if expected[path] != actual[path]
    )
    unexpected = sorted(actual.keys() - expected.keys())
    return VerificationResult(missing=missing, changed=changed, unexpected=unexpected)


def _add_json_option(parser: argparse.ArgumentParser, *, default: Any) -> None:
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        default=default,
        help="print a machine-readable JSON report",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backup-verifier",
        description="Create and verify SHA-256 manifests for directory backups.",
    )
    _add_json_option(parser, default=False)
    commands = parser.add_subparsers(dest="command", required=True)

    create_parser = commands.add_parser("create", help="create a deterministic manifest")
    _add_json_option(create_parser, default=argparse.SUPPRESS)
    create_parser.add_argument("root", help="directory tree to scan")
    create_parser.add_argument("manifest", help="manifest output path, outside ROOT")

    verify_parser = commands.add_parser("verify", help="verify a directory against a manifest")
    _add_json_option(verify_parser, default=argparse.SUPPRESS)
    verify_parser.add_argument("root", help="directory tree to scan")
    verify_parser.add_argument("manifest", help="manifest input path, outside ROOT")
    return parser


def _write_json_report(report: dict[str, Any]) -> None:
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


def main(arguments: list[str] | None = None) -> int:
    """Run the command-line interface and return its stable process status."""
    parser = _build_parser()
    options = parser.parse_args(arguments)

    try:
        if options.command == "create":
            count = create_manifest(options.root, options.manifest)
            if options.json_output:
                _write_json_report(
                    {
                        "command": "create",
                        "files": count,
                        "manifest": str(Path(options.manifest).expanduser().absolute()),
                        "ok": True,
                    }
                )
            else:
                print(f"Manifest created: {options.manifest}")
                print(f"Files: {count}")
            return 0

        result = verify_manifest(options.root, options.manifest)
        if options.json_output:
            _write_json_report(
                {
                    "changed": result.changed,
                    "command": "verify",
                    "missing": result.missing,
                    "ok": result.clean,
                    "unexpected": result.unexpected,
                }
            )
        elif result.clean:
            print("Backup matches manifest.")
        else:
            print("Backup differs from manifest.")
            for label, paths in (
                ("Missing", result.missing),
                ("Changed", result.changed),
                ("Unexpected", result.unexpected),
            ):
                if paths:
                    print(f"{label}:")
                    for path in paths:
                        print(f"  {path}")
        return 0 if result.clean else 1
    except VerifierError as error:
        error_type = (
            "scan"
            if isinstance(error, ScanError)
            else "manifest"
            if isinstance(error, ManifestError)
            else "input"
        )
        if getattr(options, "json_output", False):
            _write_json_report(
                {
                    "command": options.command,
                    "error": str(error),
                    "error_type": error_type,
                    "ok": False,
                }
            )
        else:
            print(f"{error_type} error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
