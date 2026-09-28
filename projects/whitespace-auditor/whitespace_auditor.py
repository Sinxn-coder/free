#!/usr/bin/env python3
"""Report or remove trailing whitespace and missing final newlines."""

from __future__ import annotations

import argparse
import os
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    line: int
    message: str


def _encoding_for(data: bytes) -> str:
    if data.startswith((b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")):
        return "utf-32"
    if data.startswith((b"\xfe\xff", b"\xff\xfe")):
        return "utf-16"
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    return "utf-8"


def _split_lines(text: str) -> list[tuple[str, str]]:
    """Split only on CR and LF, retaining each exact newline sequence."""
    lines: list[tuple[str, str]] = []
    start = 0
    index = 0
    while index < len(text):
        if text[index] == "\r":
            end = index + 1
            if end < len(text) and text[end] == "\n":
                end += 1
            lines.append((text[start:index], text[index:end]))
            start = end
            index = end
        elif text[index] == "\n":
            lines.append((text[start:index], "\n"))
            start = index + 1
            index += 1
        else:
            index += 1
    if start < len(text):
        lines.append((text[start:], ""))
    return lines


def inspect_text(text: str) -> tuple[list[Finding], str]:
    lines = _split_lines(text)
    findings = [
        Finding(number, "trailing whitespace")
        for number, (content, _) in enumerate(lines, start=1)
        if content != content.rstrip()
    ]
    if lines and not lines[-1][1]:
        findings.append(Finding(len(lines), "missing final newline"))

    newline = next((ending for _, ending in lines if ending), "\n")
    fixed_text = "".join(content.rstrip() + ending for content, ending in lines)
    if lines and not lines[-1][1]:
        fixed_text += newline
    return findings, fixed_text


def write_atomically(path: Path, data: bytes) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    except OSError:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def _files_from_paths(paths: list[Path]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    for path in paths:
        try:
            if path.is_dir():
                files.extend(sorted(child for child in path.rglob("*") if child.is_file()))
            elif path.is_file():
                files.append(path)
            else:
                errors.append(f"{path}: not a file or directory")
        except OSError as error:
            errors.append(f"{path}: {error}")
    return files, errors


def run(paths: list[Path], fix: bool = False) -> int:
    files, errors = _files_from_paths(paths)
    found_any = False
    for error in errors:
        print(error, file=sys.stderr)

    for path in files:
        try:
            raw = path.read_bytes()
            encoding = _encoding_for(raw)
            text = raw.decode(encoding)
            findings, fixed_text = inspect_text(text)
            if not findings:
                continue
            found_any = True
            if fix:
                fixed_bytes = fixed_text.encode(encoding)
                if fixed_bytes != raw:
                    write_atomically(path, fixed_bytes)
                print(f"{path}: fixed {len(findings)} issue(s)")
            else:
                for finding in findings:
                    print(f"{path}:{finding.line}: {finding.message}")
        except (OSError, UnicodeError) as error:
            errors.append(f"{path}: {error}")
            print(errors[-1], file=sys.stderr)

    if errors:
        return 2
    return 1 if found_any and not fix else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find trailing whitespace and files missing a final newline."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="remove the reported issues and atomically replace changed files",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="files or directories to inspect (directories are searched recursively)",
    )
    args = parser.parse_args(argv)
    return run(args.paths, fix=args.fix)


if __name__ == "__main__":
    raise SystemExit(main())
