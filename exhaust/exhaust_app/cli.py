from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from .banner import EXHAUST_BANNER
from .bench import PAYLOADS, benchmark, run_test

console = Console()


def _banner() -> None:
    console.print(f"[bold magenta]{EXHAUST_BANNER}[/bold magenta]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD performance fuzz utility."""


@main.command("test")
@click.argument("url")
@click.option("--type", "kind", type=click.Choice(list(PAYLOADS)))
def test_cmd(url: str, kind: str | None) -> None:
    table = Table(title=f"exhaust test: {url}")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Latency ms")
    for item in run_test(url, kind=kind):
        table.add_row(item["type"], str(item["status_code"]), str(item["latency_ms"]))
    console.print(table)


@main.command("benchmark")
@click.argument("url")
@click.option("--count", default=10, show_default=True, type=int)
def benchmark_cmd(url: str, count: int) -> None:
    result = benchmark(url, count)
    console.print(
        f"count={result['count']} avg_ms={result['avg_ms']} min_ms={result['min_ms']} max_ms={result['max_ms']} statuses={result['statuses']}"
    )


if __name__ == "__main__":
    main()
