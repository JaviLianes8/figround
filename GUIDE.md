# figround guide

This guide covers every public name, the rules each one follows and where the
standard library behaves differently. All arithmetic is exact decimal arithmetic
through `decimal.Decimal`; no step goes through a binary float except the final
conversion in `round_sig`.

## Inputs

Rounding and formatting accept `int`, `float`, `str` or `Decimal`
(`figround.Number`). Booleans and other types raise `TypeError`.

- A `str` is parsed by `Decimal`, so `"1.20"`, `"-3e-4"` and `" 42 "` work.
- A `float` is read through `repr(x)`, the shortest text that round-trips to the
  same float. `2.675` is therefore the decimal 2.675, not the binary value
  2.67499999999999982236431605997495353221893310546875 that the float stores.
  This is what you typed, and it is why `format_sig(2.675, 3)` is `"2.68"` while
  `format(2.675, ".3g")` is `"2.67"`. Pass `Decimal(x)` if you want the exact
  binary value instead.
- NaN, infinities and unparsable text raise `InvalidNumberError`.
- Rounding accepts any text `Decimal` accepts, including `"1_000"`; counting
  (below) accepts only plain ASCII decimal text, since it reads the digits as written.

Limits: `figures` is at most 10000 (`InvalidFiguresError` above it); a value whose
exponent leaves the decimal range raises `InvalidNumberError`; fixed notation writes
at most 10000 placeholder zeros and raises `InvalidNumberError` beyond that, so very
large or small magnitudes need `notation="sci"`. `round_sig` returns a `float`, so a
result beyond the float range becomes `inf` or `0.0`; `round_decimal` does not.

## Rounding: `round_decimal`, `round_sig`

```python
from decimal import Decimal
from figround import (
    AmbiguousFiguresError, count_sig, format_sig, format_uncertainty,
    round_decimal, round_sig, round_uncertainty, sig_bounds,
)

round_decimal(1.2, 3)                     # Decimal('1.20')
round_decimal(123456, 2)                  # Decimal('1.2E+5')
round_decimal("2.5", 1, rounding="half_up")  # Decimal('3')
round_sig(0.0125, 2, rounding="half_up")  # 0.013
```

`round_decimal` returns a `Decimal` with exactly `figures` coefficient digits for a nonzero result, so
its exponent records which digits are significant. `round_sig` converts that to
`float` (the 0.1.0 function, unchanged by default).

`rounding` is one of `figround.ROUNDING_MODES`:

| mode | rule |
| --- | --- |
| `half_even` (default) | nearest; ties to the even digit |
| `half_up` | nearest; ties away from zero |
| `half_down` | nearest; ties toward zero |
| `up` | away from zero |
| `down` | toward zero (truncate) |
| `ceiling` | toward positive infinity |
| `floor` | toward negative infinity |
| `05up` | toward zero, unless the last kept digit would be 0 or 5, then away |

The default is the rule of NIST SP 811 Appendix B.7.1 (which cites ISO 31-0, the
predecessor of ISO 80000-1) and the default rounding of IEEE 754. The modes are the
algorithms of the General Decimal Arithmetic specification, which the `decimal`
module implements; the test suite runs the `add` blocks of its `rounding.decTest`
file against every mode.

Zero rounds to a positive zero with `figures - 1` decimal places
(`round_decimal(0, 3)` is `Decimal('0.00')`), the convention `format_sig` writes.

## Formatting: `format_sig`

```python
from decimal import Decimal
from figround import (
    AmbiguousFiguresError, count_sig, format_sig, format_uncertainty,
    round_decimal, round_sig, round_uncertainty, sig_bounds,
)

format_sig(1.2, 3)                      # '1.20'
format_sig(0.00012345, 2, sci=True)     # '1.2e-04'
format_sig(123456, 4, notation="eng")   # '123.5e+03'
format_sig(1000, 4, trailing_point=True)  # '1000.'
```

- `notation="fixed"` (default) writes every digit positionally.
- `notation="sci"` writes one digit before the point; `sci=True` is the 0.1.0
  spelling and conflicts with any other `notation`.
- `notation="eng"` uses exponents that are multiples of three.
- Exponents are written with a sign and at least two digits: `e+03`, `e-04`.

Significant trailing zeros are always written. When fewer figures are requested
than there are digits before the point, the placeholder zeros are ambiguous on
paper (`format_sig(1234, 2)` is `"1200"`, which a reader may take as 2 to 4
figures); use `notation="sci"` to avoid it. Engineering notation can show the same
ambiguity inside its mantissa (`format_sig(12, 1, notation="eng")` is `"10e+00"`,
`format_sig(0.000123, 2, notation="eng")` is `"120e-06"`), and `trailing_point`
cannot mark it there. `trailing_point=True` adds a final
point to a whole number whose zeros are all significant (`"1000."`), the usual
way to mark them.

## Counting: `count_sig`, `sig_bounds`

```python
from decimal import Decimal
from figround import (
    AmbiguousFiguresError, count_sig, format_sig, format_uncertainty,
    round_decimal, round_sig, round_uncertainty, sig_bounds,
)

count_sig("0.0450")        # 3
count_sig("6.022e23")      # 4
sig_bounds("1200")         # (2, 4)
try:
    count_sig("1200", strict=True)
except AmbiguousFiguresError:
    pass
```

Rules:

1. Leading zeros never count.
2. Zeros between nonzero digits count.
3. With a decimal point, trailing zeros count (`"1200."` is 4, `"0.00120"` is 3).
4. Without a point, trailing zeros of a whole number are ambiguous: `sig_bounds`
   returns both readings, `count_sig` returns the smaller one, and
   `count_sig(..., strict=True)` raises `AmbiguousFiguresError`.
5. In scientific notation only the mantissa counts (`"1.20e3"` is 3).
6. A zero counts one plus its decimal places (`"0"` is 1, `"0.00"` is 3).

A `Decimal` is exact: every coefficient digit counts (`Decimal("1200")` is 4,
`Decimal("1.2E+3")` is 2). Numbers of type `int` or `float` cannot record trailing
zeros and raise `TypeError`.

## Values with uncertainty: `round_uncertainty`, `format_uncertainty`

These follow JCGM 100:2008, the Guide to the Expression of Uncertainty in
Measurement (GUM), clause 7.2:

- 7.2.6: the uncertainty is quoted to at most two significant digits (`figures`,
  default 2) and the estimate is rounded to the same decimal place.
- 7.2.6: it may be appropriate to round an uncertainty up rather than to the
  nearest digit; `uncertainty_rounding="up"` does that while `rounding` still
  applies to the value.
- 7.2.2 form 2: `"100.02147(35)"`, the number in parentheses is the uncertainty
  referred to the last digits of the value (`style="paren"`, the default).
- 7.2.2 form 4 and 7.2.4: `"100.02147 +/- 0.00035"` (`style="pm"`; `pm="±"`
  selects another symbol). The GUM notes that this form is easily read as a
  confidence interval, so the parenthesis form is the default.

```python
from decimal import Decimal
from figround import (
    AmbiguousFiguresError, count_sig, format_sig, format_uncertainty,
    round_decimal, round_sig, round_uncertainty, sig_bounds,
)

round_uncertainty("10.05762", "0.027")       # (Decimal('10.058'), Decimal('0.027'))
format_uncertainty(100.02147, 0.00035)       # '100.02147(35)'
format_uncertainty("123456", "1234")         # '123500(1200)'
format_uncertainty("123456", "1234", notation="sci")       # '1.235(12)e+05'
format_uncertainty(1234.56, 21, style="pm", notation="eng")  # '(1.235 +/- 0.021)e+03'
```

When the value is written without decimals the parenthesised uncertainty is in
units of one. In `sci` and `eng` notation both numbers share one exponent, taken
from whichever of the two has the larger magnitude. The uncertainty must be
positive (`UncertaintyError` otherwise).

## Errors

All value errors derive from `FigroundError`, which derives from `ValueError`, so
code written for 0.1.0 that catches `ValueError` keeps working.

| error | raised when |
| --- | --- |
| `InvalidNumberError` | invalid or nonfinite input, exponent outside the decimal range, or too many fixed-notation zeros |
| `InvalidFiguresError` | `figures` outside 1 to 10000 |
| `InvalidOptionError` | unknown `rounding`, `notation` or `style`, or `sci=True` with another notation |
| `AmbiguousFiguresError` | `count_sig(..., strict=True)` on ambiguous trailing zeros |
| `UncertaintyError` | nonpositive uncertainty or more than 100000 required value digits |

Wrong argument types raise `TypeError`. Boolean options (`strict`, `sci`, and
`trailing_point`) require actual booleans; `pm` requires a string. Unknown option
strings raise `InvalidOptionError`. Diagnostics do not echo input values, and decimal
operations leave the caller's context and flags unchanged, including on failure.

The public type aliases are `Number`, `Rounding`, `Notation` and `Style`;
`ROUNDING_MODES`, `NOTATIONS` and `STYLES` enumerate the corresponding option strings.
Only the names in `figround.__all__` and `figround.__version__` are public.

## Upgrading to 1.0.0

Install `figround` and use `from figround import ...`; the command and module runner
are `figround` and `python -m figround`. The base exception is `FigroundError`.
Numeric results, function names, signatures and defaults remain those of 0.2.1.
Wrong option types now raise `TypeError`; errors omit input values; malformed decimal
text no longer changes context flags. Modified `decimal.DefaultContext` settings do
not affect rounding. CLI usage failures use a generic diagnostic and exit 2; a closed
output pipe returns 1 quietly.

## How this differs from `format(x, ".{n}g")`

Python's `'g'` presentation type also rounds to `n` significant digits, but:

1. It removes insignificant trailing zeros (`format(1.2, ".3g")` is `"1.2"`) unless
   the `#` option is given; `format_sig` always keeps them.
2. It chooses fixed or scientific notation by magnitude (scientific when the
   exponent is below -4 for floats, -6 for Decimals, or at least `n`, so
   `format(Decimal("1200"), ".3g")` is `"1.20e+3"`); `format_sig` uses the
   notation you ask for.
3. Its exponent has no zero padding for Decimals (`1.2e-4`); `format_sig` always
   writes two digits (`1.2e-04`).
4. For a float it rounds the exact binary value; `format_sig` rounds `repr(x)`.
   The results differ only when those two decimals fall on different sides of a
   rounding boundary, such as `2.675` to three digits.
5. For a float it rounds half to even; for a `Decimal` it follows the rounding of
   the current `decimal` context. `format_sig` takes the mode as an argument and
   ignores the context.

The test suite cross-checks `round_decimal` against `Decimal.quantize` in every mode,
`format_sig(..., notation="sci")` against `format(Decimal, ".{n-1}e")`, and the value
of `format_sig` against `'g'`, on seeded random inputs.

## Command line

Installing the package adds a `figround` command (also `python -m figround`):

```
figround round 2.675 3                     # 2.68
figround round 123456 4 --notation eng     # 123.5e+03
figround count 0.00120 1200 1200.          # 3, 2 and 4, one per line
figround count 1200 --bounds               # 2 4
figround format 100.02147 -u 0.00035       # 100.02147(35)
figround format 100.02147 -u 0.00035 --style pm   # 100.02147 +/- 0.00035
figround format 1234.5 --figures 3 --notation sci # 1.23e+03
```

A negative number may need `--` before it when it could be read as an option.
`format` without `--uncertainty` formats the value alone and rejects the
uncertainty-only options (`--style`, `--pm`, `--uncertainty-rounding`). `count`
prints nothing when any of its numbers is invalid.
Invalid input prints `figround: error: ...` to standard error and exits with
status 1; invalid usage exits with status 2. Each command has `--help` with
examples.

## Sources

- NIST SP 811 (2008), Appendix B.7.1 "Rounding numbers":
  https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf
- JCGM 100:2008 (GUM), clauses 7.2.2, 7.2.4, 7.2.6 and example H.1:
  https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf
- General Decimal Arithmetic specification and `rounding.decTest`:
  https://speleotrove.com/decimal/
- Python format specification mini-language:
  https://docs.python.org/3/library/string.html#format-specification-mini-language
- ISO 80000-1 Annex B is not openly published; its tie-to-even rule is the one
  NIST SP 811 states. IEEE 754 is cited through the decimal arithmetic
  specification.
