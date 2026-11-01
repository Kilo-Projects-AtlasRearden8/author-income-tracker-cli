"""JSON on-disk storage for the ledger (local-first, no keys, no network)."""

from __future__ import annotations

import json
import os
import uuid
from datetime import date, datetime
from json import JSONDecodeError

from .models import Advance, Book, Expense, Ledger, Royalty

DEFAULT_PATH = "author_income.json"


def _default_path() -> str:
    return os.environ.get("AUTHOR_INCOME_DATA", DEFAULT_PATH)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _today() -> str:
    return date.today().isoformat()


def _load_raw(path: str) -> dict:
    if not os.path.exists(path):
        return {"books": [], "royalties": [], "advances": [], "expenses": []}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (JSONDecodeError, OSError):
        return {"books": [], "royalties": [], "advances": [], "expenses": []}
    data.setdefault("books", [])
    data.setdefault("royalties", [])
    data.setdefault("advances", [])
    data.setdefault("expenses", [])
    return data


def _save_raw(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load(path: str | None = None) -> Ledger:
    """Load the ledger from *path* (or the default location)."""
    path = path or _default_path()
    data = _load_raw(path)
    return Ledger(
        books=[Book(**item) for item in data["books"]],
        royalties=[Royalty(**item) for item in data["royalties"]],
        advances=[Advance(**item) for item in data["advances"]],
        expenses=[Expense(**item) for item in data["expenses"]],
    )


def save(ledger: Ledger, path: str | None = None) -> None:
    """Persist *ledger* to *path* (or the default location)."""
    path = path or _default_path()
    data = {
        "books": [vars(book) for book in ledger.books],
        "royalties": [vars(r) for r in ledger.royalties],
        "advances": [vars(a) for a in ledger.advances],
        "expenses": [vars(e) for e in ledger.expenses],
    }
    _save_raw(path, data)


def add_book(ledger: Ledger, title: str, path: str | None = None) -> Book:
    path = path or _default_path()
    if ledger.book_by_title(title) is not None:
        raise ValueError(f"Book already exists: {title}")
    book = Book(id=str(uuid.uuid4()), title=title, created_at=_today())
    ledger.books.append(book)
    save(ledger, path)
    return book


def _require_book(ledger: Ledger, title: str) -> Book:
    book = ledger.book_by_title(title)
    if book is None:
        titles = ", ".join(b.title for b in ledger.books) or "(none)"
        raise ValueError(f"Unknown book: {title}. Known books: {titles}")
    return book


def add_royalty(ledger: Ledger, book_title: str, platform: str, amount, date_str: str | None = None, path: str | None = None) -> Royalty:
    path = path or _default_path()
    book = _require_book(ledger, book_title)
    entry = Royalty(
        id=str(uuid.uuid4()),
        book_id=book.id,
        platform=platform,
        amount=str(amount),
        date=date_str or _today(),
    )
    ledger.royalties.append(entry)
    save(ledger, path)
    return entry


def add_advance(ledger: Ledger, book_title: str, amount, date_str: str | None = None, path: str | None = None) -> Advance:
    path = path or _default_path()
    book = _require_book(ledger, book_title)
    entry = Advance(
        id=str(uuid.uuid4()),
        book_id=book.id,
        amount=str(amount),
        date=date_str or _today(),
    )
    ledger.advances.append(entry)
    save(ledger, path)
    return entry


def add_expense(
    ledger: Ledger,
    book_title: str,
    category: str,
    amount,
    date_str: str | None = None,
    description: str = "",
    path: str | None = None,
) -> Expense:
    path = path or _default_path()
    book = _require_book(ledger, book_title)
    entry = Expense(
        id=str(uuid.uuid4()),
        book_id=book.id,
        category=category,
        amount=str(amount),
        date=date_str or _today(),
        description=description,
    )
    ledger.expenses.append(entry)
    save(ledger, path)
    return entry


def validate_date(date_str: str) -> str:
    datetime.strptime(date_str, "%Y-%m-%d")  # raises ValueError if bad
    return date_str
