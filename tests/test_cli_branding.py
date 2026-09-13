"""CLI branding smoke test."""

from hedge_fund.branding import FOUNDER_CREDIT, PRODUCT_NAME
from hedge_fund.cli import _print_report
from hedge_fund.graph import run_analysis


def test_cli_report_uses_product_and_founder(capsys):
    result = run_analysis("TSLA", demo=True, portfolio_value=100_000)
    _print_report(result)
    out = capsys.readouterr().out
    assert PRODUCT_NAME in out
    assert FOUNDER_CREDIT in out
    assert "AI Hedge Fund" not in out
