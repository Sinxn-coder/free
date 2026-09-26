#!/usr/bin/env python3
"""Offline static HTML accessibility checks using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence, TextIO


@dataclass
class Node:
    tag: str
    attributes: dict[str, str | None]
    line: int
    parent: int | None
    text_parts: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.text_parts).split())


@dataclass(frozen=True)
class Issue:
    file: str
    line: int
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class InputError:
    file: str
    message: str


class DocumentParser(HTMLParser):
    """Builds just enough document structure to evaluate semantic relationships."""

    VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.nodes: list[Node] = []
        self.stack: list[int] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        parent = self.stack[-1] if self.stack else None
        node = Node(
            tag=tag,
            attributes=dict(attrs),
            line=self.getpos()[0],
            parent=parent,
        )
        self.nodes.append(node)
        node_index = len(self.nodes) - 1
        if tag not in self.VOID_ELEMENTS:
            self.stack.append(node_index)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.nodes[self.stack[index]].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        for node_index in self.stack:
            self.nodes[node_index].text_parts.append(data)


def _has_text(value: str | None) -> bool:
    return bool(value and value.strip())


def audit_html(source: str, file_name: str = "<input>") -> list[Issue]:
    """Return actionable findings from one HTML document."""
    parser = DocumentParser()
    parser.feed(source)
    parser.close()
    nodes = parser.nodes
    issues: list[Issue] = []

    def report(
        line: int, code: str, severity: str, message: str
    ) -> None:
        issues.append(Issue(file_name, line, code, severity, message))

    titles = [node for node in nodes if node.tag == "title"]
    if not titles:
        report(1, "A11Y001", "error", "Document is missing a <title>.")
    elif not titles[0].text:
        report(titles[0].line, "A11Y002", "error", "Document title is empty.")

    html_elements = [node for node in nodes if node.tag == "html"]
    if not html_elements or not _has_text(html_elements[0].attributes.get("lang")):
        line = html_elements[0].line if html_elements else 1
        report(line, "A11Y003", "error", "The <html> element is missing a non-empty lang attribute.")

    identifiers: dict[str, Node] = {}
    for node in nodes:
        identifier = node.attributes.get("id")
        if identifier:
            if identifier in identifiers:
                report(
                    node.line,
                    "A11Y005",
                    "error",
                    f"Duplicate id {identifier!r}; first used on line {identifiers[identifier].line}.",
                )
            else:
                identifiers[identifier] = node

    labels_by_control_id: dict[str, list[Node]] = {}
    for node in nodes:
        if node.tag == "label":
            control_id = node.attributes.get("for")
            if control_id:
                labels_by_control_id.setdefault(control_id, []).append(node)

    previous_heading_level: int | None = None
    for node_index, node in enumerate(nodes):
        if node.tag == "img" and "alt" not in node.attributes:
            report(node.line, "A11Y004", "error", "Image is missing an alt attribute.")

        if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            heading_level = int(node.tag[1])
            if (
                previous_heading_level is not None
                and heading_level > previous_heading_level + 1
            ):
                report(
                    node.line,
                    "A11Y007",
                    "warning",
                    f"Heading level skips from h{previous_heading_level} to {node.tag}.",
                )
            previous_heading_level = heading_level

        if node.tag not in {"input", "select", "textarea", "button"}:
            continue
        if node.tag == "input" and (node.attributes.get("type") or "").lower() == "hidden":
            continue

        has_name = _has_text(node.attributes.get("aria-label"))
        if not has_name:
            labelled_by = (node.attributes.get("aria-labelledby") or "").split()
            has_name = any(
                identifier in identifiers and identifiers[identifier].text
                for identifier in labelled_by
            )
        control_id = node.attributes.get("id")
        if not has_name and control_id:
            has_name = any(
                label.text for label in labels_by_control_id.get(control_id, [])
            )
        if not has_name:
            ancestor_index = node.parent
            while ancestor_index is not None:
                ancestor = nodes[ancestor_index]
                if ancestor.tag == "label" and ancestor.text:
                    has_name = True
                    break
                ancestor_index = ancestor.parent
        if not has_name and node.tag == "button":
            has_name = bool(node.text)
        if not has_name and node.tag == "input":
            input_type = (node.attributes.get("type") or "").lower()
            has_name = (
                input_type in {"submit", "reset", "button"}
                and _has_text(node.attributes.get("value"))
            ) or (input_type == "image" and _has_text(node.attributes.get("alt")))

        if not has_name:
            report(
                node.line,
                "A11Y006",
                "error",
                f"<{node.tag}> form control has no accessible name.",
            )

    return sorted(issues, key=lambda issue: (issue.line, issue.code))


def collect_files(inputs: Sequence[str]) -> tuple[list[Path], list[InputError]]:
    """Expand file and directory arguments in stable order without following directory symlinks."""
    files: list[Path] = []
    errors: list[InputError] = []
    html_suffixes = {".html", ".htm"}

    def walk(directory: Path) -> None:
        try:
            entries = sorted(
                directory.iterdir(), key=lambda entry: (entry.name.casefold(), entry.name)
            )
        except OSError as error:
            errors.append(InputError(str(directory), str(error)))
            return

        for entry in entries:
            try:
                if entry.is_symlink() and entry.is_dir():
                    continue
                if entry.is_dir():
                    walk(entry)
                elif entry.is_file() and entry.suffix.lower() in html_suffixes:
                    files.append(entry)
            except OSError as error:
                errors.append(InputError(str(entry), str(error)))

    for raw_path in inputs:
        path = Path(raw_path)
        try:
            if path.is_symlink() and path.is_dir():
                errors.append(InputError(str(path), "refusing to traverse a symlink directory"))
            elif path.is_dir():
                walk(path)
            elif path.is_file():
                files.append(path)
            else:
                errors.append(InputError(str(path), "not a readable file or directory"))
        except OSError as error:
            errors.append(InputError(str(path), str(error)))
    return files, errors


def build_report(
    issues: Sequence[Issue], errors: Sequence[InputError], files_scanned: int
) -> dict[str, object]:
    return {
        "files_scanned": files_scanned,
        "summary": {
            "errors": sum(issue.severity == "error" for issue in issues),
            "warnings": sum(issue.severity == "warning" for issue in issues),
            "input_errors": len(errors),
        },
        "issues": [asdict(issue) for issue in issues],
        "input_errors": [asdict(error) for error in errors],
    }


def run(
    inputs: Sequence[str],
    output_format: str = "text",
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    files, input_errors = collect_files(inputs)
    issues: list[Issue] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            input_errors.append(InputError(str(path), str(error)))
            continue
        issues.extend(audit_html(source, str(path)))

    if output_format == "json":
        print(
            json.dumps(build_report(issues, input_errors, len(files)), indent=2),
            file=stdout,
        )
    else:
        for issue in issues:
            print(
                f"{issue.file}:{issue.line}: {issue.severity.upper()} "
                f"{issue.code} {issue.message}",
                file=stdout,
            )
        for error in input_errors:
            print(f"{error.file}: INPUT ERROR {error.message}", file=stderr)

        if not issues and not input_errors:
            print(f"Scanned {len(files)} file(s): no accessibility issues found.", file=stdout)
        else:
            error_count = sum(issue.severity == "error" for issue in issues)
            warning_count = sum(issue.severity == "warning" for issue in issues)
            print(
                f"Scanned {len(files)} file(s): {error_count} error(s), "
                f"{warning_count} warning(s), {len(input_errors)} input error(s).",
                file=stdout,
            )

    if input_errors:
        return 2
    return 1 if issues else 0


def make_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run offline static accessibility checks on HTML files and directories. "
            "Findings are limited and do not certify WCAG conformance."
        ),
        epilog=(
            "Examples: python a11y_audit.py index.html; "
            "python a11y_audit.py site/ --format json"
        ),
    )
    parser.add_argument("paths", nargs="+", help="HTML file(s) or directory(ies) to audit")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = make_argument_parser().parse_args(argv)
    return run(arguments.paths, arguments.format)


if __name__ == "__main__":
    raise SystemExit(main())
