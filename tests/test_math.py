from author_income_tracker.math import (
    earned_out,
    format_usd,
    money,
    net_income,
    profit,
    royalty_minus_advance,
    royalties_by_platform,
    total_advances,
    total_expenses,
    total_royalties,
)


def test_money_rounds_to_cents():
    assert money("10.005") == money("10.01")
    assert money("10.004") == money("10.00")
    assert money(10) == money("10.00")


def test_total_royalties_sums():
    assert total_royalties(["10.00", "20.00", "30.00"]) == money("60.00")
    assert total_royalties([]) == money("0.00")


def test_total_advances_sums():
    assert total_advances(["500.00", "500.00"]) == money("1000.00")
    assert total_advances([]) == money("0.00")


def test_total_expenses_sums():
    assert total_expenses(["25.50", "75.25"]) == money("100.75")
    assert total_expenses([]) == money("0.00")


def test_royalties_by_platform():
    entries = [
        {"platform": "kdp", "amount": "100.00"},
        {"platform": "d2d", "amount": "50.00"},
        {"platform": "kdp", "amount": "200.00"},
    ]
    totals = royalties_by_platform(entries)
    assert totals == {"kdp": money("300.00"), "d2d": money("50.00")}


def test_net_income():
    assert net_income(money("1000.00"), money("300.00")) == money("700.00")
    assert net_income(money("100.00"), money("150.00")) == money("-50.00")


def test_earned_out():
    assert earned_out(money("1000.00"), money("1000.00")) is True
    assert earned_out(money("999.99"), money("1000.00")) is False
    assert earned_out(money("0.00"), money("0.00")) is True


def test_royalty_minus_advance():
    assert royalty_minus_advance(money("1500.00"), money("1000.00")) == money("500.00")
    assert royalty_minus_advance(money("500.00"), money("1000.00")) == money("-500.00")


def test_profit():
    assert profit(money("1000.00"), money("200.00"), money("500.00")) == money("300.00")


def test_format_usd():
    assert format_usd("1234.5") == "$1,234.50"
    assert format_usd("-50.25") == "-$50.25"
