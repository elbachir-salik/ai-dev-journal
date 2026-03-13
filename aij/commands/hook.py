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

        # Open terminal directly (works for Windows + Linux)
        try:
            if platform.system() == "Windows":
                conin = open("CONIN$", "r")
                conout = open("CONOUT$", "w")
            else:
                conin = open("/dev/tty", "r")
                conout = open("/dev/tty", "w")
        except Exception:
            print("AI Journal: no interactive terminal available.")
            return

        def tty_input(prompt_text):
            conout.write(prompt_text)
            conout.flush()
            return conin.readline().strip()

        # --- GET COMMIT DATA ---

        commit_msg = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True
        ).stdout.strip()

        files = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True,
            text=True
        ).stdout.splitlines()

        diff = subprocess.run(
            ["git", "show", "HEAD"],
            capture_output=True,
            text=True
        ).stdout

        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True
        ).stdout.strip()

        # --- DISPLAY COMMIT INFO ---

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

        # --- LOAD CONFIG ---

        config_file = ".ai-journal/config.json"
        entries_dir = ".ai-journal/entries"
        sessions_dir = ".ai-journal/sessions"

        if not os.path.exists(config_file):
            print("AI Journal not initialized.")
            return

        with open(config_file) as f:
            config = json.load(f)

        current_session = config.get("current_session")

        # --- SESSION MANAGEMENT ---

        if current_session is None:
            start_session = tty_input(
                "\nNo active session. Start a new session? (y/n): "
            ).lower() == "y"

            if start_session:
                session_name = tty_input("Session name: ")

                session_id = len(os.listdir(sessions_dir)) + 1

                session = {
                    "id": session_id,
                    "name": session_name,
                    "entries": []
                }

                with open(f"{sessions_dir}/{session_id:03}.json", "w") as f:
                    json.dump(session, f, indent=2)

                config["current_session"] = session_id

                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)

                current_session = session_id

                conout.write(f"Started session: {session_name}\n")

        else:
            session_file = f"{sessions_dir}/{current_session:03}.json"

            if os.path.exists(session_file):
                with open(session_file) as f:
                    session = json.load(f)

                conout.write(
                    f"\nActive session: {session['name']}\n"
                )

                add_to_session = tty_input(
                    "Add this commit to the current session? (y/n): "
                ).lower() == "y"

                if not add_to_session:
                    conin.close()
                    conout.close()
                    return

        # --- PROMPT CAPTURE ---

        prompt = tty_input(
            "AI prompt (leave empty to use commit message): "
        )

        if prompt == "":
            prompt = commit_msg

        summary = tty_input("Summary (optional): ")

        # --- CREATE ENTRY ---

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

        # --- ATTACH ENTRY TO SESSION ---

        if current_session:
            session_file = f"{sessions_dir}/{current_session:03}.json"

            with open(session_file) as f:
                session = json.load(f)

            session["entries"].append(entry_id)

            with open(session_file, "w") as f:
                json.dump(session, f, indent=2)

        conout.write(f"\nRecorded AI Journal entry #{entry_id}\n")

        # --- OFFER SESSION END  ---

        if current_session:
            end = tty_input(
                "\nContinue working on this session? (y/n): "
            ).lower()

            if end == "n":
                config["current_session"] = None

                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)

                conout.write("Session ended.\n")

        conin.close()
        conout.close()

    except Exception as e:
        print(f"AI Journal hook error: {e}")
        #test active session