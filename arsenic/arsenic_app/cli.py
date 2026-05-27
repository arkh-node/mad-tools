from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from .banner import ARSENIC_BANNER
from .generator import create_document, list_templates

console = Console()


def _banner() -> None:
    console.print(f"[bold green]{ARSENIC_BANNER}[/bold green]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD RAG poison kit."""


@main.command("templates")
def templates_cmd() -> None:
    for item in list_templates():
        console.print(item)


@main.command("new")
@click.option("--type", "doc_type", required=True, type=click.Choice(["md", "html", "pdf"]))
@click.option("--payload", required=True)
@click.option("--strategy", default="direct", show_default=True)
def new_cmd(doc_type: str, payload: str, strategy: str) -> None:
    path = create_document(doc_type, payload, strategy)
    console.print(f"[green]Created[/green] {path}")


@main.command("preview")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def preview_cmd(file: Path) -> None:
    console.print(file.read_text(encoding="utf-8", errors="replace")[:4000])


if __name__ == "__main__":
    main()
