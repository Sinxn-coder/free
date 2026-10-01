import contextlib
import io
import unittest
from unittest import mock

import port_checker


class ParsePortTests(unittest.TestCase):
    def test_accepts_valid_port(self):
        self.assertEqual(port_checker.parse_port("443"), 443)

    def test_rejects_non_integer_port(self):
        with self.assertRaises(port_checker.argparse.ArgumentTypeError):
            port_checker.parse_port("http")

    def test_rejects_port_outside_tcp_range(self):
        for value in ("0", "65536"):
            with self.subTest(value=value), self.assertRaises(port_checker.argparse.ArgumentTypeError):
                port_checker.parse_port(value)


class ParseTimeoutTests(unittest.TestCase):
    def test_accepts_finite_positive_timeout(self):
        self.assertEqual(port_checker.parse_timeout("0.5"), 0.5)

    def test_rejects_non_positive_non_finite_and_too_large_timeouts(self):
        for value in ("0", "-1", "nan", "inf", "30.1"):
            with self.subTest(value=value), self.assertRaises(port_checker.argparse.ArgumentTypeError):
                port_checker.parse_timeout(value)


class CheckConnectionTests(unittest.TestCase):
    @mock.patch("port_checker.socket.create_connection")
    def test_success_closes_socket_and_passes_timeout(self, create_connection):
        connection = mock.MagicMock()
        create_connection.return_value.__enter__.return_value = connection

        result, message = port_checker.check_connection("localhost", 8080, 0.25)

        self.assertTrue(result)
        self.assertEqual(message, "Connected to localhost:8080")
        create_connection.assert_called_once_with(("localhost", 8080), timeout=0.25)
        create_connection.return_value.__exit__.assert_called_once()

    @mock.patch("port_checker.socket.create_connection", side_effect=TimeoutError("timed out"))
    def test_connection_failure_returns_diagnostic(self, create_connection):
        result, message = port_checker.check_connection("example.test", 443, 1.0)

        self.assertFalse(result)
        self.assertIn("Could not connect to example.test:443", message)
        self.assertIn("timed out", message)


class MainTests(unittest.TestCase):
    @mock.patch("port_checker.socket.create_connection")
    def test_reachable_target_returns_success(self, create_connection):
        create_connection.return_value.__enter__.return_value = mock.MagicMock()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            result = port_checker.main(["localhost", "80"])

        self.assertEqual(result, port_checker.EXIT_SUCCESS)
        self.assertIn("Connected to localhost:80", output.getvalue())

    @mock.patch("port_checker.socket.create_connection", side_effect=OSError("refused"))
    def test_unreachable_target_returns_failure(self, create_connection):
        errors = io.StringIO()

        with contextlib.redirect_stderr(errors):
            result = port_checker.main(["localhost", "80"])

        self.assertEqual(result, port_checker.EXIT_UNREACHABLE)
        self.assertIn("refused", errors.getvalue())

    def test_invalid_arguments_return_usage_exit_code(self):
        for arguments in (["localhost", "0"], ["localhost", "80", "--timeout", "nan"], ["", "80"]):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    port_checker.main(arguments)
            self.assertEqual(raised.exception.code, port_checker.EXIT_USAGE)


if __name__ == "__main__":
    unittest.main()
