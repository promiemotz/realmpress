"""
localization.py
---------------
Localization support for the Kanka to Markdown/HTML/PDF workflow.

Provides translations for chapter titles and other UI elements.
"""

import json
import os
from typing import Dict, Any

# Available languages
SUPPORTED_LANGUAGES = ['hu', 'en']

# Default language
DEFAULT_LANGUAGE = 'en'

# Global cache for translations
_TRANSLATIONS_CACHE = None

def _load_translations() -> Dict[str, Any]:
    """
    Load translations from the JSON file.
    
    Returns:
        Dictionary containing all translations
    """
    global _TRANSLATIONS_CACHE
    
    if _TRANSLATIONS_CACHE is not None:
        return _TRANSLATIONS_CACHE
    
    # Get the directory where this module is located
    module_dir = os.path.dirname(os.path.abspath(__file__))
    translations_file = os.path.join(module_dir, 'translations.json')
    
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            _TRANSLATIONS_CACHE = json.load(f)
        return _TRANSLATIONS_CACHE
    except FileNotFoundError:
        raise FileNotFoundError(f"Translations file not found: {translations_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in translations file: {e}")

def get_translation(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Get a translation for the given key in the specified language.
    
    Args:
        key: The translation key (can be 'chapter_titles.key' or 'ui_elements.key')
        language: The language code (e.g., 'hu', 'en')
        
    Returns:
        The translated string, or the key itself if translation not found
    """
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    translations = _load_translations()
    lang_data = translations.get(language, {})
    
    # Handle nested keys like 'chapter_titles.locations'
    if '.' in key:
        section, subkey = key.split('.', 1)
        section_data = lang_data.get(section, {})
        return section_data.get(subkey, key)
    
    # Handle legacy flat keys (for backward compatibility)
    # Check all sections for the key
    for section in ['chapter_titles', 'section_slugs', 'ui_elements']:
        section_data = lang_data.get(section, {})
        if key in section_data:
            return section_data[key]
    
    return key

def get_chapter_title(chapter_type: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Get the chapter title for a specific entity type.
    
    Args:
        chapter_type: The entity type (e.g., 'locations', 'characters')
        language: The language code
        
    Returns:
        The translated chapter title
    """
    return get_translation(f'chapter_titles.{chapter_type}', language)

def get_chapter_slug(chapter_type: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Get the chapter slug for a specific entity type.
    
    Args:
        chapter_type: The entity type (e.g., 'locations', 'characters')
        language: The language code
        
    Returns:
        The translated chapter slug
    """
    return get_translation(f'section_slugs.{chapter_type}', language)

def get_ui_text(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Get UI text translation.
    
    Args:
        key: The UI text key
        language: The language code
        
    Returns:
        The translated UI text
    """
    return get_translation(f'ui_elements.{key}', language)

def validate_language(language: str) -> str:
    """
    Validate and return a supported language code.
    
    Args:
        language: The language code to validate
        
    Returns:
        A valid language code, or the default if invalid
    """
    if language in SUPPORTED_LANGUAGES:
        return language
    return DEFAULT_LANGUAGE

def reload_translations():
    """
    Reload translations from the JSON file.
    Useful for development or when translations are updated.
    """
    global _TRANSLATIONS_CACHE
    _TRANSLATIONS_CACHE = None
    _load_translations() 