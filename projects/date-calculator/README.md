# Date Calculator

A Python 3 command-line utility for calculating signed day differences and
adding or subtracting an integer number of days. It uses only the standard
library.

## Requirements

Python 3.10 or newer.

## Usage

Run commands from this directory:

```console
python date_calculator.py between 2024-02-28 2024-03-01
```

Output:

```text
2 days (END - START)
```

`between START END` reports `END - START`; the result is negative when END is
earlier than START and zero when the dates are equal.

Use a positive offset to add days and a negative offset to subtract them:

```console
python date_calculator.py offset 2024-03-01 -1
```

Output:

```text
2024-03-01 - 1 day = 2024-02-29
```

Dates must use the exact `YYYY-MM-DD` format and represent valid calendar
dates. Offsets must be integers. Invalid input prints an error and exits with
status 2. Run `python date_calculator.py --help` for command help.

## Tests

```console
python -m unittest -v
```
