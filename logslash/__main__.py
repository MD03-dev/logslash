"""Cho phép chạy: python -m logslash"""

import sys
from logslash.cli import main

if __name__ == "__main__":
    sys.exit(main())
