# Random Quote Printer

Print a quote from the built-in categories:

```text
python quotes.py
python quotes.py --category motivation
python quotes.py --seed 42
python quotes.py --category learning --seed 42
```

Use `--seed` with an integer to make the random selection reproducible. Omitting
it preserves the default random selection. You can combine it with `--category`
to get a reproducible quote from a specific category.

The quote collection is stored directly in the script for easy editing.
