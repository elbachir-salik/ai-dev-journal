import typer
import os
import subprocess
import json
from rich.console import Console
import sys

console = Console()


def install_hook():
    """Install the Git post-commit hook for AI Journal"""

    git_dir = ".git"
    hooks_dir = os.path.join(git_dir, "hooks")
    hook_file = os.path.join(hooks_dir, "post-commit")

    if not os.path.exists(git_dir):
        console.print("[red]This is not a git repository.[/red]")
        raise typer.Exit()

    script = """#!/bin/sh
python main.py commit-hook
"""

    with open(hook_file, "w") as f:
        f.write(script)

    os.chmod(hook_file, 0o755)

    console.print("[green]AI Journal Git hook installed successfully.[/green]")


def commit_hook():
    """Triggered automatically after git commit"""

    try:
        if not sys.stdin.isatty():
            console.print("[yellow]AI Journal: non-interactive terminal detected, skipping prompt.[/yellow]")
            return
        # get commit message
        commit_msg = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True
        ).stdout.strip()

        # get changed files
        files = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True,
            text=True
        ).stdout.splitlines()

        # get diff
        diff = subprocess.run(
            ["git", "show", "HEAD"],
            capture_output=True,
            text=True
        ).stdout

        console.print("\n[bold cyan]AI Journal detected a new commit[/bold cyan]\n")

        console.print(f"[bold]Commit message:[/bold] {commit_msg}")

        if files:
            console.print("\n[bold]Files changed:[/bold]")
            for f in files:
                console.print(f"  • {f}")

        record = input("\nStore this commit in AI Journal? (y/n): ").lower() == "y"

        if not record:
            return

        # prompt = typer.prompt("What AI prompt produced this change?")
        # summary = typer.prompt("Summary (optional)", default="")
        prompt = input("What AI prompt produced this change? ")
        summary = input("Summary (optional): ") or ""

        config_file = ".ai-journal/config.json"
        entries_dir = ".ai-journal/entries"

        if not os.path.exists(config_file):
            console.print("[red]AI Journal not initialized.[/red]")
            return

        with open(config_file) as f:
            config = json.load(f)

        entry_id = config["entries"] + 1

        entry = {
            "id": entry_id,
            "prompt": prompt,
            "summary": summary,
            "files": files,
            "diff": diff
        }

        entry_file = os.path.join(entries_dir, f"{entry_id:03}.json")

        with open(entry_file, "w") as f:
            json.dump(entry, f, indent=2)

        config["entries"] = entry_id

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        console.print(f"\n[green]Recorded AI Journal entry #{entry_id}[/green]")

    except Exception as e:
        # never break git commit
        console.print(f"[red]AI Journal hook error:[/red] {e}")