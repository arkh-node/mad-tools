from __future__ import annotations

import json

import click
from rich.console import Console
from rich.table import Table

from .banner import NEEDLER_BANNER
from .fuzzer import fuzz_url, payloads

console = Console()


def _banner() -> None:
    console.print(f"[bold magenta]{NEEDLER_BANNER}[/bold magenta]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD MCP tool fuzzer."""


@main.command("payloads")
def payloads_cmd() -> None:
    for name, values in payloads().items():
        table = Table(title=f"Payloads: {name}")
        table.add_column("Payload")
        for item in values:
            table.add_row(json.dumps(item, ensure_ascii=False))
        console.print(table)


@main.command("fuzz")
@click.argument("url")
@click.option("--tool")
@click.option("--strategy", default="chaos", type=click.Choice(["chaos", "boundary", "type-confusion"]), show_default=True)
def fuzz_cmd(url: str, tool: str | None, strategy: str) -> None:
    table = Table(title=f"Needler: {url}")
    table.add_column("Verdict")
    table.add_column("Status")
    table.add_column("Payload")
    for item in fuzz_url(url, tool=tool, strategy=strategy):
        table.add_row(item["verdict"], str(item["status_code"]), json.dumps(item["payload"], ensure_ascii=False)[:80])
    console.print(table)


if __name__ == "__main__":
    main()
