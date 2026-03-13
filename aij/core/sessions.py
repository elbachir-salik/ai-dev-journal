"""Session-related logic."""

import json
import os

from aij.core.storage import (
    read_config,
    write_config,
    get_sessions_dir,
    get_session_path,
)


def get_current_session() -> int | None:
    config = read_config()
    return config.get("current_session")


def start_session(name: str) -> int:
    """Start a new session. Returns session_id. Raises if one is already active."""
    config = read_config()
    if config.get("current_session"):
        raise ValueError("A session is already active.")

    sessions_dir = get_sessions_dir()
    session_id = len(os.listdir(sessions_dir)) + 1

    session = {
        "id": session_id,
        "name": name,
        "entries": [],
    }

    session_file = get_session_path(session_id)
    with open(session_file, "w") as f:
        json.dump(session, f, indent=2)

    config["current_session"] = session_id
    write_config(config)

    return session_id


def end_session() -> int | None:
    """End the current session. Returns the session_id that was ended, or None."""
    config = read_config()
    session_id = config.get("current_session")
    if not session_id:
        return None

    config["current_session"] = None
    write_config(config)
    return session_id


def add_entry_to_session(entry_id: int) -> None:
    """Append an entry id to the current session's entries."""
    session_id = get_current_session()
    if not session_id:
        return

    session_file = get_session_path(session_id)
    if not os.path.exists(session_file):
        return

    with open(session_file) as f:
        session = json.load(f)

    session["entries"].append(entry_id)

    with open(session_file, "w") as f:
        json.dump(session, f, indent=2)


def list_sessions() -> list[dict]:
    """Return list of session dicts, sorted by id descending."""
    sessions_dir = get_sessions_dir()
    if not os.path.exists(sessions_dir):
        return []

    filenames = os.listdir(sessions_dir)
    if not filenames:
        return []

    sessions = []
    for fn in filenames:
        path = os.path.join(sessions_dir, fn)
        with open(path) as f:
            sessions.append(json.load(f))

    sessions.sort(key=lambda s: s["id"], reverse=True)
    return sessions


def read_session(session_id: int) -> dict | None:
    path = get_session_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)
