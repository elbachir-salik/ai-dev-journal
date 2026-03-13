"""Shared filesystem logic for journal config and entries."""

import json
import os

JOURNAL_DIR = ".ai-journal"


def get_entries_dir() -> str:
    return os.path.join(JOURNAL_DIR, "entries")


def get_config_path() -> str:
    return os.path.join(JOURNAL_DIR, "config.json")


def get_sessions_dir() -> str:
    return os.path.join(JOURNAL_DIR, "sessions")


def journal_initialized() -> bool:
    return os.path.exists(JOURNAL_DIR)


def read_config() -> dict:
    with open(get_config_path()) as f:
        return json.load(f)


def write_config(config: dict) -> None:
    with open(get_config_path(), "w") as f:
        json.dump(config, f, indent=2)


def get_entry_path(entry_id: int) -> str:
    return os.path.join(get_entries_dir(), f"{entry_id:03}.json")


def get_session_path(session_id: int) -> str:
    return os.path.join(get_sessions_dir(), f"{session_id:03}.json")


def read_entry(entry_id: int) -> dict | None:
    path = get_entry_path(entry_id)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def write_entry(entry_id: int, data: dict) -> None:
    path = get_entry_path(entry_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def list_entry_filenames() -> list[str]:
    entries_dir = get_entries_dir()
    if not os.path.exists(entries_dir):
        return []
    return os.listdir(entries_dir)
