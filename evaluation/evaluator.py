"""Compatibility entry point for running the labelled live evaluator."""

import sys

from server_measure import main


if __name__ == "__main__":
    raise SystemExit(main(["--suite", "quality", *sys.argv[1:]]))
