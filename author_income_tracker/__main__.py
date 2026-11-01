"""Allow ``python -m author_income_tracker``."""

import sys

from .cli import main

sys.exit(main())
