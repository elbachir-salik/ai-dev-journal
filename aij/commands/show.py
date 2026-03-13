"""Show details of a specific AI entry."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from aij.core.storage import read_entry


def show(entry_id: int):
    """Show details of a specific AI entry"""

    console = Console()

    entry = read_entry(entry_id)

    if entry is None:
        console.print(f"[red]Entry #{entry_id} not found.[/red]")
        raise typer.Exit()

    console.print(f"\n[bold cyan]Entry #{entry['id']}[/bold cyan]\n")

    console.print(f"[bold]Prompt:[/bold] {entry['prompt']}")
    console.print(f"[dim]Time:[/dim] {entry.get('timestamp', '')}")

    files = ", ".join(entry.get("files", []))
    console.print(f"[dim]Files:[/dim] {files}\n")

    diff = entry.get("diff", "")
    syntax = Syntax(diff, "diff", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Diff"))
