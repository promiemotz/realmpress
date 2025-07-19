"""
test_io_utils.py
---------------
Unit tests for io_utils module.

Note: Uses sys.path.insert to import io_utils from ../kanka_to_md for testability without package install.
"""

import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../kanka_to_md')))
import io_utils  # type: ignore

def test_load_json_entries(tmp_path):
    # Create a temporary directory with JSON files
    d = tmp_path / "subdir"
    d.mkdir()
    file1 = d / "a.json"
    file2 = d / "b.json"
    file1.write_text(json.dumps({"foo": 1}))
    file2.write_text(json.dumps([{"bar": 2}]))
    entries = io_utils.load_json_entries(str(tmp_path))
    assert any(e.get("foo") == 1 for e in entries)
    assert any(e.get("bar") == 2 for e in entries)


def test_save_markdown(tmp_path):
    md_file = tmp_path / "test.md"
    io_utils.save_markdown(str(md_file), "# Hello\nWorld")
    assert md_file.read_text() == "# Hello\nWorld"


def test_load_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"include_private": True}))
    config = io_utils.load_config(str(config_file))
    assert config["include_private"] is True
    # Test default config if file missing
    config = io_utils.load_config(str(tmp_path / "missing.json"))
    assert config["include_private"] is False 