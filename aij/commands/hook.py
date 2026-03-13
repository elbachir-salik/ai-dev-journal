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
        import platform

        # Open terminal directly — bypasses git's stdin redirection
        try:
            if platform.system() == "Windows":
                conin = open("CONIN$", "r")
                conout = open("CONOUT$", "w")
            else:
                conin = open("/dev/tty", "r")
                conout = open("/dev/tty", "w")
        except Exception:
            console.print("[yellow]AI Journal: no interactive terminal available.[/yellow]")
            return

        def tty_input(prompt_text):
            conout.write(prompt_text)
            conout.flush()
            return conin.readline().strip()

        # get commit message
        commit_msg = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True, text=True
        ).stdout.strip()

        # get changed files
        files = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True, text=True
        ).stdout.splitlines()

        # get diff
        diff = subprocess.run(
            ["git", "show", "HEAD"],
            capture_output=True, text=True
        ).stdout

        # get commit SHA
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True
        ).stdout.strip()

        conout.write("\nAI Journal detected a new commit\n")
        conout.write(f"Commit message: {commit_msg}\n")
        if files:
            conout.write("\nFiles changed:\n")
            for f in files:
                conout.write(f"  - {f}\n")
        conout.flush()

        record = tty_input("\nStore this commit in AI Journal? (y/n): ").lower() == "y"
        if not record:
            conin.close()
            conout.close()
            return

        prompt = tty_input("What AI prompt produced this change? ")
        summary = tty_input("Summary (optional): ")

        conin.close()
        conout.close()

        config_file = ".ai-journal/config.json"
        entries_dir = ".ai-journal/entries"

        if not os.path.exists(config_file):
            print("AI Journal not initialized.")
            return

        with open(config_file) as f:
            config = json.load(f)

        entry_id = config["entries"] + 1

        entry = {
            "schema_version": 1,
            "id": entry_id,
            "commit_sha": sha,
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

        print(f"\nRecorded AI Journal entry #{entry_id}")

    except Exception as e:
        print(f"AI Journal hook error: {e}")