"""
test_markdown_utils.py
---------------------
Unit tests for markdown_utils module.

Note: Uses sys.path.insert to import markdown_utils from ../kanka_to_md for testability without package install.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../kanka_to_md')))
import markdown_utils  # type: ignore

def test_create_anchor_label():
    assert markdown_utils.create_anchor_label("Hello World!") == "hello-world"
    assert markdown_utils.create_anchor_label("Árvíztűrő tükörfúrógép") == "arvizturo-tukorfurogep"
    assert markdown_utils.create_anchor_label("") == ""


def test_md_escape():
    assert markdown_utils.md_escape("foo_bar") == "foo\\_bar"
    assert markdown_utils.md_escape(None) == ""


def test_replace_mentions():
    entity_map = {123: {"name": "Alice"}}
    text = "[character:123]"
    replaced = markdown_utils.replace_mentions(text, entity_map)
    assert "[Alice](#alice)" in replaced
    # Test fallback for missing entity
    text2 = "[character:999]"
    replaced2 = markdown_utils.replace_mentions(text2, entity_map)
    assert "**Entity_999**" in replaced2 