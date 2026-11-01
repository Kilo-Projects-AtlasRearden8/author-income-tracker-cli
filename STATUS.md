# STATUS

## What was built

A local-first Python CLI for authors to log royalties, advances, and expenses across books and platforms, with per-book statements and CSV export. Built for Dylan Asdale / Asdale Dynamics, LLC (Indiana, formed Oct 2026).

Project: `author-income-tracker-cli` (Python 3.9+, no dependencies outside the standard library; pytest for tests).

Commands:
- `add-book <title>` — register a book
- `add-royalty <book> <platform> <amount> [--date]` — log a royalty payment by platform
- `add-advance <book> <amount> [--date]` — log an advance payment
- `add-expense <book> <category> <amount> [--date] [--description]` — log a book-related expense
- `statement <book>` — per-book statement: advances, royalties by platform, expenses, net income, profit, royalties minus advances, earned-out status
- `export-csv <book|--all> --output <file>` — CSV export for one book or all books
- `list-books` — list registered books

Modules:
- `author_income_tracker/models.py` — dataclasses (Book, Royalty, Advance, Expense, Ledger)
- `author_income_tracker/math.py` — decimal-based money math (no float drift), USD formatting
- `author_income_tracker/storage.py` — local JSON ledger (default `author_income.json`, overridable via `--data` or `AUTHOR_INCOME_DATA`); no network, no keys
- `author_income_tracker/cli.py` — argparse CLI
- `author_income_tracker/__main__.py` — `python -m author_income_tracker` support

Tests: `tests/test_math.py` (money math, totals, platform splits, net income, earned out, profit, formatting), `tests/test_storage.py` (JSON round trip, unknown-book error).

Packaging: `pyproject.toml` with console script entry point `author-income-tracker`.

License: MIT, `Copyright (c) 2026 Asdale Dynamics, LLC`. README credits Asdale Dynamics, LLC. No `.github/workflows`. No secrets, API keys, or personal data in any file.

## How to run

```bash
pip install -e .            # installs the author-income-tracker command
# (on this sandboxed env needed: pip install -e . --break-system-packages)

author-income-tracker add-book "The Massive AI Manual"
author-income-tracker add-royalty "The Massive AI Manual" kdp 1500.00 --date 2026-10-01
author-income-tracker add-royalty "The Massive AI Manual" d2d 1000.00 --date 2026-10-15
author-income-tracker add-advance "The Massive AI Manual" 1000.00 --date 2026-09-01
author-income-tracker add-expense "The Massive AI Manual" "Cover design" 200.00 --description "Freelance cover"
author-income-tracker statement "The Massive AI Manual"
author-income-tracker export-csv "The Massive AI Manual" --output royalties.csv
author-income-tracker list-books

# Or without installing:
PYTHONPATH=. python3 -m author_income_tracker statement "The Massive AI Manual"
```

Data is stored in `author_income.json` in the current directory (or `$AUTHOR_INCOME_DATA`).

## Verification results

- `pytest`: 12 passed (10 math tests, 2 storage tests)
- CLI smoke test: add-book, add-royalty x2, add-advance, add-expense x2, statement, export-csv (single book + all books), list-books all executed successfully; statement output matched expected figures ($2,500 royalties, $275 expenses, $2,225 net, $1,225 profit, earned out: Yes)
- Package installs via `pip install -e .` with console script on PATH

## Known gaps

- No edit/delete commands for ledger entries (correct a mistake by editing the JSON file directly or deleting and re-entering)
- No file locking; single-writer local use only
- No GUI or web interface (intentionally local-first CLI)
- Invalid `--date` values surface as a generic error from argparse/type conversion
- Installed location on this environment: `~/.local/bin` (may be outside PATH depending on shell)
