"""
main.py
-------
Main entry point for the Kanka to Markdown/HTML/PDF workflow.

This script does the following steps in order:
1. Fetches updated data from your Kanka campaign
2. Processes all the entities (characters, locations, etc.)
3. Generates a beautiful markdown worldbook
4. Converts the markdown to HTML with styling
5. Converts the HTML to PDF with working links
6. OPTIONAL: Uploads the PDF to Google Drive

You can easily comment out any step you don't want to use!
"""

import os
import subprocess
import time
import logging
from datetime import datetime, timezone
from io_utils import load_json_entries, save_markdown, load_config
from entity_processing import (
    build_entity_map, get_type_id_sets, filter_entities_by_type, filter_entities_by_type_dict, build_character_id_to_entity_id
)
from worldbook_generator import generate_worldbook
from kanka_function import fetch_and_save_updated_entities, save_last_run_time
from html_converter import convert_markdown_file_to_html
from pdf_converter_wkhtmltopdf import convert_html_to_pdf

# =============================================================================
# SETUP LOGGING - This creates log files so you can see what happened
# =============================================================================
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/realmpress.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION - You can change these paths if needed
# =============================================================================
INPUT_FOLDER = "kanka_to_md/kanka_jsons"  # Where your Kanka data is stored
OUTPUT_FILE = "worldbook.md"              # The markdown file that gets created


def fetch_entities(now, logger):
    """
    STEP 1: Fetch updated entities from Kanka API
    ---------------------------------------------
    This connects to your Kanka campaign and downloads any new or updated content.
    It only downloads what has changed since the last time you ran the script.
    """
    from kanka_function import fetch_and_save_updated_entities, save_last_run_time
    logger.info("🔄 Fetching updated entities from Kanka API...")
    try:
        fetch_and_save_updated_entities()
        logger.info("✅ Entity fetch completed successfully")
        save_last_run_time(now)
        logger.info(f"Saved last run time: {now.isoformat()} (UTC)")
    except Exception as e:
        logger.error(f"❌ Error during entity fetch: {e}")
        logger.warning("Continuing with existing data...")

def process_entities(INPUT_FOLDER, logger):
    """
    STEP 2: Process and organize all the entities
    ---------------------------------------------
    This takes all the raw data from Kanka and organizes it by type:
    - Characters (PCs, NPCs, monsters)
    - Locations (cities, dungeons, landmarks)
    - Events (sessions, historical events)
    - Organizations (guilds, factions, families)
    - Items (magic items, equipment)
    - Notes (lore, background information)
    - Races (playable races, monster types)
    """
    from io_utils import load_json_entries
    from entity_processing import (
        build_entity_map, get_type_id_sets, filter_entities_by_type, filter_entities_by_type_dict, build_character_id_to_entity_id
    )
    entries = load_json_entries(INPUT_FOLDER)
    logger.info(f"Loaded {len(entries)} entities.")
    
    # Get the different types of entities that Kanka uses
    type_id_sets = get_type_id_sets()
    
    # Filter entities by their type
    locations = filter_entities_by_type_dict(entries, type_id_sets['LOCATION_TYPE_IDS'])
    characters = filter_entities_by_type(entries, type_id_sets['CHARACTER_TYPE_IDS'])
    charlocations = filter_entities_by_type_dict(entries, type_id_sets['CHARACTER_TYPE_IDS'])
    events = filter_entities_by_type(entries, type_id_sets['EVENT_TYPE_IDS'])
    organizations = filter_entities_by_type(entries, type_id_sets['ORGANIZATION_TYPE_IDS'])
    items = filter_entities_by_type(entries, type_id_sets['ITEM_TYPE_IDS'])
    families = filter_entities_by_type(entries, type_id_sets['FAMILY_TYPE_IDS'])
    notes = filter_entities_by_type(entries, type_id_sets['NOTE_TYPE_IDS'])
    races = filter_entities_by_type(entries, type_id_sets['RACE_TYPE_IDS'])
    
    # Log how many of each type we found
    logger.info(f"Locations found: {len(locations)}")
    logger.info(f"Characters found: {len(characters)}")
    logger.info(f"Events found: {len(events)}")
    logger.info(f"Organizations found: {len(organizations)}")
    logger.info(f"Items found: {len(items)}")
    logger.info(f"Families found: {len(families)}")
    logger.info(f"Notes found: {len(notes)}")
    logger.info(f"Races found: {len(races)}")
    
    # Create maps to help with linking between entities
    entity_map = build_entity_map(entries)
    logger.info(f"Entity map built with {len(entity_map)} entities.")
    character_id_to_entity_id = build_character_id_to_entity_id(entries)
    
    return (locations, characters, charlocations, organizations, events, entity_map, character_id_to_entity_id, notes, items, families, races)

def generate_markdown(locations, characters, charlocations, organizations, events, entity_map, character_id_to_entity_id, notes, items, families, races, include_private, OUTPUT_FILE, logger):
    """
    STEP 3: Generate the markdown worldbook
    ---------------------------------------
    This creates a beautiful, organized markdown document with all your campaign content.
    It includes:
    - Table of contents with working links
    - Organized sections for each entity type
    - Cross-references between related content
    - Proper formatting and structure
    """
    from worldbook_generator import generate_worldbook
    from io_utils import save_markdown
    markdown = generate_worldbook(
        locations, characters, charlocations, organizations, events,
        entity_map, character_id_to_entity_id,
        notes, items, families, races,
        include_private=include_private
    )
    save_markdown(OUTPUT_FILE, markdown)
    logger.info(f"Worldbook generated: {OUTPUT_FILE}")

def convert_to_html(OUTPUT_FILE, logger):
    """
    STEP 4: Convert markdown to HTML with styling
    ---------------------------------------------
    This converts your markdown to a beautiful HTML file with:
    - Professional styling that matches Kanka's look
    - Working internal links
    - Responsive design
    - Ready for PDF conversion
    """
    try:
        output_html = "worldbook_styled.html"
        if not os.path.exists(OUTPUT_FILE):
            logger.error(f"❌ Markdown source file not found: {OUTPUT_FILE}")
        else:
            convert_markdown_file_to_html(OUTPUT_FILE, output_html)
            logger.info(f"🎉 HTML conversion completed: {output_html}")
        return output_html
    except Exception as e:
        logger.error(f"❌ Error during HTML conversion: {e}")
        return None

def convert_to_pdf(output_html, logger):
    """
    STEP 5: Convert HTML to PDF with working links
    ----------------------------------------------
    This creates a professional PDF with:
    - All internal links working (clickable)
    - External links that open in browser
    - Professional formatting
    - Ready for sharing or printing
    
    NOTE: This requires wkhtmltopdf to be installed on your system.
    On Windows, you can install it with: winget install wkhtmltopdf
    """
    try:
        output_pdf = "worldbook.pdf"
        if not output_html or not os.path.exists(output_html):
            logger.error(f"❌ HTML source file not found: {output_html}")
        else:
            convert_html_to_pdf(output_html, output_pdf, "Worldbook")
            logger.info(f"🎉 PDF conversion completed: {output_pdf}")
            return output_pdf
    except Exception as e:
        logger.error(f"❌ Error during PDF conversion: {e}")
        logger.info("💡 Make sure wkhtmltopdf is installed:")
        logger.info("   winget install wkhtmltopdf")
        return None

def upload_to_drive(output_pdf, logger):
    """
    STEP 6: Upload PDF to Google Drive (OPTIONAL)
    ---------------------------------------------
    This uploads your PDF to Google Drive and makes it shareable.
    
    TO DISABLE THIS STEP: Comment out the upload_to_drive() call in the main() function below
    
    Requirements:
    - Google Drive API credentials in google/client_secret.json
    - First time will open browser for authentication
    - Creates a shareable link that stays the same for future updates
    """
    try:
        logger.info("Uploading PDF to Google Drive via OAuth...")
        import subprocess
        result = subprocess.run([
            'python', 'kanka_to_md/publish_to_drive_oauth.py'
        ], capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
    except Exception as e:
        logger.error(f"❌ Error during Google Drive upload: {e}")

def main():
    """
    MAIN WORKFLOW - This runs all the steps in order
    ================================================
    
    You can easily comment out any step you don't want to use!
    For example, to skip Google Drive upload, comment out the last line.
    """
    start_time = time.time()
    
    # Load configuration (like whether to include private content)
    from io_utils import load_config
    config = load_config(os.path.join("kanka_to_md", "config.json"))
    include_private = config.get("include_private", False)
    logger.info(f"Loaded config: include_private = {include_private}")
    
    # Get current time for tracking when we last ran
    try:
        now = datetime.now(timezone.utc)
    except Exception as e:
        logger.error("datetime.now(timezone.utc) failed: %r", e)
        now = datetime.utcnow()
    
    # STEP 1: Fetch updated data from Kanka
    fetch_entities(now, logger)
    
    # STEP 2: Process and organize all entities
    (locations, characters, charlocations, organizations, events, entity_map, character_id_to_entity_id, notes, items, families, races) = process_entities(INPUT_FOLDER, logger)
    
    # STEP 3: Generate the markdown worldbook
    generate_markdown(locations, characters, charlocations, organizations, events, entity_map, character_id_to_entity_id, notes, items, families, races, include_private, OUTPUT_FILE, logger)
    
    # STEP 4: Convert to HTML with styling
    output_html = convert_to_html(OUTPUT_FILE, logger)
    
    # STEP 5: Convert to PDF with working links
    output_pdf = convert_to_pdf(output_html, logger)
    
    # STEP 6: Upload to Google Drive (OPTIONAL - COMMENT OUT TO DISABLE)
    # To disable Google Drive upload, comment out the next line:
    if output_pdf:
        upload_to_drive(output_pdf, logger)
    
    # Show how long everything took
    elapsed = time.time() - start_time
    logger.info(f"\nTotal elapsed time: {elapsed:.2f} seconds")


def cli():
    """
    COMMAND LINE INTERFACE
    ======================
    This allows you to run the script with custom options from the command line.
    """
    import argparse
    parser = argparse.ArgumentParser(description='RealmPress: Kanka to Markdown/HTML/PDF workflow')
    parser.add_argument('--config', default=os.path.join("kanka_to_md", "config.json"), help='Path to config file')
    parser.add_argument('--output', default="worldbook.md", help='Output markdown file')
    args = parser.parse_args()
    global INPUT_FOLDER, OUTPUT_FILE
    OUTPUT_FILE = args.output
    main()


if __name__ == '__main__':
    cli() 