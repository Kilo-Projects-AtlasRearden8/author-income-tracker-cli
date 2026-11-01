import json
import os
import tempfile

from author_income_tracker.math import money
from author_income_tracker.storage import (
    add_advance,
    add_book,
    add_expense,
    add_royalty,
    load,
    save,
)


def _tmp_path():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def test_round_trip():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        add_royalty(ledger, "Test Book", "kdp", "100.00", "2026-10-01", path=path)
        add_advance(ledger, "Test Book", "500.00", "2026-09-01", path=path)
        add_expense(ledger, "Test Book", "Ads", "25.00", "2026-10-02", "Facebook ads", path=path)

        reloaded = load(path)
        assert len(reloaded.books) == 1
        assert reloaded.books[0].title == "Test Book"
        assert len(reloaded.royalties) == 1
        assert len(reloaded.advances) == 1
        assert len(reloaded.expenses) == 1
        assert money(reloaded.royalties[0].amount) == money("100.00")

        raw = json.load(open(path))
        assert raw["books"][0]["title"] == "Test Book"
    finally:
        os.unlink(path)


def test_unknown_book_raises():
    path = _tmp_path()
    try:
        ledger = load(path)
        try:
            add_royalty(ledger, "No Such Book", "kdp", "10.00", path=path)
        except ValueError as exc:
            assert "No Such Book" in str(exc)
        else:
            raise AssertionError("expected ValueError")
    finally:
        os.unlink(path)
