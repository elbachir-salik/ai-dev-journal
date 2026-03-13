"""Record an AI development step."""

import subprocess
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from aij.core.storage import (
    journal_initialized,
    read_config,
    write_config,
    write_entry,
)
from aij.core.sessions import add_entry_to_session


def record():
    """Record an AI development step"""

    console = Console()

    if not journal_initialized():
        console.print("[red]AI Journal not initialized. Run 'init' first.[/red]")
        raise typer.Exit()

    console.print("\n[bold cyan]Checking for code changes...[/bold cyan]\n")

    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True,
    )

    diff = result.stdout

    if not diff.strip():
        console.print("[yellow]No changes detected.[/yellow]")
        raise typer.Exit()

    files = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    console.print("[bold green]Files changed:[/bold green]")
    for f in files:
        console.print(f"  • {f}")

    console.print()

    syntax = Syntax(diff, "diff", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Diff Preview"))

    console.print()

    prompt = typer.prompt("Describe this AI change")

    confirm = typer.confirm("Record this entry?")

    if not confirm:
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit()

    config = read_config()
    entry_id = config["entries"] + 1

    entry = {
        "id": entry_id,
        "timestamp": str(datetime.now()),
        "prompt": prompt,
        "files": files,
        "diff": diff,
    }

    write_entry(entry_id, entry)

    config["entries"] = entry_id
    add_entry_to_session(entry_id)
    write_config(config)

    console.print(f"\n[bold green]✓ Recorded AI step #{entry_id}[/bold green]")
