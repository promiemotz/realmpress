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
    import logging
    logger = logging.getLogger(__name__)
    
    entries = []
    logger.info(f"🔍 Starting to load JSON entries from: {folder_path}")
    
    file_count = 0
    loaded_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(folder_path):
        logger.debug(f"📂 Scanning directory: {root}")
        logger.debug(f"📂 Found {len(dirs)} subdirectories: {dirs[:5]}{'...' if len(dirs) > 5 else ''}")
        logger.debug(f"📄 Found {len(files)} files: {files[:5]}{'...' if len(files) > 5 else ''}")
        
        for filename in files:
            if filename.endswith(".json"):
                file_count += 1
                file_path = os.path.join(root, filename)
                logger.debug(f"📄 Processing JSON file: {file_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            entries.extend(data)
                            loaded_count += len(data)
                            logger.debug(f"✅ Loaded {len(data)} entries from list in {filename}")
                        elif isinstance(data, dict):
                            entries.append(data)
                            loaded_count += 1
                            logger.debug(f"✅ Loaded 1 entry from dict in {filename}")
                        else:
                            logger.warning(f"⚠️ Unexpected data type in {filename}: {type(data)}")
                except json.JSONDecodeError as e:
                    error_count += 1
                    logger.warning(f"⚠️ Skipped invalid JSON: {file_path} - {e}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Error reading file {file_path}: {e}")
    
    logger.info(f"📊 JSON loading summary:")
    logger.info(f"   - Files processed: {file_count}")
    logger.info(f"   - Entries loaded: {loaded_count}")
    logger.info(f"   - Errors encountered: {error_count}")
    logger.info(f"   - Total entries in result: {len(entries)}")
    
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