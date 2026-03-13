import typer
import os
import json

app = typer.Typer(help="AI Dev Journal CLI")

@app.callback()
def main():
    """
    AI Dev Journal CLI
    """
    pass


@app.command()
def init():
    """Initialize AI Dev Journal in the current project"""

    journal_dir = ".ai-journal"
    entries_dir = os.path.join(journal_dir, "entries")
    config_file = os.path.join(journal_dir, "config.json")
    sessions_dir = os.path.join(journal_dir, "sessions")


    if os.path.exists(journal_dir):
        typer.echo("AI Journal already initialized.")
        raise typer.Exit()

    os.makedirs(entries_dir)
    os.makedirs(sessions_dir)

    config = {
        "version": "0.1",
        "entries": 0,
        "current_session": None
    }

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    typer.echo("AI Dev Journal initialized.")
    typer.echo("Created .ai-journal directory")


@app.command()
def record():
    """Record an AI development step"""

    import subprocess
    from datetime import datetime
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel

    console = Console()

    journal_dir = ".ai-journal"
    entries_dir = os.path.join(journal_dir, "entries")
    config_file = os.path.join(journal_dir, "config.json")

    if not os.path.exists(journal_dir):
        console.print("[red]AI Journal not initialized. Run 'init' first.[/red]")
        raise typer.Exit()

    console.print("\n[bold cyan]Checking for code changes...[/bold cyan]\n")

    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True
    )

    diff = result.stdout

    if not diff.strip():
        console.print("[yellow]No changes detected.[/yellow]")
        raise typer.Exit()

    # show files changed
    files = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True
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

    with open(config_file) as f:
        config = json.load(f)

    entry_id = config["entries"] + 1

    entry = {
        "id": entry_id,
        "timestamp": str(datetime.now()),
        "prompt": prompt,
        "files": files,
        "diff": diff
    }

    entry_file = os.path.join(entries_dir, f"{entry_id:03}.json")

    with open(entry_file, "w") as f:
        json.dump(entry, f, indent=2)

    config["entries"] = entry_id

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    console.print(f"\n[bold green]✓ Recorded AI step #{entry_id}[/bold green]")


@app.command()
def log(oneline: bool = typer.Option(False, "--oneline", "-o")):
    """Show AI development history"""

    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    journal_dir = ".ai-journal"
    entries_dir = os.path.join(journal_dir, "entries")

    if not os.path.exists(entries_dir):
        console.print("[red]AI Journal not initialized.[/red]")
        raise typer.Exit()

    entries = os.listdir(entries_dir)

    if not entries:
        console.print("[yellow]No AI entries recorded yet.[/yellow]")
        return

    entries.sort(reverse=True)

    console.print("\n[bold cyan]AI Journal History[/bold cyan]\n")

    for file in entries:
        path = os.path.join(entries_dir, file)

        with open(path) as f:
            entry = json.load(f)

        if oneline:
            console.print(f"{entry['id']}  {entry['prompt']}")
        else:
            files = ", ".join(entry.get("files", []))

            text = f"[bold]{entry['prompt']}[/bold]\n\n"
            text += f"[dim]Files:[/dim] {files}\n"
            text += f"[dim]Time :[/dim] {entry['timestamp']}"

            console.print(Panel(text, title=f"Entry #{entry['id']}"))


@app.command()
def show(entry_id: int):
    """Show details of a specific AI entry"""

    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel

    console = Console()

    entry_file = f".ai-journal/entries/{entry_id:03}.json"

    if not os.path.exists(entry_file):
        console.print(f"[red]Entry #{entry_id} not found.[/red]")
        raise typer.Exit()

    with open(entry_file) as f:
        entry = json.load(f)

    console.print(f"\n[bold cyan]Entry #{entry['id']}[/bold cyan]\n")

    console.print(f"[bold]Prompt:[/bold] {entry['prompt']}")
    console.print(f"[dim]Time:[/dim] {entry['timestamp']}")

    files = ", ".join(entry.get("files", []))
    console.print(f"[dim]Files:[/dim] {files}\n")

    diff = entry["diff"]

    syntax = Syntax(diff, "diff", theme="monokai", line_numbers=False)

    console.print(Panel(syntax, title="Diff"))
if __name__ == "__main__":
    app()