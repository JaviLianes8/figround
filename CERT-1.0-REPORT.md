# figround 1.0.0 certification report

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
- [x] Open release PR #4; guard CLEAN
- [x] Independent review and five QA lenses
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

## Preparation checks before QA

Before changes: 198 passed, two optional archive tests skipped; format, lint and
`mypy --strict src tests` passed. The final source suite contains 249 tests including
live archive tests, executable README/GUIDE blocks, attribute docstrings and module
doctests, plus three artifact checks.

## QA lenses, round 1

Reviewed head: `671e7cb0d24e9d86356117ce7e84a4e2f82313b1`.
Fix commit: `ea3a57aff56f2c53dffdfbae4213d33d1d0f02ae`
(`fix certification regressions and strengthen contracts`).
Date: 2026-11-03. All 21 reported findings are accepted and addressed.
All five initial lens verdicts were FAIL; independent confirmation of these fixes
remains pending. The fixes do not constitute new PASS verdicts for the lenses.

| Findings | Change and verification |
| --- | --- |
| A001, D-01 | README and packaged metadata link to the existing `JaviLianes8/sigfigs` repository. Source, Issues, GUIDE, CHANGELOG and LICENSE URLs all returned HTTP 200; rebuilt wheel metadata is asserted. |
| A002, B-R1-001, C-06, E-63 | Separate working carry precision from the 100000-digit result limit. Tests accept 99999 and 100000 coefficient digits, reject 100001, and distinguish rounding down at the boundary from a carry beyond it. |
| A003 | Restore `SigFigsError`, `sigfigs` and `python -m sigfigs` in the 0.2.0 history. The rename remains documented in 1.0.0. |
| A004 | Handle Windows EINVAL and broken output pipes during writes and flushes, replacing stdout before shutdown. Real subprocess tests pass for the module and installed executable; unrelated output errors still propagate. |
| A005 | Add an attribute docstring and runnable example for `__version__`; include it in the attribute-documentation contract. |
| B-R1-002, C-05 | Estimate zero's precision independently of its stored exponent and uncertainty scale. Signed and scaled zeros produce the same positive result; tiny uncertainty formats compactly in scientific notation. |
| C-01 | Reject integer inputs above 65536 bits before Decimal conversion with `InvalidNumberError`; document decimal text and Decimal alternatives. Test both signs, the inclusive limit and overridden subclass bit lengths. Repeat the size-scaling probe with construction excluded. |
| C-02 | Use the base float representation in an isolated decimal context. Subclass tests verify the numeric result and unchanged caller flags and traps under both InvalidOperation trap settings. |
| C-03 | Use a constant notation-conflict message. A custom representation containing 1.4 million characters never appears in the bounded diagnostic. |
| C-04 | Normalize figure-count subclasses to their stored base integer before validation and all arithmetic. Tests cover invalid counts, overridden comparisons, conversion and subtraction, and valid subclass counts. |
| D-02 | Include `scripts/check.ps1` in the sdist. Assert its archive membership and execute the documented command from the extracted archive. |
| E-10 | Assert float underflow signs and positive exact zero. |
| E-25 | Assert Decimal zero counts for positive, zero and negative exponents through both counting functions and strict mode. |
| E-37 | Assert acceptance at both 99999 and 100000 digits and rejection above the public limit. |
| E-39 | Assert separate value and uncertainty modes using 2.41 and 0.11, producing 2.4 and 0.2. |
| E-40 | Inspect Decimal zero signs after rounding negative values and negative zero. |

### Regression evidence

Before implementation changes, the added source contracts recorded 23 failures and
23 passes, including the missing version documentation. The old sdist failed the
script-membership assertion, and its installed CLI reproduced exit 120 and stderr.
After the fixes, all 46 focused source checks pass. Expectations are hand-written
contracts; the inclusive precision test also compares independent Decimal quantization.

Each surviving mutation was reapplied separately to a scratch copy. All five now
fail assertions. M39's replacement was adjusted only to account for the new carry
headroom in the context-construction expression.

| Mutation | Contract that catches it |
| --- | --- |
| M10 | `test_float_underflow_preserves_sign` |
| M25 | `test_decimal_zero_count_uses_only_decimal_places` |
| M37 | `test_uncertainty_accepts_inclusive_digit_limit` |
| M39 | `test_uncertainty_rounding_does_not_override_value_rounding` |
| M40 | `test_uncertainty_result_zero_is_positive` |

The integer probe excluded input construction and used three timing windows per
size. Inputs with 32000, 128000 and 512000 decimal digits were rejected in median
2.99, 3.51 and 3.17 microseconds respectively. The first two sizes had previously
required 0.0992 and 1.7524 seconds. The committed size-limit contract protects the
bounded conversion policy without relying on machine-dependent test timing.

### Validation

On local CPython 3.14.6, each required gate exits 0: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, and pytest. The additional strict source/test
type check passes for 35 files. The full suite passes **295 tests, no skips**,
including reference data, doctests, the rebuilt wheel consumer and both CLI entry
points. Per-test timeout is 300 seconds, with all temporary paths under the dedicated
scratch directory. All source and test files remain at most 200 lines.

Built the sdist and its wheel with `python -m build --no-isolation`; both pass
`twine check --strict`. The extracted sdist's `scripts/check.ps1` also passes format,
lint, strict source/test typing and all 295 tests. The pre-QA artifact identities
below are superseded for this round by the artifacts under `fix-r1/dist`.

Evidence is retained under
`the build machine scratch folder sigfigs-cert/fix-r1/`:
`red-corrected.log`, `red.log` (old-artifact failures), `full.log`, `full.xml`,
`sdist-check.log`, `mutation-results.json`, each mutation's `result.log`,
`timings.json`, `links.json` and `dist/`.
This fix round ran only CPython 3.14.6; the earlier preparation matrix below is
historical evidence, not a rerun of the corrected code on those interpreters.

### Disputed findings

None.

## QA lenses, round 2

Reviewed head: `907311825ebd69ae24cd8c893b7b624b80a0bfec`.
Fix commit: `b33008903399896b3ccfe09c677b647b1a145848`
(`read numeric and notation subclasses from stored text`).
Date: 2026-11-03. Both reported findings are accepted and addressed.
Independent confirmation by the adversarial lens remains pending; rerunning its
checks here does not constitute a new independent PASS verdict.

| Finding | Change and verification |
| --- | --- |
| C-07 | Use `str.strip(x)` for numeric string inputs. Subclasses cannot substitute oversized integers or raise through overridden stripping/conversion methods. Contracts cover 32000- and 128000-digit substitutions, whitespace, malformed text, NaN, and unchanged caller flags/traps. |
| C-08 | Normalize notation to its stored base string before validation and retain that normalized value through conflict checks and rendering in both formatting functions. Contracts cover overridden equality, inequality and string conversion, all three valid notations, scientific compatibility, and bounded typed errors for conflicts and unknown names. |

### Regression evidence and validation

All 14 new hand-written cases in `tests/test_string_subclasses.py` failed on the
reviewed code before implementation changes, then passed after the fixes.
Public signatures and accepted input types remain unchanged; the CHANGELOG records
the stored-string behaviour for numeric inputs and notation options.

Copied the reviewer's six original regression tests and 40 probe cases into this
round's scratch directory and ran them against the corrected source: **46 passed**.
The 32000- and 128000-digit integer-substitution probes both return `Decimal('1.25')`.
Their median conversion times, excluding integer construction, are 9.40 and 9.60
microseconds (1.02x for 4x the unused integer size). Contracts assert stored-value
semantics without machine-dependent timing thresholds.

On local CPython 3.14.6, all four required gates exit 0: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, and pytest. The additional
`mypy --strict src tests` check passes for 36 files. The final suite passes
**309 tests, no skips**, including reference vectors, doctests, rebuilt artifact
checks, an installed-wheel consumer and both CLI entry points. The rebuilt wheel
and sdist pass `twine check --strict`. All Python source/test files remain at most
200 lines. Every pytest invocation uses a 300-second timeout and scratch basetemp.
The earlier interpreter matrix is historical evidence, not a rerun for this round.

Evidence: `the build machine scratch folder sigfigs-cert/fix-r2/`, containing
`red.log`, `green.log`, `full.log`, `full.xml`, `build.log`, `dist/`,
`reviewer.log`, `reviewer.xml`, and `reviewer/sweep.json` with timing results.

### Disputed findings

None.

## QA lenses, round 3

Reviewed head: `fc67c43474d29fdb6bd4f0f98d8582b480b10741`.
Fix commit: `9a5d899ccacb56648d0f3bf02eed09c3d6b9e122`
(`dispatch inputs and options by real type without instance hooks`).
Date: 2026-11-03. The reported finding is accepted and addressed at its root.
Independent confirmation by the adversarial lens remains pending; rerunning its
checks here does not constitute a new independent PASS verdict.

| Finding | Change and verification |
| --- | --- |
| C-09 | `isinstance` falls back to an instance's `__class__` attribute, so a subclass overriding `__getattribute__` ran code before normalization. Every public entry point now dispatches on `type()` and `issubclass` of the real type and reads values through base-class methods. |

Paths audited and closed in the same way:

1. Numeric inputs of `round_decimal`, `round_sig`, `format_sig`, `round_uncertainty`
   and `format_uncertainty`: str, int, float and Decimal subclasses are converted to
   their stored base value (`str.strip`, `int.__int__`, `float.__repr__`, `Decimal()`)
   before any method call, so later `is_finite`, `is_zero`, comparisons and
   quantization only see exact `Decimal` values.
2. Figure counts in both rounding families: real-type check, then `int.__int__`.
3. `rounding` and `uncertainty_rounding`: stored text before the dictionary lookup,
   so overridden `__hash__` and `__eq__` never run.
4. `notation`: the same real-type helper (already normalized in round 2).
5. `style`: stored text before membership and dispatch comparisons.
6. `pm`: stored text before f-string rendering, so `__format__` never runs.
7. `sci`, `trailing_point` and `strict`: `type(value) is bool`, so an object
   claiming `bool` through `__class__` cannot reach `__bool__`.
8. `sig_bounds` and `count_sig`: real-type dispatch, `str.strip` on stored text and
   a base `Decimal` copy before inspection.
9. CLI `main(argv)`: str subclass arguments are passed to argparse as stored text.

Objects that only claim an accepted type through `__class__` now raise `TypeError`
with the documented messages; the CHANGELOG records both behaviour changes.

### Regression evidence and validation

`tests/test_attribute_hooks.py` adds 30 hand-written cases using subclasses whose
attribute access and 28 overridable special methods record each call and raise.
Each asserts the stored-value result and an empty call record, or a typed error.
On the reviewed code 29 failed; the notation case passed, being already closed.
All 30 pass after the fix, including the reviewer's minimal C-09 reproduction.

On local CPython 3.14.6, all four required gates exit 0: `ruff format --check .`,
`ruff check .`, `mypy --strict src`, and pytest (also `mypy --strict src tests`).
The suite passes 336 tests; the 3 skipped are the built-artifact e2e cases, not
rerun because packaging is unchanged since round 2. All Python source/test files
remain at most 200 lines. Every pytest invocation uses a 300-second timeout and
scratch basetemp. The earlier interpreter matrix is historical evidence.

Evidence: `D:/pylib-scratch/sigfigs-cert/fix-r3/`, containing `red.log` and `full.log`.

### Disputed findings

None.

## Certification result

| Lens | Rounds | Final verdict | Report | Commit |
| --- | --- | --- | --- | --- |
| a, API and docs | 2 | PASS | lens-a-r2/REPORT.md | 9073118 |
| b, correctness and ground truth | 2 | PASS | lens-b-r2/REPORT.md | 9073118 |
| c, adversarial and robustness | 4 | PASS | lens-c-r4/REPORT.md | d742d05 |
| d, packaging and e2e | 2 | PASS | lens-d-r2/REPORT.md | 9073118 |
| e, contract strength | 2 | PASS | lens-e-r2/REPORT.md | 9073118 |

Independent reviewer, round 1 at d742d05: every item PASS except item 16, whose single
finding (two evidence paths in this report named a build folder instead of describing it)
was fixed in the report text. The re-check confirmed the fix and re-ran the four gates on
a fresh clone. Reviewer evidence: decTest archive re-fetched (size, sha256, Last-Modified
and ETag match the manifest), NIST SP 811 and JCGM 100:2008 examples found verbatim,
the installed wheel suite on CPython 3.10, 3.11, 3.12, 3.13 and 3.14 (exit 0), two extra
mutations of its own caught, `twine check --strict` passed, no prior PyPI release.

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

## Preparation gates before QA (item 15)

All four commands exited 0 independently: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `python -m pytest`. The additional `mypy --strict src tests`
check passed for 30 files. The final pytest run passed 252 tests with no skips,
including the built-wheel consumer and both artifact inspections. Final pytest checks
use `pytest-timeout` with 300 seconds per test and dedicated scratch basetemps.
The live archive and both artifact paths were supplied through `FIGROUND_UPSTREAM_DIR`,
`FIGROUND_WHEEL` and `FIGROUND_SDIST`. `twine check --strict` passed for both artifacts.
All 13 package source files stay below 200 lines.

## Certification scorecard

| Item | Result | Evidence |
| --- | --- | --- |
| 1 | PASS | Twenty exports, stable names/signatures/defaults; all changes in CHANGELOG |
| 2 | PASS | Exact `__all__`, no unlisted public attributes, public imports in docs |
| 3 | PASS | Function/class doctests, eight alias/constant/version attribute docstrings, executable README/GUIDE blocks |
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
| 15 | PASS | Four gates exit 0; round-2 fixed suite 309 passed |
| 16 | PASS | Independent reviewer round 1, item 16 finding fixed and re-checked |
| 17 | PASS | PR #4 from `release/1.0.0` to `main`, guard CLEAN; merged by the orchestrator |
| 18 | PASS | 24 preparation mutations caught; five round-1 survivors now caught by added contracts |
| 19 | PASS | Five lenses PASS (table under Certification result) |
