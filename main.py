import typer
import os
import json

app = typer.Typer()

@app.command()
def init():
    """
    Initialize AI Dev Journal in the current project.
    """

    journal_dir = ".ai-journal"
    entries_dir = os.path.join(journal_dir, "entries")
    config_file = os.path.join(journal_dir, "config.json")

    if os.path.exists(journal_dir):
        print("AI Journal already initialized.")
        return

    # create folders
    os.makedirs(entries_dir)

    # create config
    config = {
        "version": "0.1",
        "entries": 0
    }

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print("AI Dev Journal initialized.")
    print("Folder created: .ai-journal")


if __name__ == "__main__":
    app()