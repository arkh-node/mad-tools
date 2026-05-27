from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import click
from rich.console import Console
from rich.table import Table

from .banner import SNARE_BANNER
from .traps import ROOT, TEMPLATES, create_trap, list_traps

console = Console()


def _banner() -> None:
    console.print(f"[bold yellow]{SNARE_BANNER}[/bold yellow]")


class BannerGroup(click.Group):
    def get_help(self, ctx: click.Context) -> str:
        _banner()
        return super().get_help(ctx)


@click.group(cls=BannerGroup)
def main() -> None:
    """MAD browser trap utility."""


@main.command("new")
@click.option("--type", "kind", required=True, type=click.Choice(sorted(TEMPLATES)))
def new_cmd(kind: str) -> None:
    path = create_trap(kind)
    console.print(path)


@main.command("list")
def list_cmd() -> None:
    table = Table(title="snare traps")
    table.add_column("File")
    for path in list_traps():
        table.add_row(str(path))
    console.print(table)


@main.command("serve")
@click.option("--port", default=8888, show_default=True, type=int)
def serve_cmd(port: int) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    console.print(f"serving {ROOT} on 127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
