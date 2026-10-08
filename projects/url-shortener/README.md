# URL Shortener

Create local short codes for URLs:

```text
python shortener.py https://example.com
python shortener.py abc12345 --expand
```

Codes use the first eight characters of the URL's SHA-256 digest. If that code
is already assigned to a different URL, the code is extended until it is
unique; existing codes are not replaced. Mappings are stored locally in
`urls.json`. This is a learning project, not a hosted internet URL service.
