from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from .banner import BABEL_BANNER
from .scenarios import list_scenarios, run_chain, run_scenario

console = Console()


def _banner() -> None:
    console.print(f"[bold red]{BABEL_BANNER}[/bold red]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD multi-agent confusion utility."""


@main.group("scenario")
def scenario_group() -> None:
    """Scenario helpers."""


@scenario_group.command("list")
def scenario_list_cmd() -> None:
    for item in list_scenarios():
        console.print(item)


@scenario_group.command("run")
@click.argument("name", type=click.Choice(list_scenarios()))
@click.option("--url", required=True)
def scenario_run_cmd(name: str, url: str) -> None:
    result = run_scenario(name, url)
    console.print(f"{result['name']} status={result['status_code']}")


@main.command("chain")
@click.argument("url1")
@click.argument("url2")
def chain_cmd(url1: str, url2: str) -> None:
    result = run_chain(url1, url2)
    table = Table(title="babel chain")
    table.add_column("First")
    table.add_column("Second")
    table.add_column("Preview")
    table.add_row(str(result["first_status"]), str(result["second_status"]), result["preview"])
    console.print(table)


if __name__ == "__main__":
    main()
