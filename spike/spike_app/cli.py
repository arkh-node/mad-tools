"""CLI for spike."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .banner import SPIKE_BANNER
from .payloads import add_custom_payloads
from .tester import payload_catalog, run_test

console = Console()


def _banner() -> None:
    console.print(f"[bold red]{SPIKE_BANNER}[/bold red]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD prompt injection battery."""


@main.command("payloads")
@click.option("--type", "payload_type")
def payloads_cmd(payload_type: str | None) -> None:
    data = payload_catalog(payload_type)
    for kind, values in data.items():
        table = Table(title=f"Payloads: {kind}")
        table.add_column("Payload")
        for payload in values:
            table.add_row(payload)
        console.print(table)


@main.command("add-payload")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def add_payload_cmd(file: Path) -> None:
    count = add_custom_payloads(str(file))
    console.print(f"[green]Added[/green] {count} payloads")


@main.command("test")
@click.argument("url")
@click.option("--type", "payload_type")
@click.option("--all", "run_all", is_flag=True)
@click.option("--format", "fmt", default="custom", type=click.Choice(["openai", "custom", "get"]), show_default=True)
@click.option("--body")
@click.option("--key")
def test_cmd(url: str, payload_type: str | None, run_all: bool, fmt: str, body: str | None, key: str | None) -> None:
    results = run_test(url, test_type=payload_type, run_all=run_all, fmt=fmt, body=body, key=key)
    table = Table(title=f"Spike Results: {url}")
    table.add_column("Type")
    table.add_column("Score")
    table.add_column("Status")
    table.add_column("Payload")
    for item in results:
        table.add_row(item["type"], item["score"], str(item["status_code"]), item["payload"][:80])
    console.print(table)


if __name__ == "__main__":
    main()
