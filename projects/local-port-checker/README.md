# Local Port Checker

A small Python 3 command-line diagnostic that attempts one TCP connection to a
specified host and port. It does not scan port ranges or perform any other
discovery.

## Usage

```text
python port_checker.py HOST PORT [--timeout SECONDS]
```

For example:

```text
python port_checker.py example.com 443 --timeout 1.5
```

The default timeout is 2 seconds. The timeout must be finite, greater than 0,
and no more than 30 seconds. The TCP port must be an integer from 1 through
65535.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | The TCP connection succeeded. |
| `1` | The connection failed or timed out. |
| `2` | Invalid command-line arguments. |

## Tests

The test suite uses only the Python standard library and mocks sockets, so it
does not require network access:

```text
python -m unittest -v
```
