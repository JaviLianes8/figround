# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-03

### Changed

- Rename the distribution, import package and CLI from `sigfigs` to `figround`; rename the base exception from `SigFigsError` to `FigroundError`.
- Stabilize seven numeric functions, six exception classes, four type aliases and
  three option tuples; numeric results, signatures and defaults are unchanged.
- Invalid inputs and options no longer appear in error messages. Extremely wide
  invalid figure counts raise `InvalidFiguresError` without integer conversion errors.
- Parsing malformed decimal text leaves the caller's decimal context flags unchanged.
  Rounding is isolated from modified `decimal.DefaultContext` traps and clamp settings.
- Wrong option types raise `TypeError`, including nonboolean `strict`, `sci` and
  `trailing_point` values and nonstring `pm` values.
- CLI usage errors omit supplied arguments and direct callers to `--help` (exit 2).
  Closed output pipes return exit 1 without a traceback.
- Publish Python 3.10 to 3.14 classifiers and Production/Stable metadata; include
  runnable API examples, contract tests, reference vectors and wheel validation.

## [0.2.1] - 2026-10-13

### Changed

- The `rounding.decTest` excerpt is no longer committed or shipped in the sdist:
  `scripts/fetch_upstream.py` fetches the General Decimal Arithmetic test archive,
  checked against `tests/upstream/MANIFEST.json`, and a hand-written table covers every
  rounding mode when it is absent.

## [0.2.0]

- Add `rounding=` to `round_sig` and `format_sig` with eight modes (`half_even`
  default, `half_up`, `half_down`, `up`, `down`, `ceiling`, `floor`, `05up`).
- Add `round_decimal`, returning an exact `Decimal` whose exponent records the
  significant figures.
- Add `count_sig` and `sig_bounds` to count the significant figures of a written
  number, with ambiguous trailing zeros reported or rejected (`strict=True`).
- Add `notation=` (`fixed`, `sci`, `eng`) and `trailing_point=` to `format_sig`.
- Add `round_uncertainty` and `format_uncertainty` for values with a standard
  uncertainty, in the `1.234(5)` and `1.234 +/- 0.005` forms of JCGM 100:2008.
- Add typed errors under `FigroundError`; all remain `ValueError` subclasses.
- Add the `figround` command (`round`, `count`, `format`) and `python -m figround`.
- Read floats through `repr` (unchanged results; `str` and `repr` agree for floats).
- Add `GUIDE.md`.

## [0.1.0]

- Add `round_sig` to round a number to a given count of significant figures.
- Add `format_sig` to format significant figures as a string, keeping trailing
  zeros, with optional scientific notation.
