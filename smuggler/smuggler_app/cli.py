from __future__ import annotations

import click
from rich.console import Console
from rich.text import Text
from rich.table import Table

from .banner import SMUGGLER_BANNER
from .tester import catalog, run_test

console = Console()


def _banner() -> None:
    console.print(f"[bold cyan]{SMUGGLER_BANNER}[/bold cyan]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD token smuggling tester."""


@main.command("payloads")
def payloads_cmd() -> None:
    for name, values in catalog().items():
        table = Table(title=f"Payloads: {name}")
        table.add_column("Payload")
        for payload in values:
            table.add_row(Text(payload))
        console.print(table)


@main.command("test")
@click.argument("url")
@click.option("--type", "kind", type=click.Choice(["special", "unicode", "boundary"]))
def test_cmd(url: str, kind: str | None) -> None:
    table = Table(title=f"Smuggler: {url}")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Payload")
    for item in run_test(url, kind=kind):
        table.add_row(item["type"], str(item["status_code"]), Text(item["payload"][:80]))
    console.print(table)


if __name__ == "__main__":
    main()
