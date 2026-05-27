from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from .banner import COLLIDER_BANNER
from .engine import find, generate_candidates, rank

console = Console()


def _banner() -> None:
    console.print(f"[bold green]{COLLIDER_BANNER}[/bold green]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD embedding collision helper."""


@main.command("rank")
@click.argument("text1")
@click.argument("text2")
def rank_cmd(text1: str, text2: str) -> None:
    console.print(f"score={rank(text1, text2):.4f}")


@main.command("find")
@click.argument("target_text")
@click.option("--embed-url")
def find_cmd(target_text: str, embed_url: str | None) -> None:
    result = find(target_text, embed_url=embed_url)
    table = Table(title="collider find")
    table.add_column("Mode")
    table.add_column("Score")
    table.add_column("Candidate")
    table.add_row(result["mode"], f"{result['score']:.4f}", result["candidate"])
    console.print(table)


@main.command("generate")
@click.option("--near", "near_text", required=True)
@click.option("--steps", default=10, show_default=True, type=int)
def generate_cmd(near_text: str, steps: int) -> None:
    for item in generate_candidates(near_text, steps=steps):
        console.print(item)


if __name__ == "__main__":
    main()
