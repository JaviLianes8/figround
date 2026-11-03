# Improvement round: figround 0.2.0

Progress:
- [x] 1. Brainstorm ranked improvements (this file)
- [x] 2. Implement on `improve/figround-round` (additive API, minor bump to 0.2.0)
- [x] 3. CLI (`figround round|count|format`, `[project.scripts]`)
- [x] 4. Gates: `ruff format --check .`, `ruff check .`, `mypy --strict src`, `pytest`
- [x] 5. Contracts from cited sources, seeded oracle cross-check, real wheel e2e
- [x] 6. Pull request opened
- [x] 7. Independent review, fixes, re-gate, trace guard clean

## Sources (fetched 2026-10-12)

- NIST SP 811 (2008 edition), Appendix B.7.1 "Rounding numbers":
  https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf
- JCGM 100:2008 (GUM), clauses 7.2.2, 7.2.4, 7.2.6 and example H.1:
  https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf
- General Decimal Arithmetic specification 1.70 (rounding algorithms; round-half-even is
  the IEEE 754 section 4.3.3 default): https://speleotrove.com/decimal/decarith.pdf
- General Decimal Arithmetic testcases, `rounding.decTest` version 2.62:
  https://speleotrove.com/decimal/dectest.zip
- Python format specification mini-language, `'g'` rules:
  https://docs.python.org/3/library/string.html#format-specification-mini-language
- ISO 80000-1:2009 Annex B is not openly published (the ISO online browsing platform
  answered 403). Its rule A (ties to even) is the rule NIST SP 811 B.7.1 states, citing
  ISO 31-0, the predecessor of ISO 80000-1; no vector here is claimed to come from ISO.
- IEEE 754 itself is paywalled; its tie-to-even default is cited through the decimal
  arithmetic specification above.

## Ranked improvements

1. **All rounding modes.** `round_sig`, `format_sig` and a new `round_decimal` take
   `rounding=` with the eight decimal modes (`half_even` default, `half_up`, `half_down`,
   `up`, `down`, `ceiling`, `floor`, `05up`). Golden vectors: `rounding.decTest`.
2. **Exact Decimal result.** `round_decimal` returns a `Decimal` whose exponent records
   the significant figures (`Decimal("1.20")`, `Decimal("1.2E+3")`), so callers never
   go through a binary float.
3. **Count significant figures** of a numeric string: `count_sig` and `sig_bounds`.
   Leading zeros never count; a decimal point makes trailing zeros significant
   (`"1200."` is 4); without one they are ambiguous (`"1200"` is 2 to 4) and
   `count_sig(..., strict=True)` raises `AmbiguousFiguresError`; scientific notation
   counts the mantissa only.
4. **Notations.** `format_sig(..., notation="fixed" | "sci" | "eng")`, engineering
   exponents in multiples of three, significant trailing zeros kept in every notation;
   `trailing_point=True` writes `"1000."` when every zero is significant.
5. **Value with uncertainty per the GUM.** `round_uncertainty` and `format_uncertainty`:
   uncertainty to `figures` (default 2) significant digits, value rounded to the same
   decimal place, `"100.02147(35)"` (GUM 7.2.2 form 2) or `"100.02147 +/- 0.00035"`
   (form 4), fixed, scientific or engineering with a shared exponent; separate
   rounding mode for the uncertainty since GUM 7.2.6 allows rounding up.
6. **Typed errors.** `FigroundError(ValueError)` with `InvalidNumberError`,
   `InvalidFiguresError`, `InvalidOptionError`, `AmbiguousFiguresError`,
   `UncertaintyError`; all still `ValueError`, so 0.1.0 callers keep working.
7. **CLI.** `figround round`, `figround count`, `figround format` (with `--uncertainty`),
   runnable examples in `--help`, errors to stderr with exit status 1.
8. **Docs.** Docstrings with examples on every public name, `GUIDE.md` covering float
   input via `repr`, the zero convention, and where `format(x, ".{n}g")` differs.
9. **Contracts and e2e.** Golden tests from the sources above, seeded cross-check against
   `decimal` quantize and `format(Decimal, ".{n-1}e")`, wheel built and driven from a
   throwaway virtual environment.
