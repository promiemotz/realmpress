"""
test_entity_processing.py
------------------------
Unit tests for entity_processing module.

Note: Uses sys.path.insert to import entity_processing from ../kanka_to_md for testability without package install.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../kanka_to_md')))
import entity_processing  # type: ignore

def test_build_entity_map():
    entries = [
        {"entity": {"id": 1, "type": "character"}, "name": "Alice"},
        {"entity": {"id": 2, "type": "location"}, "name": "Bob"},
    ]
    result = entity_processing.build_entity_map(entries)
    assert result[1]["name"] == "Alice"
    assert result[2]["type"] == "location"


def test_get_type_id_sets():
    types = entity_processing.get_type_id_sets()
    assert "CHARACTER_TYPE_IDS" in types
    assert isinstance(types["CHARACTER_TYPE_IDS"], set)


def test_filter_entities_by_type():
    entries = [
        {"entity": {"type_id": 1}},
        {"entity": {"type_id": 2}},
    ]
    filtered = entity_processing.filter_entities_by_type(entries, {1})
    assert len(filtered) == 1
    assert filtered[0]["entity"]["type_id"] == 1


def test_filter_entities_by_type_dict():
    entries = [
        {"entity": {"id": 1, "type_id": 1}},
        {"entity": {"id": 2, "type_id": 2}},
    ]
    filtered = entity_processing.filter_entities_by_type_dict(entries, {1})
    assert 1 in filtered
    assert 2 not in filtered


def test_build_character_id_to_entity_id():
    entries = [
        {"id": 10, "entity": {"id": 100, "type_id": 1}},
        {"id": 20, "entity": {"id": 200, "type_id": 2}},
    ]
    mapping = entity_processing.build_character_id_to_entity_id(entries)
    assert mapping[10] == 100
    assert 20 not in mapping 