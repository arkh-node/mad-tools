from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from .banner import GHOSTWRITE_BANNER
from .memory import TEMPLATES, check, inject

console = Console()


def _banner() -> None:
    console.print(f"[bold white]{GHOSTWRITE_BANNER}[/bold white]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD memory poison tester."""


@main.command("templates")
def templates_cmd() -> None:
    for item in TEMPLATES:
        console.print(item)


@main.command("inject")
@click.argument("url")
@click.option("--payload", required=True)
def inject_cmd(url: str, payload: str) -> None:
    result = inject(url, payload)
    console.print(f"status={result['status_code']} payload={result['payload']}")


@main.command("check")
@click.argument("url")
def check_cmd(url: str) -> None:
    result = check(url)
    table = Table(title="ghostwrite check")
    table.add_column("Status")
    table.add_column("Memory hit")
    table.add_column("Preview")
    table.add_row(str(result["status_code"]), str(result["memory_hit"]), result["preview"])
    console.print(table)


if __name__ == "__main__":
    main()
