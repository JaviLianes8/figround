"""Help text for the ``figround`` command: runnable examples for each subcommand."""

MAIN_EPILOG = """examples:
  figround round 2.675 3                    -> 2.68
  figround round 123456 2 --notation sci    -> 1.2e+05
  figround count 0.00120 1200 1200.         -> 3, 2, 4 (one per line)
  figround format 100.02147 -u 0.00035      -> 100.02147(35)

Run "figround COMMAND --help" for the options of each command."""

ROUND_EPILOG = """examples:
  figround round 1.2 3                          -> 1.20
  figround round 2.5 1 --rounding half_up       -> 3
  figround round 123456 4 --notation eng        -> 123.5e+03
  figround round 1000 4 --trailing-point        -> 1000.
  figround round -- -0.0125 2                   -> -0.012"""

COUNT_EPILOG = """examples:
  figround count 0.0450            -> 3
  figround count 6.022e23          -> 4
  figround count 1200 --bounds     -> 2 4
  figround count 1200 --strict     -> error, exit status 1

Leading zeros never count; with a decimal point trailing zeros count; without one,
trailing zeros of a whole number are ambiguous (counted as not significant).
If any NUMBER is invalid nothing is printed and the exit status is 1."""

FORMAT_EPILOG = """examples:
  figround format 100.02147 -u 0.00035                -> 100.02147(35)
  figround format 100.02147 -u 0.00035 --style pm     -> 100.02147 +/- 0.00035
  figround format 10.05762 -u 0.027                   -> 10.058(27)
  figround format 1 -u 10.47 --uncertainty-rounding up  -> 1(11)
  figround format 1234.5 --figures 3 --notation sci   -> 1.23e+03

The uncertainty is rounded to --figures significant figures (default 2, JCGM 100:2008
clause 7.2.6) and the value to the same decimal place."""
