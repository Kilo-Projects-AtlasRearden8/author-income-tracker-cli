"""Data models for the author income tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Book:
    id: str
    title: str
    created_at: str


@dataclass
class Royalty:
    id: str
    book_id: str
    platform: str
    amount: str  # stored as string to preserve decimal precision
    date: str


@dataclass
class Advance:
    id: str
    book_id: str
    amount: str
    date: str


@dataclass
class Expense:
    id: str
    book_id: str
    category: str
    amount: str
    date: str
    description: str = ""


@dataclass
class Ledger:
    books: list[Book] = field(default_factory=list)
    royalties: list[Royalty] = field(default_factory=list)
    advances: list[Advance] = field(default_factory=list)
    expenses: list[Expense] = field(default_factory=list)

    def book_by_title(self, title: str) -> Optional[Book]:
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None
