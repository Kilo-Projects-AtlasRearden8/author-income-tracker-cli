# Author Income Tracker

A local-first command line tool for authors to log royalties, advances, and expenses across books and platforms, with per-book statements and CSV export.

Built by **Dylan Asdale** for **Asdale Dynamics, LLC** — Indiana, formed October 2026 — as part of the LLC's small-business and author tooling for KDP book publishing, marketing, and bookkeeping. No API keys, no accounts, no network: your data stays in a JSON file on your machine.

## What it does

- `add-book` — register a book (e.g. *The Massive AI Manual*)
- `add-royalty` — log royalty payments by platform (Amazon KDP, Draft2Digital, etc.)
- `add-advance` — log advance payments
- `add-expense` — log book-related expenses by category
- `statement` — print a per-book statement: advances, royalties by platform, expenses, net income, profit, earned-out status
- `export-csv` — export ledger rows to CSV for one book or all books

All math uses Python's `decimal` module so cents never drift. Data lives in a local JSON file (`author_income.json` by default, or `$AUTHOR_INCOME_DATA`).

## Install

```bash
pip install -e .
```

## Quick start

```bash
# Register a book
author-income-tracker add-book "The Massive AI Manual"

# Log royalties from two platforms
author-income-tracker add-royalty "The Massive AI Manual" kdp 1500.00 --date 2026-10-01
author-income-tracker add-royalty "The Massive AI Manual" d2d 1000.00 --date 2026-10-15

# Log an advance and expenses
author-income-tracker add-advance "The Massive AI Manual" 1000.00 --date 2026-09-01
author-income-tracker add-expense "The Massive AI Manual" "Cover design" 200.00 --description "Freelance cover"
author-income-tracker add-expense "The Massive AI Manual" Ads 75.00

# Per-book statement
author-income-tracker statement "The Massive AI Manual"

# CSV export
author-income-tracker export-csv "The Massive AI Manual" --output royalties.csv
author-income-tracker export-csv --all --output all-books.csv

# List books
author-income-tracker list-books
```

Example statement output:

```
Statement for: The Massive AI Manual
Created:       2026-11-01

Advances:
  2026-09-01  $1,000.00
  Total advances: $1,000.00

Royalties (gross):
  d2d            $1,000.00
  kdp            $1,500.00
  Total royalties: $2,500.00

Expenses:
  2026-10-01  Cover design     $200.00  (Freelance cover)
  2026-10-15  Ads               $75.00
  Total expenses: $275.00

Net income (royalties - expenses): $2,225.00
Profit (royalties - expenses - advances): $1,225.00
Royalties minus advances: $1,500.00
Earned out: Yes
```

## Running tests

```bash
pip install -e ".[test]"
pytest
```

## Privacy and data

This tool is local-first: nothing is sent over the network, and no keys or credentials are required or stored. Your ledger is a plain JSON file you control. Back it up like any other file.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

Credits: Built by Dylan Asdale, founder of Asdale Dynamics, LLC — beginner-friendly AI education, books, guides, and practical tools (dylanasdale.github.io).
