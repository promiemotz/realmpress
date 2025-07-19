"""
io_utils.py
-----------
Input/output utility functions for Kanka to Markdown/HTML workflow.

Provides helpers to:
- Load JSON entries from folders (recursively)
- Save markdown output to files
- Load configuration from JSON files

Intended for use in the Kanka to Markdown/HTML workflow.
"""

import os
import json
from typing import List, Dict, Any


def load_json_entries(folder_path: str) -> List[Dict[str, Any]]:
    """Recursively load all JSON files from folder and subfolders."""
    entries = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            entries.extend(data)
                        elif isinstance(data, dict):
                            entries.append(data)
                    except json.JSONDecodeError:
                        print(f"⚠️ Skipped invalid JSON: {file_path}")
    return entries


def save_markdown(output_file: str, markdown: str) -> None:
    """Save the generated markdown to a file."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from a JSON file. Returns a dict with at least 'include_private'."""
    default_config = {"include_private": False}
    if not os.path.exists(config_path):
        return default_config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                return default_config
            return {**default_config, **config}
    except Exception:
        return default_config 