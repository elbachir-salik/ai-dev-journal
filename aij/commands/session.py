"""Session commands: session-start, session-end, session-log, session-show."""

import typer
from rich.console import Console
from rich.panel import Panel

from aij.core.storage import read_entry
from aij.core.sessions import (
    start_session,
    end_session,
    list_sessions,
    read_session,
)


def session_start(name: str):
    """Start a new AI development session"""

    console = Console()

    try:
        session_id = start_session(name)
        console.print(f"[green]Started session #{session_id}: {name}[/green]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit()
    except FileNotFoundError:
        console.print("[red]AI Journal not initialized. Run 'init' first.[/red]")
        raise typer.Exit()


def session_end():
    """End the current AI session"""

    console = Console()

    session_id = end_session()
    if session_id is None:
        console.print("[yellow]No active session.[/yellow]")
        return

    console.print(f"[green]Session #{session_id} ended.[/green]")


def session_log():
    """List AI sessions"""

    console = Console()

    sessions = list_sessions()

    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    for session in sessions:
        text = f"[bold]{session['name']}[/bold]\n"
        text += f"[dim]Entries:[/dim] {len(session['entries'])}"
        console.print(Panel(text, title=f"Session #{session['id']}"))


def session_show(session_id: int):
    """Show details of a session"""

    console = Console()

    session = read_session(session_id)

    if session is None:
        console.print("[red]Session not found.[/red]")
        raise typer.Exit()

    console.print(f"\n[bold cyan]Session #{session['id']}[/bold cyan]")
    console.print(f"[bold]{session['name']}[/bold]\n")

    for entry_id in session["entries"]:
        entry = read_entry(entry_id)
        if entry is not None:
            console.print(f"{entry['id']}  {entry['prompt']}")
