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
    remove_advance,
    remove_book,
    remove_expense,
    remove_royalty,
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


def test_amount_validation_rejects_negative():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        try:
            add_royalty(ledger, "Test Book", "kdp", "-50.00", path=path)
        except ValueError as exc:
            assert "negative" in str(exc).lower()
        else:
            raise AssertionError("expected ValueError for negative amount")
    finally:
        os.unlink(path)


def test_amount_validation_rejects_invalid():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        try:
            add_royalty(ledger, "Test Book", "kdp", "not-a-number", path=path)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for invalid amount")
    finally:
        os.unlink(path)


def test_remove_book_removes_all_entries():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Gone Book", path=path)
        add_royalty(ledger, "Gone Book", "kdp", "100.00", "2026-10-01", path=path)
        add_advance(ledger, "Gone Book", "500.00", "2026-09-01", path=path)
        add_expense(ledger, "Gone Book", "Ads", "25.00", "2026-10-02", path=path)

        # Add another book to make sure it survives
        add_book(ledger, "Kept Book", path=path)
        add_royalty(ledger, "Kept Book", "d2d", "75.00", "2026-10-03", path=path)

        remove_book(ledger, "Gone Book", path=path)

        reloaded = load(path)
        assert len(reloaded.books) == 1
        assert reloaded.books[0].title == "Kept Book"
        assert len(reloaded.royalties) == 1
        assert reloaded.royalties[0].platform == "d2d"
        assert len(reloaded.advances) == 0
        assert len(reloaded.expenses) == 0
    finally:
        os.unlink(path)


def test_remove_book_unknown_raises():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        try:
            remove_book(ledger, "No Such Book", path=path)
        except ValueError as exc:
            assert "No Such Book" in str(exc)
        else:
            raise AssertionError("expected ValueError")
    finally:
        os.unlink(path)


def test_remove_royalty_matches_and_removes():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        add_royalty(ledger, "Test Book", "kdp", "100.00", "2026-10-01", path=path)
        add_royalty(ledger, "Test Book", "kdp", "200.00", "2026-10-02", path=path)

        removed = remove_royalty(ledger, "Test Book", "kdp", "100.00", "2026-10-01", path=path)
        assert removed == 1

        reloaded = load(path)
        assert len(reloaded.royalties) == 1
        assert reloaded.royalties[0].amount == "200.00"
    finally:
        os.unlink(path)


def test_remove_royalty_no_match_returns_zero():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        add_royalty(ledger, "Test Book", "kdp", "100.00", "2026-10-01", path=path)

        removed = remove_royalty(ledger, "Test Book", "d2d", "999.00", "2026-10-01", path=path)
        assert removed == 0
    finally:
        os.unlink(path)


def test_remove_advance_matches_and_removes():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        add_advance(ledger, "Test Book", "500.00", "2026-09-01", path=path)
        add_advance(ledger, "Test Book", "500.00", "2026-09-01", path=path)

        removed = remove_advance(ledger, "Test Book", "500.00", "2026-09-01", path=path)
        assert removed == 2

        reloaded = load(path)
        assert len(reloaded.advances) == 0
    finally:
        os.unlink(path)


def test_remove_expense_matches_and_removes():
    path = _tmp_path()
    try:
        ledger = load(path)
        add_book(ledger, "Test Book", path=path)
        add_expense(ledger, "Test Book", "Ads", "25.00", "2026-10-02", "Facebook ads", path=path)

        removed = remove_expense(ledger, "Test Book", "Ads", "25.00", "2026-10-02", path=path)
        assert removed == 1

        reloaded = load(path)
        assert len(reloaded.expenses) == 0
    finally:
        os.unlink(path)
