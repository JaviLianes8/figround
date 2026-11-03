# figround

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

Significant-figures rounding and formatting with exact Decimal math and preserved trailing zeros

## Install

```
pip install figround
```

## Usage

```python
from figround import (
    count_sig, format_sig, format_uncertainty, round_decimal, round_sig, sig_bounds,
)

round_sig(123456, 3)        # 123000.0
round_sig(2.675, 3)         # 2.68, exact: no binary float drift
round_decimal(1.2, 3)       # Decimal('1.20'), the exponent records the figures
round_decimal("2.5", 1, rounding="half_up")  # Decimal('3'), eight rounding modes

format_sig(1.2, 3)          # "1.20", trailing zeros kept
format_sig(0, 3)            # "0.00"
format_sig(0.00012345, 2, sci=True)          # "1.2e-04"
format_sig(123456, 4, notation="eng")        # "123.5e+03"
format_sig(1000, 4, trailing_point=True)     # "1000."

count_sig("0.00120")        # 3
count_sig("6.022e23")       # 4
sig_bounds("1200")          # (2, 4), trailing zeros without a point are ambiguous

format_uncertainty(100.02147, 0.00035)               # "100.02147(35)"
format_uncertainty(100.02147, 0.00035, style="pm")   # "100.02147 +/- 0.00035"
```

Rounding and formatting accept an `int`, `float`, `str` or `Decimal`.
Integer inputs are limited to 65536 bits; use decimal text or `Decimal` for larger values.
Counting accepts only `str` or `Decimal`, which can record trailing zeros. Values are converted
through `decimal.Decimal` so the rounding matches the decimal digits you see rather
than the binary approximation: a float is read through `repr`, so
`round_sig(2.675, 3)` is `2.68`, not `2.67`. Rounding is half to even by default
(NIST SP 811 B.7.1, the IEEE 754 default) and every `decimal` rounding mode is
available. Values with an uncertainty follow the GUM (JCGM 100:2008, clause 7.2):
the uncertainty keeps two significant figures and the value is rounded to match.

Errors are typed (`InvalidNumberError`, `InvalidFiguresError`, `InvalidOptionError`,
`AmbiguousFiguresError`, `UncertaintyError`), all subclasses of `FigroundError` and
of `ValueError`.

## Command line

```
figround round 2.675 3                    # 2.68
figround round 123456 2 --notation sci    # 1.2e+05
figround count 0.00120 1200 1200.         # 3, 2, 4
figround format 100.02147 -u 0.00035      # 100.02147(35)
```

See [GUIDE](https://github.com/JaviLianes8/sigfigs/blob/main/GUIDE.md) for every rule, the command options, the cited sources and
how the results differ from `format(x, ".{n}g")`.

## Why

Python's built-in `format(x, ".3g")` already rounds to significant figures.
Use it when its choice of notation and handling of trailing zeros fit your output.
`Decimal.quantize` is a good choice when you know the decimal place to round to.

`figround` combines explicit fixed, scientific and engineering notation, eight
rounding modes, preserved trailing zeros, and value-with-uncertainty formatting.
It reads floats through `repr`, so `format_sig(2.675, 3)` gives `"2.68"` while
`format(2.675, ".3g")` gives `"2.67"`. It has no runtime dependencies and ships
Python type information. Counting follows the documented written-number convention;
it cannot recover precision that was lost before a number became a float.

## Development

Requires Python 3.10 or newer. Install `.[dev]`, then run `scripts/check.ps1`.
`python scripts/fetch_upstream.py` fetches the optional decimal reference archive;
set `FIGROUND_UPSTREAM_DIR` to store it outside the checkout. Tests skip that archive
when it is absent. See the [CHANGELOG](https://github.com/JaviLianes8/sigfigs/blob/main/CHANGELOG.md)
for release changes.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/sigfigs/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
