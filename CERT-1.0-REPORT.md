# figround 1.0.0 preparation report

Date: 2026-11-03. Baseline: 0.2.1, main `9ab199be31037f1863621a5461d7a8ecfe149e37`.

Progress:
- [x] Check release state and create `release/1.0.0`
- [x] Check PyPI and select the new distribution, package and command name
- [x] Review API, typing, errors and runnable documentation
- [x] Re-fetch reference data and verify published examples
- [x] Add contract, integer-oracle and parser fuzz tests
- [x] Update README, GUIDE, CHANGELOG and release metadata
- [x] Build, inspect and exercise wheel and sdist
- [x] Run every available supported interpreter
- [x] Complete mutation round
- [x] Final gates
- [ ] Open release PR
- [ ] Independent review and five QA lenses
- [ ] Merge and publish

## API and behaviour

The stable surface has seven numeric functions, six exception classes, four type aliases
and three option tuples. `__all__` and signatures are pinned in tests. The base exception
is now `FigroundError`. Numeric results, function names, signatures and defaults remain
those of 0.2.1. Wrong option types raise `TypeError`; invalid values use the documented
exception hierarchy. Errors do not echo values. Decimal parsing and arithmetic are
isolated from caller context flags and modified `DefaultContext` traps and clamp.
CLI usage errors are generic and closed output pipes return 1 quietly.
Every behaviour change is listed in the dated CHANGELOG section.

## Name and release availability

The previous distribution's JSON endpoint returned HTTP 404 on 2026-11-03, so there is
no public release to install for an upgrade test. The new endpoint
https://pypi.org/pypi/figround/json also returned 404. All 21 single separator insertions
(`-`, `_`, `.` at each boundary), plus `f1ground`, `figr0und` and `f1gr0und`, returned 404.
The live https://pypi.org/simple/ index contains no name matching after removing
separators, lowercasing and mapping `l`/`1`/`I` and `o`/`0` together.
Availability is a point-in-time observation, not a reservation or upload guarantee.

## Ground truth

- https://speleotrove.com/decimal/dectest.zip fetched on 2026-11-03, 791733 bytes,
  SHA-256 `b70a224cd52e82b7a8150aedac5efa2d0cb3941696fd829bdbe674f9f65c3926`.
  The manifest pins version 2.62 of `rounding.decTest`. All 482 applicable add vectors
  cover eight modes. Signed-zero blocks are excluded because positive zero is the
  documented convention. The archive is external and never shipped.
- [NIST SP 811 (2008)](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf),
  Appendix B.7.1 and B.7.2, fetched on 2026-11-03. Five rounding examples and one
  conversion example are checked in `test_sources.py`.
- [JCGM 100:2008](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf),
  clauses 7.2.2, 7.2.4, 7.2.6 and H.1, fetched on 2026-11-03. Examples use decimal
  points and common units. The H.1.5 parenthesis form is explicitly labelled derived.
- Python `Decimal.quantize` and numeric formatting run in this session provide
  independent standard-library comparisons. The oracle does not import private
  rounding code. A separate integer-division oracle checks 24000 cases over all modes.
- Random inputs are generated from recorded seeds, not represented as external vectors.
  Parser fuzz exercises 5000 ASCII/Unicode strings; long inputs reach 100000 characters.

Set `FIGROUND_UPSTREAM_DIR` before `python scripts/fetch_upstream.py` to choose the
reference archive directory. Without the archive, its two tests skip cleanly.

## Baseline and current checks

Before changes: 198 passed, two optional archive tests skipped; format, lint and
`mypy --strict src tests` passed. The final source suite contains 249 tests including live archive tests, executable
README/GUIDE blocks, attribute docstrings and module doctests, plus three artifact checks.

## Remaining certification stages

Items 16 and 19 have not been evaluated for this release. Earlier improvement-round
reviews do not certify 1.0.0. Item 17 merge and publication remain pending.

## Mutation round (item 18)

Each change was applied alone to a scratch copy, with bytecode disabled, and the full
contract suite was run with stop-on-first-failure and 300-second timeouts. All 24 bugs
were caught by assertions, not collection or setup errors. Three initial runs had a
missing scratch parent directory; those results were discarded and the cases rerun.
The restored source passed 249 tests (three optional artifact checks skipped).

| ID | Deliberate bug | Caught by |
| --- | --- | --- |
| M01 | half-even ties become half-up | `test_cli.py::test_commands` |
| M02 | maximum figure count rejected | `test_errors.py::test_figures_have_an_upper_bound` |
| M03 | floats read as binary values | `test_format.py::test_rounds_before_formatting` |
| M04 | zero loses a decimal place | `test_api.py::test_documentation_python_blocks` |
| M05 | rounding quantum off by one | `test_api.py::test_documentation_python_blocks` |
| M06 | float result has inverted sign | `test_api.py::test_documentation_python_blocks` |
| M07 | strict counting ignores ambiguity | `test_cli.py::test_bad_input_exits_1_with_message` |
| M08 | written zero loses one significant digit | `test_count.py::test_sig_bounds` |
| M09 | integer placeholder zeros always count | `test_api.py::test_documentation_python_blocks` |
| M10 | negative formatting loses sign | `test_cli.py::test_commands` |
| M11 | negative exponents get a plus sign | `test_api.py::test_documentation_python_blocks` |
| M12 | fixed zero limit becomes exclusive | `test_errors.py::test_fixed_limit_is_inclusive_and_sci_still_works` |
| M13 | trailing decimal point suppressed | `test_api.py::test_documentation_python_blocks` |
| M14 | engineering exponent not a multiple of three | `test_api.py::test_documentation_python_blocks` |
| M15 | zero uncertainty accepted | `test_cli.py::test_bad_input_exits_1_with_message` |
| M16 | uncertainty rounding option ignored | `test_cli.py::test_commands` |
| M17 | value rounding option ignored | `test_uncertainty.py::test_rounding_modes_apply_separately` |
| M18 | wrong rounding type uses value error | `test_safety.py::test_wrong_option_types_raise_type_error` |
| M19 | malformed text modifies caller flags | `test_safety.py::test_caller_context_and_flags_survive_success_and_failure` |
| M20 | CLI count order reversed | `test_cli.py::test_commands` |
| M21 | CLI usage echoes untrusted arguments | `test_cli.py::test_usage_errors_do_not_echo_arguments` |
| M22 | unlisted public name leaks | `test_api.py::test_no_unlisted_public_names` |
| M23 | positive zero retains negative sign | `test_notation.py::test_round_decimal_records_figures_in_the_exponent` |
| M24 | boolean option validation dropped | `test_safety.py::test_wrong_option_types_raise_type_error` |

## Packaging and external use (items 8, 10, 13, 14)

`python -m build --no-isolation` built the sdist and then the wheel from that sdist.
`twine check --strict` passed for both. The wheel contains only the package, type marker,
metadata, entry point and license. The sdist contains source, tests, the reference
manifest and fetch script, README, GUIDE, CHANGELOG, build metadata, LICENSE and
Hatchling's `.gitignore`. No downloaded reference content, scratch output, caches or
certification notes are shipped.

`test_e2e.py` installs the wheel without dependencies in a fresh venv. An isolated
external consumer exercises all seven functions and checks the installed import path.
Both the console entry point and `python -m figround` are tested by subprocess for
rounding, counting, uncertainty, negative inputs, help and failures. Usage and data
errors have distinct exit codes and do not echo supplied values. A separate external
consumer passes `mypy --strict` against the installed wheel's `py.typed` package.
There is no live prior PyPI release, so an actual PyPI upgrade cannot be run.

For the interpreter matrix, tests and docs were extracted from the sdist into a folder
without `src`. Each interpreter used a fresh venv with the wheel installed; imports
were verified to come from that venv. The package's module doctests ran separately.
Both CLI entry points ran on every interpreter.

| Python | Installed contract tests | Module doctests | CLI |
| --- | --- | --- | --- |
| 3.10.22 | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |
| 3.11.18 | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |
| 3.12.16 | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |
| 3.13.18 | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |
| 3.14.6 | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |
| 3.14.10 | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |
| 3.14.10t | 235 passed, 3 optional artifact checks skipped | 14 passed | PASS |

The three skipped checks build no additional venvs during the matrix: they are run
explicitly with `FIGROUND_WHEEL` and `FIGROUND_SDIST` in the final source gate.
No supported minor version from 3.10 through 3.14 was unavailable. The launcher's
older interpreter registrations pointed to removed directories; actual installed
interpreters were located and probed, including free-threaded 3.14.10.

Artifact identities from the inspected build:

- `figround-1.0.0-py3-none-any.whl`: SHA-256 `4330904b3b0b67c9734dedae99a9da05e3961a47bee3b08bbd44f629de271a39`.
- `figround-1.0.0.tar.gz`: SHA-256 `b41e9f9e46e053d4c68f317f5f55a3a71809ac15a613a37a4b3e0a0412c04253`.

## Final gates (item 15)

All four commands exited 0 independently: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `python -m pytest`. The additional `mypy --strict src tests`
check passed for 30 files. The final pytest run passed 252 tests with no skips,
including the built-wheel consumer and both artifact inspections. Every pytest run
used `pytest-timeout` with 300 seconds per test and a dedicated scratch basetemp.
The live archive and both artifact paths were supplied through `FIGROUND_UPSTREAM_DIR`,
`FIGROUND_WHEEL` and `FIGROUND_SDIST`. `twine check --strict` passed for both artifacts.
All 13 package source files stay below 200 lines.

## Certification scorecard

| Item | Result | Evidence |
| --- | --- | --- |
| 1 | PASS | Twenty exports, stable names/signatures/defaults; all changes in CHANGELOG |
| 2 | PASS | Exact `__all__`, no unlisted public attributes, public imports in docs |
| 3 | PASS | Function/class doctests, seven alias/constant attribute docstrings, executable README/GUIDE blocks |
| 4 | PASS | Strict source/test typing and installed external consumer; `py.typed` shipped |
| 5 | PASS | Typed failures, bounded messages, no reflected inputs, context isolation |
| 6 | PASS | Every function, type alias, option tuple and exception has contracts |
| 7 | PASS | Live NIST/GUM documents, 482 decTest vectors and independent integer/stdlib oracles |
| 8 | PASS | Fresh wheel venv, external consumer, console and module subprocesses; no prior PyPI release |
| 9 | PASS | Recorded seeds, 24000 integer-oracle cases, 5000 parser inputs, 100000-character stress cases |
| 10 | PASS | Seven installed interpreter builds, 3.10 through 3.14, including free-threaded 3.14 |
| 11 | PASS | Problem, verified alternatives, absolute links, requested badge, strict Twine checks |
| 12 | PASS | Dated 1.0.0 section, 2026-11-03 |
| 13 | PASS | Version 1.0.0, Production/Stable, Python classifiers, MIT, project URLs, no runtime dependencies |
| 14 | PASS | Inspected sdist and wheel; package, type marker and license included; external archive excluded |
| 15 | PASS | Four gates exit 0; final suite 252 passed |
| 16 | PENDING | Independent release reviewer has not evaluated this version |
| 17 | PENDING | Release PR, merge and publication |
| 18 | PASS | 24 deliberately broken variants caught; restored suite passes |
| 19 | PENDING | No release QA lens verdicts yet |
