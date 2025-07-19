"""
entity_processing.py
-------------------
Utility functions for processing Kanka entity data.

Provides helpers to:
- Build mappings between entity IDs, names, and types
- Filter entities by type
- Support downstream processing for markdown/HTML generation

Intended for use in the Kanka to Markdown/HTML workflow.
"""

from typing import List, Dict, Any, Set


def build_entity_map(entries: List[Dict[str, Any]]) -> Dict[int, Dict[str, str]]:
    """Build a mapping from entity id to entity name and type."""
    entity_map = {}
    for entry in entries:
        entity = entry.get('entity')
        if entity:
            entity_map[entity['id']] = {
                'name': entry.get('name') or entity.get('name', 'Unknown'),
                'type': entity.get('type', 'Unknown'),
            }
    return entity_map


def get_type_id_sets() -> Dict[str, Set[int]]:
    """Return a dictionary of type_id sets for each entity type."""
    return {
        'CHARACTER_TYPE_IDS': {1},
        'LOCATION_TYPE_IDS': {3, 7},
        'EVENT_TYPE_IDS': {10, 12, 18},
        'ORGANIZATION_TYPE_IDS': {4},
        'ITEM_TYPE_IDS': {5},
        'FAMILY_TYPE_IDS': {2},
        'NOTE_TYPE_IDS': {6},
        'RACE_TYPE_IDS': {9},
    }


def filter_entities_by_type(entries: List[Dict[str, Any]], type_ids: Set[int]) -> List[Dict[str, Any]]:
    """Filter entities by a set of type_ids."""
    return [e for e in entries if e.get('entity', {}).get('type_id') in type_ids]


def filter_entities_by_type_dict(entries: List[Dict[str, Any]], type_ids: Set[int]) -> Dict[int, Dict[str, Any]]:
    """Filter entities by a set of type_ids and return as a dict keyed by entity id."""
    return {e['entity']['id']: e for e in entries if e.get('entity', {}).get('type_id') in type_ids}


def build_character_id_to_entity_id(entries: List[Dict[str, Any]]) -> Dict[int, int]:
    """Build a mapping from character id to entity id for characters."""
    mapping = {}
    for entry in entries:
        if entry.get('entity') and entry.get('entity', {}).get('type_id') == 1:
            mapping[entry['id']] = entry['entity']['id']
    return mapping 