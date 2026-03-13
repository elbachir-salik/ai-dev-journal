"""Initialize AI Dev Journal in the current project."""

import os
import typer

from aij.core.storage import (
    JOURNAL_DIR,
    get_entries_dir,
    get_sessions_dir,
    write_config,
)


def init():
    """Initialize AI Dev Journal in the current project"""

    if os.path.exists(JOURNAL_DIR):
        typer.echo("AI Journal already initialized.")
        raise typer.Exit()

    os.makedirs(get_entries_dir())
    os.makedirs(get_sessions_dir())

    config = {
        "version": "0.1",
        "entries": 0,
        "current_session": None,
    }

    write_config(config)

    typer.echo("AI Dev Journal initialized.")
    typer.echo("Created .ai-journal directory")
