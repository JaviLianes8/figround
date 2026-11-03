"""Golden vectors copied from the cited sources, rechecked against live sources on 2026-11-03.

Every case names its source. The GUM writes a decimal comma and groups digits with
spaces (``100,021 47``); those numbers are transcribed with a decimal point and no
spaces, and quantities quoted in two units (g and mg) are expressed in one unit.
"""

from decimal import Decimal

import pytest

from figround import format_sig, format_uncertainty, round_decimal, round_uncertainty

# NIST SP 811 (2008), Appendix B.7.1 "Rounding numbers", rules 1 to 3 and their examples.
# https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf
NIST_B71 = [
    ("6.9749515", 3, "6.97"),  # rule 1
    ("6.9749515", 2, "7.0"),  # rule 2
    ("6.9749515", 5, "6.9750"),  # rule 2
    ("6.9749515", 7, "6.974952"),  # rule 3, odd digit increased
    ("6.9749505", 7, "6.974950"),  # rule 3, even digit unchanged
]


@pytest.mark.parametrize(("value", "figures", "expected"), NIST_B71)
def test_nist_sp811_b71_rounding_examples(value: str, figures: int, expected: str) -> None:
    assert format_sig(value, figures) == expected
    assert round_decimal(value, figures) == Decimal(expected)


def test_nist_sp811_b72_conversion_example() -> None:
    # B.7.2: 36 ft x 0.3048 m/ft = 10.9728 m, rounded to three significant digits: 11.0 m.
    assert format_sig(Decimal(36) * Decimal("0.3048"), 3) == "11.0"


# JCGM 100:2008 (GUM), clause 7.2 and example H.1.
# https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf


def test_gum_722_form_2_parenthesis() -> None:
    # "mS = 100,021 47(35) g" with uc = 0,35 mg = 0.00035 g.
    assert format_uncertainty("100.02147", "0.00035") == "100.02147(35)"


def test_gum_722_form_4_plus_minus() -> None:
    # "mS = (100,021 47 +/- 0,000 35) g"
    assert format_uncertainty("100.02147", "0.00035", style="pm") == "100.02147 +/- 0.00035"


def test_gum_724_expanded_uncertainty() -> None:
    # "mS = (100,021 47 +/- 0,000 79) g"
    assert format_uncertainty("100.02147", "0.00079", style="pm") == "100.02147 +/- 0.00079"


def test_gum_726_round_up_example() -> None:
    # "uc(y) = 10,47 m(ohm) might be rounded up to 11 m(ohm)"
    _, spread = round_uncertainty("0", "10.47", uncertainty_rounding="up")
    assert spread == Decimal("11")
    assert str(spread) == "11"


def test_gum_726_round_down_example() -> None:
    # "u(xi) = 28,05 kHz should be rounded down to 28 kHz"
    _, spread = round_uncertainty("0", "28.05")
    assert str(spread) == "28"


def test_gum_726_estimate_consistent_with_uncertainty() -> None:
    # "if y = 10,057 62 ohm with uc(y) = 27 m(ohm), y should be rounded to 10,058 ohm"
    value, spread = round_uncertainty("10.05762", "0.027")
    assert (str(value), str(spread)) == ("10.058", "0.027")


def test_gum_h15_end_gauge_result() -> None:
    # H.1.5 states "l = 50,000 838 mm with ... uc = 32 nm" (form 1 of 7.2.2). The
    # parenthesis rendering asserted here is derived from it by form 2; the GUM does not
    # print this string. 32 nm = 0.000032 mm.
    assert format_uncertainty("50.000838", "0.000032") == "50.000838(32)"


def test_gum_h16_expanded_result() -> None:
    # H.1.6: "l = (50,000 838 +/- 0,000 093) mm"
    text = format_uncertainty("50.000838", "0.000093", style="pm")
    assert text == "50.000838 +/- 0.000093"
