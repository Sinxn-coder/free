# Color Palette

Generate HEX colors:

```text
python palette.py --count 5
python palette.py --count 5 --seed 42
python palette.py --count 5 --seed 42 --unique
```

Use a seed when you want a repeatable palette.
Pass `--unique` to guarantee that every color in the palette is different.
In Python, use `palette(count, seed=None, unique=False)`; unique palettes are
limited to the 16,777,216 possible HEX colors.
