# figround 1.0.0 preparation report

Date: 2026-11-03. Baseline: 0.2.1, main `9ab199be31037f1863621a5461d7a8ecfe149e37`.

Progress:
- [x] Check release state and create `release/1.0.0`
- [x] Check PyPI and select the new distribution, package and command name
- [x] Review API, typing, errors and runnable documentation
- [x] Re-fetch reference data and verify published examples
- [x] Add contract, integer-oracle and parser fuzz tests
- [x] Update README, GUIDE, CHANGELOG and release metadata
- [ ] Build, inspect and exercise wheel and sdist
- [ ] Run every available supported interpreter
- [ ] Complete mutation round and final gates
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
`mypy --strict src tests` passed. Current contract run: 242 passed, including live
archive tests, executable README/GUIDE blocks and module doctests.

## Remaining certification stages

Items 16 and 19 have not been evaluated for this release. Earlier improvement-round
reviews do not certify 1.0.0. Item 17 merge and publication remain pending.
