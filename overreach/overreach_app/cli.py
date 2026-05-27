from __future__ import annotations

import asyncio

import click
from rich.console import Console
from rich.table import Table

from .analyzer import scan_url, write_report
from .banner import OVERREACH_BANNER

console = Console()


def _banner() -> None:
    console.print(f"[bold yellow]{OVERREACH_BANNER}[/bold yellow]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD excessive-agency analyzer."""


@main.command("scan")
@click.argument("url")
def scan_cmd(url: str) -> None:
    data = asyncio.run(scan_url(url))
    table = Table(title=f"Overreach: {url}")
    table.add_column("Tool")
    table.add_column("Risk")
    table.add_column("Notes")
    for item in data["tools"]:
        table.add_row(item["name"], str(item["score"]), item["notes"])
    console.print(table)
    console.print(f"Total risk score: {data['total_risk']}")


@main.command("check")
@click.argument("url")
@click.option("--tool", required=True)
def check_cmd(url: str, tool: str) -> None:
    data = asyncio.run(scan_url(url))
    for item in data["tools"]:
        if item["name"] == tool:
            console.print(item)
            return
    console.print(f"tool not found: {tool}")


@main.command("report")
@click.argument("url")
def report_cmd(url: str) -> None:
    path = write_report(asyncio.run(scan_url(url)))
    console.print(f"[green]Report[/green] {path}")


if __name__ == "__main__":
    main()
