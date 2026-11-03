"""The ``figround`` command: round, count and format numbers from the shell."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import cast

from ._cli_output import write_lines
from ._cli_text import COUNT_EPILOG, FORMAT_EPILOG, MAIN_EPILOG, ROUND_EPILOG
from ._count import count_sig, sig_bounds
from ._errors import FigroundError
from ._format import format_sig
from ._modes import NOTATIONS, ROUNDING_MODES, Rounding
from ._parser import Parser
from ._uncertainty import STYLES, format_uncertainty


def _add_rounding(parser: argparse.ArgumentParser, flag: str = "--rounding") -> None:
    parser.add_argument(
        flag,
        choices=ROUNDING_MODES,
        default=None,
        metavar="MODE",
        help=f"rounding mode: {', '.join(ROUNDING_MODES)} (default half_even)",
    )


def _add_notation(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--notation",
        choices=NOTATIONS,
        default="fixed",
        help="fixed, sci (scientific) or eng (engineering); default fixed",
    )


def _parser() -> argparse.ArgumentParser:
    raw = argparse.RawDescriptionHelpFormatter
    parser = Parser(
        prog="figround",
        description="Round, count and format significant figures with exact decimal math.",
        epilog=MAIN_EPILOG,
        formatter_class=raw,
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    rnd = commands.add_parser(
        "round",
        help="round a number to N significant figures",
        description="Round NUMBER to FIGURES significant figures and "
        "print it, keeping significant trailing zeros.",
        epilog=ROUND_EPILOG,
        formatter_class=raw,
    )
    rnd.add_argument("number", help="the number, as decimal text (1.5, -2e-3)")
    rnd.add_argument("figures", type=int, help="significant figures to keep (at least 1)")
    _add_rounding(rnd)
    _add_notation(rnd)
    rnd.add_argument(
        "--trailing-point",
        action="store_true",
        help='write "1000." when every zero of a whole number is significant',
    )

    cnt = commands.add_parser(
        "count",
        help="count the significant figures of numbers",
        description="Print the significant figures of each NUMBER, one per line.",
        epilog=COUNT_EPILOG,
        formatter_class=raw,
    )
    cnt.add_argument("numbers", nargs="+", metavar="NUMBER", help="numbers as written")
    mode = cnt.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict",
        action="store_true",
        help="fail on ambiguous trailing zeros instead of not counting them",
    )
    mode.add_argument(
        "--bounds",
        action="store_true",
        help="print the fewest and the most figures, space separated",
    )

    fmt = commands.add_parser(
        "format",
        help="format a value with its uncertainty",
        description="Format VALUE with its uncertainty per JCGM 100:2008 "
        "clause 7.2, or alone to --figures significant figures.",
        epilog=FORMAT_EPILOG,
        formatter_class=raw,
    )
    fmt.add_argument("value", help="the measured value")
    fmt.add_argument("-u", "--uncertainty", help="standard uncertainty (positive)")
    fmt.add_argument(
        "--figures",
        type=int,
        default=None,
        help="significant figures of the uncertainty (default 2), or of the "
        "value when no uncertainty is given (then required)",
    )
    fmt.add_argument(
        "--style",
        choices=STYLES,
        default=None,
        help='paren (default) writes "1.234(5)", pm writes "1.234 +/- 0.005"',
    )
    fmt.add_argument(
        "--pm",
        default=None,
        metavar="SYMBOL",
        help='plus-minus symbol for --style pm (default "+/-")',
    )
    _add_rounding(fmt)
    _add_rounding(fmt, "--uncertainty-rounding")
    _add_notation(fmt)
    return parser


def _rounding(name: str | None) -> Rounding:
    return cast(Rounding, name or "half_even")


def _round(args: argparse.Namespace) -> list[str]:
    return [
        format_sig(
            args.number,
            args.figures,
            notation=args.notation,
            rounding=_rounding(args.rounding),
            trailing_point=args.trailing_point,
        )
    ]


def _count(args: argparse.Namespace) -> list[str]:
    if args.bounds:
        return [" ".join(str(n) for n in sig_bounds(text)) for text in args.numbers]
    return [str(count_sig(text, strict=args.strict)) for text in args.numbers]


def _format(args: argparse.Namespace, parser: argparse.ArgumentParser) -> list[str]:
    rounding = _rounding(args.rounding)
    if args.uncertainty is None:
        if args.figures is None:
            parser.error("format needs --uncertainty or --figures")
        given = (args.style, args.pm, args.uncertainty_rounding)
        if any(option is not None for option in given):
            parser.error("--style, --pm and --uncertainty-rounding need --uncertainty")
        return [format_sig(args.value, args.figures, notation=args.notation, rounding=rounding)]
    figures = 2 if args.figures is None else args.figures
    text = format_uncertainty(
        args.value,
        args.uncertainty,
        figures,
        style=args.style or "paren",
        notation=args.notation,
        rounding=rounding,
        uncertainty_rounding=args.uncertainty_rounding,
        pm="+/-" if args.pm is None else args.pm,
    )
    return [text]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line; return the exit status (0 ok, 1 bad input, 2 bad usage)."""
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "round":
            lines = _round(args)
        elif args.command == "count":
            lines = _count(args)
        else:
            lines = _format(args, parser)
    except (FigroundError, ArithmeticError) as error:
        print(f"figround: error: {error}", file=sys.stderr)
        return 1
    return write_lines(lines)
