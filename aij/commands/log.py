"""Show AI development history."""

import os
import typer
from rich.console import Console
from rich.panel import Panel

from aij.core.storage import get_entries_dir, journal_initialized, read_entry, list_entry_filenames


def log(oneline: bool = typer.Option(False, "--oneline", "-o")):
    """Show AI development history"""

    console = Console()

    if not journal_initialized():
        console.print("[red]AI Journal not initialized.[/red]")
        raise typer.Exit()

    entries_dir = get_entries_dir()
    if not os.path.exists(entries_dir):
        console.print("[red]AI Journal not initialized.[/red]")
        raise typer.Exit()

    filenames = list_entry_filenames()

    if not filenames:
        console.print("[yellow]No AI entries recorded yet.[/yellow]")
        return

    filenames.sort(reverse=True)

    console.print("\n[bold cyan]AI Journal History[/bold cyan]\n")

    for file in filenames:
        # Parse entry id from filename (e.g. 001.json -> 1)
        entry_id = int(file.split(".")[0])
        entry = read_entry(entry_id)
        if entry is None:
            continue

        if oneline:
            console.print(f"{entry['id']}  {entry['prompt']}")
        else:
            files = ", ".join(entry.get("files", []))
            text = f"[bold]{entry['prompt']}[/bold]\n\n"
            text += f"[dim]Files:[/dim] {files}\n"
            text += f"[dim]Time :[/dim] {entry.get('timestamp', '')}"
            console.print(Panel(text, title=f"Entry #{entry['id']}"))
