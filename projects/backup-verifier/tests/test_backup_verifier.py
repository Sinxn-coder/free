from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import backup_verifier


class BackupVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)
        self.root = self.base / "source"
        self.root.mkdir()
        self.manifest = self.base / "backup-manifest.json"

    def write_file(self, relative_path: str, contents: bytes) -> None:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)

    def create(self) -> None:
        backup_verifier.create_manifest(self.root, self.manifest)

    def test_manifest_is_deterministic_and_paths_are_sorted(self) -> None:
        self.write_file("z-last.txt", b"last")
        self.write_file("dir/a-first.txt", b"first")
        first = backup_verifier.create_manifest(self.root, self.manifest)
        initial_bytes = self.manifest.read_bytes()

        second = backup_verifier.create_manifest(self.root, self.manifest)

        self.assertEqual(first, 2)
        self.assertEqual(second, 2)
        self.assertEqual(self.manifest.read_bytes(), initial_bytes)
        document = json.loads(initial_bytes)
        self.assertEqual(
            [entry["path"] for entry in document["files"]],
            ["dir/a-first.txt", "z-last.txt"],
        )

    def test_clean_tree_verifies(self) -> None:
        self.write_file("nested/data.bin", b"contents")
        self.create()

        result = backup_verifier.verify_manifest(self.root, self.manifest)

        self.assertTrue(result.clean)
        self.assertEqual(result.missing, [])
        self.assertEqual(result.changed, [])
        self.assertEqual(result.unexpected, [])

    def test_reports_missing_changed_and_unexpected_separately(self) -> None:
        self.write_file("missing.txt", b"will be deleted")
        self.write_file("changed.txt", b"original")
        self.create()
        (self.root / "missing.txt").unlink()
        (self.root / "changed.txt").write_bytes(b"modified")
        self.write_file("extra.txt", b"not in manifest")

        result = backup_verifier.verify_manifest(self.root, self.manifest)

        self.assertEqual(result.missing, ["missing.txt"])
        self.assertEqual(result.changed, ["changed.txt"])
        self.assertEqual(result.unexpected, ["extra.txt"])
        self.assertFalse(result.clean)

    def test_manifest_inside_scanned_root_is_rejected(self) -> None:
        with self.assertRaisesRegex(backup_verifier.VerifierError, "outside"):
            backup_verifier.create_manifest(self.root, self.root / "manifest.json")

    def test_symlink_files_and_directories_are_not_followed(self) -> None:
        outside_file = self.base / "outside.txt"
        outside_file.write_text("not scanned", encoding="utf-8")
        self.write_file("included.txt", b"included")
        file_link = self.root / "linked.txt"
        directory_link = self.root / "linked-directory"
        try:
            file_link.symlink_to(outside_file)
            directory_link.symlink_to(self.base, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlinks are unavailable: {error}")

        self.create()

        paths = [entry["path"] for entry in json.loads(self.manifest.read_text())["files"]]
        self.assertEqual(paths, ["included.txt"])

    def test_rejects_traversal_paths_before_scanning(self) -> None:
        self.manifest.write_text(
            json.dumps(
                {
                    "version": 1,
                    "files": [{"path": "../outside.txt", "sha256": "0" * 64}],
                }
            ),
            encoding="utf-8",
        )
        with mock.patch.object(
            backup_verifier, "_collect_files", side_effect=AssertionError("scan called")
        ):
            with self.assertRaisesRegex(backup_verifier.VerifierError, "unsafe"):
                backup_verifier.verify_manifest(self.root, self.manifest)

    def test_rejects_duplicate_paths_bad_digest_and_unknown_version(self) -> None:
        for entries, version, message in (
            (
                [
                    {"path": "same.txt", "sha256": "0" * 64},
                    {"path": "same.txt", "sha256": "1" * 64},
                ],
                1,
                "duplicate",
            ),
            ([{"path": "file.txt", "sha256": "xyz"}], 1, "digest"),
            ([], 2, "version"),
        ):
            with self.subTest(message=message):
                self.manifest.write_text(
                    json.dumps({"version": version, "files": entries}), encoding="utf-8"
                )
                with self.assertRaisesRegex(backup_verifier.VerifierError, message):
                    backup_verifier.verify_manifest(self.root, self.manifest)

    def test_failed_scan_preserves_existing_manifest(self) -> None:
        self.write_file("source.txt", b"contents")
        self.manifest.write_bytes(b"previous manifest")
        with mock.patch.object(
            backup_verifier, "_hash_file", side_effect=backup_verifier.ScanError("read failed")
        ):
            with self.assertRaisesRegex(backup_verifier.ScanError, "read failed"):
                backup_verifier.create_manifest(self.root, self.manifest)
        self.assertEqual(self.manifest.read_bytes(), b"previous manifest")

    def test_failed_atomic_replace_preserves_existing_manifest(self) -> None:
        self.write_file("source.txt", b"contents")
        self.manifest.write_bytes(b"previous manifest")
        with mock.patch.object(
            backup_verifier.os, "replace", side_effect=OSError("replace failed")
        ):
            with self.assertRaisesRegex(backup_verifier.ManifestError, "replace failed"):
                backup_verifier.create_manifest(self.root, self.manifest)
        self.assertEqual(self.manifest.read_bytes(), b"previous manifest")
        self.assertEqual(list(self.base.glob(".backup-manifest.json.*.tmp")), [])

    def test_cli_exit_codes_and_json_reports(self) -> None:
        self.write_file("file.txt", b"original")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(
                backup_verifier.main(
                    ["--json", "create", str(self.root), str(self.manifest)]
                ),
                0,
            )
        self.assertTrue(json.loads(output.getvalue())["ok"])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(
                backup_verifier.main(
                    ["verify", str(self.root), str(self.manifest), "--json"]
                ),
                0,
            )
        self.assertTrue(json.loads(output.getvalue())["ok"])

        (self.root / "file.txt").write_bytes(b"changed")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(
                backup_verifier.main(
                    ["verify", str(self.root), str(self.manifest), "--json"]
                ),
                1,
            )
        self.assertEqual(json.loads(output.getvalue())["changed"], ["file.txt"])

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(
                backup_verifier.main(
                    ["verify", str(self.root), str(self.base / "absent.json"), "--json"]
                ),
                2,
            )
        error_report = json.loads(output.getvalue())
        self.assertFalse(error_report["ok"])
        self.assertEqual(error_report["error_type"], "manifest")

    def test_rejects_absolute_paths_and_malformed_records(self) -> None:
        for entry, message in (
            ({"path": "/outside.txt", "sha256": "0" * 64}, "invalid"),
            ({"path": "file.txt"}, "exactly"),
        ):
            with self.subTest(message=message):
                self.manifest.write_text(
                    json.dumps({"version": 1, "files": [entry]}), encoding="utf-8"
                )
                with self.assertRaisesRegex(backup_verifier.ManifestError, message):
                    backup_verifier.verify_manifest(self.root, self.manifest)

    @unittest.skipIf(os.name == "nt", "permission bits do not prevent reads on Windows")
    def test_scan_error_does_not_replace_manifest(self) -> None:
        self.write_file("source.txt", b"contents")
        self.manifest.write_bytes(b"previous manifest")
        (self.root / "source.txt").chmod(0)
        try:
            with self.assertRaises(backup_verifier.ScanError):
                backup_verifier.create_manifest(self.root, self.manifest)
        finally:
            (self.root / "source.txt").chmod(0o600)
        self.assertEqual(self.manifest.read_bytes(), b"previous manifest")


if __name__ == "__main__":
    unittest.main()
