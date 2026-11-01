"""Command line interface for the author income tracker."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Optional

from .math import (
    earned_out,
    format_usd,
    net_income,
    profit,
    royalty_minus_advance,
    royalties_by_platform,
    total_advances,
    total_expenses,
    total_royalties,
)
from .storage import (
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
    validate_date,
)


def _entries_for_book(ledger, book_id) -> tuple[list, list, list]:
    royalties = [r for r in ledger.royalties if r.book_id == book_id]
    advances = [a for a in ledger.advances if a.book_id == book_id]
    expenses = [e for e in ledger.expenses if e.book_id == book_id]
    return royalties, advances, expenses


def _print_statement(ledger, title: str) -> int:
    book = ledger.book_by_title(title)
    if book is None:
        print(f"Error: unknown book '{title}'.")
        known = ", ".join(b.title for b in ledger.books) or "(none)"
        print(f"Known books: {known}")
        return 1

    royalties, advances, expenses = _entries_for_book(ledger, book.id)
    royalties_total = total_royalties([r.amount for r in royalties])
    advances_total = total_advances([a.amount for a in advances])
    expenses_total = total_expenses([e.amount for e in expenses])
    by_platform = royalties_by_platform([{"platform": r.platform, "amount": r.amount} for r in royalties])
    net = net_income(royalties_total, expenses_total)
    pnl = profit(royalties_total, expenses_total, advances_total)
    out = royalty_minus_advance(royalties_total, advances_total)
    done = earned_out(royalties_total, advances_total)

    print(f"Statement for: {book.title}")
    print(f"Created:       {book.created_at}")
    print()
    print("Advances:")
    if advances:
        for a in advances:
            print(f"  {a.date}  {format_usd(a.amount)}")
    else:
        print("  (none)")
    print(f"  Total advances: {format_usd(advances_total)}")
    print()
    print("Royalties (gross):")
    if by_platform:
        for platform in sorted(by_platform):
            print(f"  {platform:12s} {format_usd(by_platform[platform]):>12s}")
    else:
        print("  (none)")
    print(f"  Total royalties: {format_usd(royalties_total)}")
    print()
    print("Expenses:")
    if expenses:
        for e in expenses:
            desc = f"  ({e.description})" if e.description else ""
            print(f"  {e.date}  {e.category:16s} {format_usd(e.amount):>12s}{desc}")
    else:
        print("  (none)")
    print(f"  Total expenses: {format_usd(expenses_total)}")
    print()
    print(f"Net income (royalties - expenses): {format_usd(net)}")
    print(f"Profit (royalties - expenses - advances): {format_usd(pnl)}")
    print(f"Royalties minus advances: {format_usd(out)}")
    print(f"Earned out: {'Yes' if done else 'No'}")
    if not done and advances_total > 0:
        print(f"  {format_usd(-out)} more in royalties needed to earn out.")
    return 0


def _export_csv(ledger, title: Optional[str], output: str) -> int:
    rows = []
    if title:
        book = ledger.book_by_title(title)
        if book is None:
            print(f"Error: unknown book '{title}'.")
            return 1
        for r in ledger.royalties:
            if r.book_id == book.id:
                rows.append([r.date, book.title, "royalty", r.platform, r.amount, ""])
        for a in ledger.advances:
            if a.book_id == book.id:
                rows.append([a.date, book.title, "advance", "", a.amount, ""])
        for e in ledger.expenses:
            if e.book_id == book.id:
                rows.append([e.date, book.title, "expense", e.category, e.amount, e.description])
    else:
        for r in ledger.royalties:
            book = next((b for b in ledger.books if b.id == r.book_id), None)
            rows.append([r.date, book.title if book else "(unknown)", "royalty", r.platform, r.amount, ""])
        for a in ledger.advances:
            book = next((b for b in ledger.books if b.id == a.book_id), None)
            rows.append([a.date, book.title if book else "(unknown)", "advance", "", a.amount, ""])
        for e in ledger.expenses:
            book = next((b for b in ledger.books if b.id == e.book_id), None)
            rows.append([e.date, book.title if book else "(unknown)", "expense", e.category, e.amount, e.description])

    rows.sort(key=lambda row: row[0])
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "book", "type", "platform_or_category", "amount", "description"])
        writer.writerows(rows)
    scope = f"for '{title}'" if title else "for all books"
    print(f"Exported {len(rows)} rows {scope} to {output}")
    return 0


def _list_books(args) -> int:
    ledger = load(args.data)
    if not ledger.books:
        print("No books yet. Add one with: author-income-tracker add-book \"Title\"")
        return 0
    print("Books:")
    for book in ledger.books:
        print(f"  {book.title}")
    return 0


def _cmd_add_book(args) -> int:
    try:
        book = add_book(load(args.data), args.title, path=args.data)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Added book: {book.title} ({book.created_at})")
    return 0


def _cmd_add_royalty(args) -> int:
    try:
        validate_date(args.date) if args.date else None
        entry = add_royalty(load(args.data), args.book, args.platform, args.amount, args.date, path=args.data)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Added royalty {format_usd(entry.amount)} from {entry.platform} on {entry.date}")
    return 0


def _cmd_add_advance(args) -> int:
    try:
        validate_date(args.date) if args.date else None
        entry = add_advance(load(args.data), args.book, args.amount, args.date, path=args.data)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Added advance {format_usd(entry.amount)} on {entry.date}")
    return 0


def _cmd_add_expense(args) -> int:
    try:
        validate_date(args.date) if args.date else None
        entry = add_expense(load(args.data), args.book, args.category, args.amount, args.date, args.description, path=args.data)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Added expense {format_usd(entry.amount)} for {entry.category} on {entry.date}")
    return 0


def _cmd_statement(args) -> int:
    return _print_statement(load(args.data), args.book)


def _cmd_export(args) -> int:
    title = None if args.all else args.book
    return _export_csv(load(args.data), title, args.output)


def _cmd_summary(args) -> int:
    ledger = load(args.data)
    if not ledger.books:
        print("No books yet. Add one with: author-income-tracker add-book \"Title\"")
        return 0

    print("Author income summary")
    print("=" * 40)

    grand_royalties = 0
    grand_advances = 0
    grand_expenses = 0

    for book in ledger.books:
        royalties, advances, expenses = _entries_for_book(ledger, book.id)
        royalties_total = total_royalties([r.amount for r in royalties])
        advances_total = total_advances([a.amount for a in advances])
        expenses_total = total_expenses([e.amount for e in expenses])
        pnl = profit(royalties_total, expenses_total, advances_total)
        done = earned_out(royalties_total, advances_total)

        print(f"\n{book.title}")
        print(f"  Royalties:  {format_usd(royalties_total):>12s}")
        print(f"  Advances:   {format_usd(advances_total):>12s}")
        print(f"  Expenses:   {format_usd(expenses_total):>12s}")
        print(f"  Profit:     {format_usd(pnl):>12s}")
        print(f"  Earned out: {'Yes' if done else 'No'}")

        grand_royalties += royalties_total
        grand_advances += advances_total
        grand_expenses += expenses_total

    print("\n" + "=" * 40)
    print(f"{'All books':<16s} {format_usd(grand_royalties):>12s} "
          f"{format_usd(grand_advances):>12s} {format_usd(grand_expenses):>12s} "
          f"{format_usd(profit(grand_royalties, grand_expenses, grand_advances)):>12s}")
    print()
    print("Columns: royalties  advances  expenses  profit")
    return 0


def _cmd_remove_book(args) -> int:
    try:
        book = remove_book(load(args.data), args.title, path=args.data)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Removed book: {book.title} (and all its royalties, advances, and expenses)")
    return 0


def _cmd_remove_royalty(args) -> int:
    try:
        validate_date(args.date)
        removed = remove_royalty(
            load(args.data), args.book, args.platform, args.amount, args.date, path=args.data
        )
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    if removed:
        print(f"Removed {removed} royalty entr{'y' if removed == 1 else 'ies'}.")
    else:
        print("No matching royalty found.")
    return 0


def _cmd_remove_advance(args) -> int:
    try:
        validate_date(args.date)
        removed = remove_advance(
            load(args.data), args.book, args.amount, args.date, path=args.data
        )
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    if removed:
        print(f"Removed {removed} advance entr{'y' if removed == 1 else 'ies'}.")
    else:
        print("No matching advance found.")
    return 0


def _cmd_remove_expense(args) -> int:
    try:
        validate_date(args.date)
        removed = remove_expense(
            load(args.data), args.book, args.category, args.amount, args.date, path=args.data
        )
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}")
        return 1
    if removed:
        print(f"Removed {removed} expense entr{'y' if removed == 1 else 'ies'}.")
    else:
        print("No matching expense found.")
    return 0


def _cmd_export(args) -> int:
    return _export_csv(load(args.data), args.book if args.all is False else None, args.output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="author-income-tracker",
        description="Log royalties, advances, and expenses across books and platforms. Local-first JSON storage.",
    )
    parser.add_argument("--data", default=None, help="Path to the ledger JSON file (default: author_income.json or AUTHOR_INCOME_DATA env var)")

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-book", help="Create a new book record")
    p.add_argument("title")
    p.set_defaults(func=_cmd_add_book)

    p = sub.add_parser("add-royalty", help="Log a royalty payment")
    p.add_argument("book")
    p.add_argument("platform")
    p.add_argument("amount", help="Royalty amount, e.g. 1500.00")
    p.add_argument("--date", default=None, help="Date YYYY-MM-DD (default: today)")
    p.set_defaults(func=_cmd_add_royalty)

    p = sub.add_parser("add-advance", help="Log an advance payment")
    p.add_argument("book")
    p.add_argument("amount", help="Advance amount, e.g. 1000.00")
    p.add_argument("--date", default=None, help="Date YYYY-MM-DD (default: today)")
    p.set_defaults(func=_cmd_add_advance)

    p = sub.add_parser("add-expense", help="Log a book-related expense")
    p.add_argument("book")
    p.add_argument("category", help="Expense category, e.g. 'Cover design'")
    p.add_argument("amount", help="Expense amount, e.g. 200.00")
    p.add_argument("--date", default=None, help="Date YYYY-MM-DD (default: today)")
    p.add_argument("--description", default="", help="Optional description")
    p.set_defaults(func=_cmd_add_expense)

    p = sub.add_parser("statement", help="Print a per-book income statement")
    p.add_argument("book")
    p.set_defaults(func=_cmd_statement)

    p = sub.add_parser("export-csv", help="Export ledger rows to CSV")
    group = p.add_mutually_exclusive_group()
    group.add_argument("book", nargs="?", default=None, help="Book title (omit to export all books)")
    group.add_argument("--all", action="store_true", help="Export all books (ignores positional book argument)")
    p.add_argument("--output", required=True, help="Output CSV path")
    p.set_defaults(func=_cmd_export)

    p = sub.add_parser("list-books", help="List known books")
    p.set_defaults(func=_list_books)

    p = sub.add_parser("summary", help="Show a one-line summary across all books")
    p.set_defaults(func=_cmd_summary)

    p = sub.add_parser("remove-book", help="Remove a book and all its entries")
    p.add_argument("title")
    p.set_defaults(func=_cmd_remove_book)

    p = sub.add_parser("remove-royalty", help="Remove a royalty entry by match criteria")
    p.add_argument("book")
    p.add_argument("platform")
    p.add_argument("amount", help="Royalty amount, e.g. 1500.00")
    p.add_argument("date", help="Date YYYY-MM-DD")
    p.set_defaults(func=_cmd_remove_royalty)

    p = sub.add_parser("remove-advance", help="Remove an advance entry by match criteria")
    p.add_argument("book")
    p.add_argument("amount", help="Advance amount, e.g. 1000.00")
    p.add_argument("date", help="Date YYYY-MM-DD")
    p.set_defaults(func=_cmd_remove_advance)

    p = sub.add_parser("remove-expense", help="Remove an expense entry by match criteria")
    p.add_argument("book")
    p.add_argument("category", help="Expense category, e.g. 'Cover design'")
    p.add_argument("amount", help="Expense amount, e.g. 200.00")
    p.add_argument("date", help="Date YYYY-MM-DD")
    p.set_defaults(func=_cmd_remove_expense)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
