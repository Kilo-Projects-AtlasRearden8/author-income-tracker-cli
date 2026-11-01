"""Money math for the author income tracker.

All calculations use :class:`decimal.Decimal` so cents never drift the way
binary floating point can. Amounts are rounded to two decimal places.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

TWO_PLACES = Decimal("0.01")


def money(value) -> Decimal:
    """Coerce *value* into a :class:`Decimal` rounded to cents."""
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def total_royalties(amounts) -> Decimal:
    return sum((money(a) for a in amounts), Decimal("0"))


def royalties_by_platform(entries) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for entry in entries:
        platform = entry.get("platform", "unknown")
        totals[platform] = totals.get(platform, Decimal("0")) + money(entry["amount"])
    return totals


def total_advances(amounts) -> Decimal:
    return sum((money(a) for a in amounts), Decimal("0"))


def total_expenses(amounts) -> Decimal:
    return sum((money(a) for a in amounts), Decimal("0"))


def net_income(royalties_total: Decimal, expenses_total: Decimal) -> Decimal:
    return money(royalties_total - expenses_total)


def royalty_minus_advance(royalties_total: Decimal, advances_total: Decimal) -> Decimal:
    return money(royalties_total - advances_total)


def profit(royalties_total: Decimal, expenses_total: Decimal, advances_total: Decimal) -> Decimal:
    return money(royalties_total - expenses_total - advances_total)


def earned_out(royalties_total: Decimal, advances_total: Decimal) -> bool:
    return royalties_total >= advances_total


def format_usd(amount) -> str:
    value = money(amount)
    if value < 0:
        return f"-${abs(value):,.2f}"
    return f"${value:,.2f}"
