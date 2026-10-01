import io
import socket
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

import link_checker


PUBLIC_RECORD = (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", 80))
PRIVATE_RECORD = (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("127.0.0.1", 80))


class URLValidationTests(unittest.TestCase):
    @mock.patch("link_checker.socket.getaddrinfo", return_value=[PUBLIC_RECORD])
    def test_accepts_public_http_url(self, _getaddrinfo):
        parsed = link_checker.validate_url("http://example.com/path")
        self.assertEqual(parsed.hostname, "example.com")

    @mock.patch("link_checker.socket.getaddrinfo", return_value=[PRIVATE_RECORD])
    def test_rejects_private_address(self, _getaddrinfo):
        with self.assertRaisesRegex(link_checker.URLCheckError, "non-public"):
            link_checker.validate_url("http://localhost/")

    @mock.patch("link_checker.socket.getaddrinfo", return_value=[PUBLIC_RECORD])
    @mock.patch("link_checker.socket.socket")
    def test_connects_to_the_validated_address(self, create_socket, _getaddrinfo):
        sock = create_socket.return_value
        result = link_checker._connect_to_public_address(("example.com", 80), 2)
        self.assertIs(result, sock)
        sock.connect.assert_called_once_with(PUBLIC_RECORD[4])

    def test_rejects_non_http_scheme_without_dns(self):
        with mock.patch("link_checker.socket.getaddrinfo") as getaddrinfo:
            with self.assertRaisesRegex(link_checker.URLCheckError, "only http and https"):
                link_checker.validate_url("file:///etc/passwd")
        getaddrinfo.assert_not_called()

    def test_rejects_embedded_credentials(self):
        with mock.patch("link_checker.socket.getaddrinfo", return_value=[PUBLIC_RECORD]):
            with self.assertRaisesRegex(link_checker.URLCheckError, "credentials"):
                link_checker.validate_url("http://user:password@example.com/")


class URLCheckingTests(unittest.TestCase):
    @mock.patch("link_checker.socket.getaddrinfo", return_value=[PUBLIC_RECORD])
    @mock.patch("link_checker.urllib.request.build_opener")
    def test_reports_success(self, build_opener, _getaddrinfo):
        response = mock.MagicMock()
        response.getcode.return_value = 200
        response.reason = "OK"
        response.__enter__.return_value = response
        build_opener.return_value.open.return_value = response

        result = link_checker._check_one("http://example.com/", 1)

        self.assertEqual(result.status, "OK")
        self.assertEqual(result.detail, "HTTP 200 OK")
        build_opener.return_value.open.assert_called_once_with("http://example.com/", timeout=1)

    @mock.patch("link_checker.socket.getaddrinfo", return_value=[PUBLIC_RECORD])
    @mock.patch("link_checker.urllib.request.build_opener")
    def test_reports_http_error_status(self, build_opener, _getaddrinfo):
        build_opener.return_value.open.side_effect = urllib.error.HTTPError(
            "http://example.com/missing", 404, "Not Found", {}, io.BytesIO()
        )
        result = link_checker._check_one("http://example.com/missing", 1)
        self.assertEqual(result.status, "HTTP_ERROR")
        self.assertEqual(result.detail, "HTTP 404 Not Found")

    @mock.patch("link_checker.socket.getaddrinfo", return_value=[PUBLIC_RECORD])
    def test_redirect_to_private_address_is_rejected(self, _getaddrinfo):
        handler = link_checker._PublicRedirectHandler()
        with mock.patch("link_checker.socket.getaddrinfo", return_value=[PRIVATE_RECORD]):
            with self.assertRaisesRegex(link_checker.URLCheckError, "non-public"):
                handler.redirect_request(
                    urllib.request.Request("http://example.com/"),
                    io.BytesIO(),
                    302,
                    "Found",
                    {},
                    "http://127.0.0.1/",
                )


class InputAndCLITests(unittest.TestCase):
    def test_skips_blank_lines_and_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "urls.txt"
            path.write_text("\n  # ignored\nhttps://example.com\n  http://example.org  \n", encoding="utf-8")
            self.assertEqual(
                link_checker._read_urls(path),
                ["https://example.com", "http://example.org"],
            )

    def test_help_exits_successfully(self):
        with self.assertRaises(SystemExit) as raised:
            link_checker.main(["--help"])
        self.assertEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
