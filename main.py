"""
AI Dev Journal CLI.

Usage:
  python main.py init
  python main.py record
  python main.py log
  python main.py show <entry_id>
  python main.py session-start "name"
  python main.py session-end
  python main.py session-log
  python main.py session-show <session_id>
"""

import typer

from aij.commands import init as init_cmd
from aij.commands import record as record_cmd
from aij.commands import log as log_cmd
from aij.commands import show as show_cmd
from aij.commands import session as session_cmd
from aij.commands.hook import install_hook, commit_hook
app = typer.Typer(help="AI Dev Journal CLI")


@app.callback()
def main():
    """
    AI Dev Journal CLI
    """
    pass


app.command()(init_cmd.init)
app.command()(record_cmd.record)
app.command()(log_cmd.log)
app.command()(show_cmd.show)
app.command()(session_cmd.session_start)
app.command()(session_cmd.session_end)
app.command()(session_cmd.session_log)
app.command()(session_cmd.session_show)
app.command("install-hook")(install_hook)
app.command("commit-hook")(commit_hook)


if __name__ == "__main__":
    app()