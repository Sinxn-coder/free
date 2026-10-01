# HTTP Link Checker

A Python 3.10+ command-line utility that checks HTTP and HTTPS URLs from a
text file. It uses only the Python standard library and follows HTTP redirects.

## Usage

Put one URL per line in a UTF-8 text file. Blank lines and lines whose first
non-whitespace character is `#` are ignored.

```text
https://example.com/
https://www.python.org/
# This line is ignored
```

Run the checker:

```console
python link_checker.py urls.txt
python link_checker.py urls.txt --timeout 5 --workers 8
```

`--timeout` sets the timeout in seconds for each request (default: 10).
`--workers` limits concurrent requests to 1-64 (default: 4; use `1` for sequential
checking). Output is kept in input order and shows `OK`, `HTTP_ERROR`,
`BLOCKED`, or `ERROR` for each URL. The process exits with status 1 if any URL
was not successful, and status 2 if the input file cannot be read.

## Network safety

The checker makes outbound network requests to the URLs in the input file.
Only HTTP and HTTPS URLs are accepted; embedded credentials are rejected.
Before connecting, it resolves each host and rejects destinations whose
addresses are not globally routable, including private, loopback, link-local,
and reserved addresses. It connects to a validated resolved address directly
(without using environment-configured proxies), and validates each redirect
destination under the same rules. Use only with URL lists you trust.

## Tests

Run the standard-library tests from this directory:

```console
python -m unittest -v
```

All network and DNS interactions in the tests are mocked; the tests do not
depend on a live network.
