"""CLI entrypoint for Dinesh AI Fund."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from hedge_fund.branding import FOUNDER_CREDIT, PRODUCT_NAME
from hedge_fund.demo_data import DEMO_UNIVERSE
from hedge_fund.graph import run_analysis

console = Console()

SECTION_ORDER = [
    "1. Market Scout",
    "2. Technical Analyst",
    "3. Fundamental Analyst",
    "4. News Analyst",
    "5. Quant Analyst",
    "6. Risk Manager",
    "7. Portfolio Manager",
]


def _print_report(result: dict) -> None:
    ticker = result.get("ticker") or "?"
    demo = result.get("demo")
    mode = "DEMO (mock data, no LLM)" if demo else "LIVE"
    console.print()
    console.print(
        Panel.fit(
            f"[bold]{PRODUCT_NAME}[/bold] — Analysis Report\n[dim]{FOUNDER_CREDIT}[/dim]\n"
            f"Ticker: [cyan]{ticker}[/cyan]  |  Mode: [yellow]{mode}[/yellow]",
            border_style="green",
        )
    )

    sections = result.get("report_sections") or {}
    for key in SECTION_ORDER:
        body = sections.get(key)
        if not body and key == "7. Portfolio Manager":
            # Risk rejected — still print a short note
            if result.get("trade_rejected"):
                body = (
                    "Portfolio Manager skipped — trade REJECTED by Risk Manager.\n"
                    f"Reason: {result.get('rejection_reason') or 'n/a'}"
                )
                # Ensure section appears for done-criteria
                sections[key] = body
        if body:
            console.print(Rule(f"[bold]{key}[/bold]"))
            console.print(body)
            console.print()

    # Always surface final memo if present
    memo = result.get("investment_memo")
    if memo and "7. Portfolio Manager" not in sections:
        console.print(Rule("[bold]7. Portfolio Manager[/bold]"))
        console.print(memo)
        console.print()

    if result.get("trade_rejected") and not result.get("investment_memo"):
        console.print(
            Panel(
                f"[red]TRADE REJECTED[/red]\n{result.get('rejection_reason')}",
                title="Final Decision",
                border_style="red",
            )
        )


def cmd_analyze(args: argparse.Namespace) -> int:
    ticker = args.ticker.upper()
    console.print(f"[dim]Running 7-agent pipeline for {ticker}...[/dim]")
    try:
        result = run_analysis(
            ticker,
            demo=args.demo,
            portfolio_value=args.portfolio_value,
        )
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Pipeline failed:[/red] {exc}")
        return 1
    _print_report(result)
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    console.print("[dim]Scanning demo universe via Market Scout + full pipeline on top name...[/dim]")
    universe = DEMO_UNIVERSE
    try:
        # Run scout ranking first via analysis of top name after a light scan
        from hedge_fund.tools.market_data import rank_opportunities

        ranked = rank_opportunities(universe, demo=args.demo)
        console.print(Rule("[bold]Universe Scan[/bold]"))
        for o in ranked:
            console.print(
                f"  #{o['rank']:>2} {o['ticker']:<6} score={o['opportunity_score']:<7} "
                f"chg={o['change_pct']}% mom5d={o['momentum_5d']}%"
            )
        top = ranked[0]["ticker"]
        console.print(f"\n[dim]Deep-diving top opportunity: {top}[/dim]\n")
        result = run_analysis(
            top,
            demo=args.demo,
            portfolio_value=args.portfolio_value,
            tickers=universe,
        )
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Scan failed:[/red] {exc}")
        return 1
    _print_report(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hedge_fund",
        description="Dinesh AI Fund — 7-agent paper-research assistant (not live trading)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Run full 7-agent analysis on a ticker")
    analyze.add_argument("ticker", help="Ticker symbol, e.g. TSLA")
    analyze.add_argument(
        "--demo",
        action="store_true",
        help="Use canned data + rule-based agents (no API key required)",
    )
    analyze.add_argument(
        "--portfolio-value",
        type=float,
        default=None,
        help="Portfolio NAV for position sizing (default from env or 100000)",
    )
    analyze.set_defaults(func=cmd_analyze)

    scan = sub.add_parser("scan", help="Scan a universe and deep-dive the top name")
    scan.add_argument(
        "--demo",
        action="store_true",
        help="Use canned data + rule-based agents (no API key required)",
    )
    scan.add_argument("--portfolio-value", type=float, default=None)
    scan.set_defaults(func=cmd_scan)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    code = args.func(args)
    sys.exit(code)


if __name__ == "__main__":
    main()
