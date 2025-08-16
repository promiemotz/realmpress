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
from .io_utils import load_json_entries, save_markdown, load_config
from .entity_processing import (
    build_entity_map, get_type_id_sets, filter_entities_by_type, filter_entities_by_type_dict, build_character_id_to_entity_id
)
from .worldbook_generator import generate_worldbook
from .kanka_function import fetch_and_save_updated_entities, save_last_run_time
from .html_converter import convert_markdown_file_to_html
from .pdf_converter_wkhtmltopdf import convert_html_to_pdf
import json # Added missing import for json

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
# Use absolute path based on script location to avoid path issues
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(SCRIPT_DIR, "kanka_jsons")  # Where your Kanka data is stored
OUTPUT_FILE = "worldbook.md"              # The markdown file that gets created


def update_input_folder(new_path):
    """Update the global INPUT_FOLDER variable."""
    global INPUT_FOLDER
    INPUT_FOLDER = new_path
    logger.info(f"🔄 Global INPUT_FOLDER updated to: {INPUT_FOLDER}")


def fetch_entities(now, logger):
    """
    STEP 1: Fetch updated entities from Kanka API
    ---------------------------------------------
    This connects to your Kanka campaign and downloads any new or updated content.
    It only downloads what has changed since the last time you ran the script.
    """
    from .kanka_function import fetch_and_save_updated_entities, save_last_run_time
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
    from .io_utils import load_json_entries, save_markdown, load_config
    from .entity_processing import (
        build_entity_map, get_type_id_sets, filter_entities_by_type, filter_entities_by_type_dict, build_character_id_to_entity_id
    )
    
    # Add detailed path logging
    import os
    current_dir = os.getcwd()
    logger.info(f"🔍 PATH DIAGNOSTICS:")
    logger.info(f"   Current working directory: {current_dir}")
    logger.info(f"   Input folder (as passed): {INPUT_FOLDER}")
    logger.info(f"   Input folder type: {'absolute' if os.path.isabs(INPUT_FOLDER) else 'relative'}")
    
    # Check if INPUT_FOLDER is absolute or relative
    if os.path.isabs(INPUT_FOLDER):
        absolute_input_folder = INPUT_FOLDER
        logger.info(f"   Input folder is already absolute: {absolute_input_folder}")
    else:
        absolute_input_folder = os.path.abspath(INPUT_FOLDER)
        logger.info(f"   Input folder resolved to absolute: {absolute_input_folder}")
    
    # Check if directory exists
    if os.path.exists(absolute_input_folder):
        logger.info(f"   ✅ Input folder exists: {absolute_input_folder}")
        # Check if it's actually a directory
        if os.path.isdir(absolute_input_folder):
            logger.info(f"   ✅ Input folder is a directory")
            # List contents of the directory
            try:
                contents = os.listdir(absolute_input_folder)
                logger.info(f"   📁 Directory contents ({len(contents)} items): {contents[:10]}{'...' if len(contents) > 10 else ''}")
                
                # Check for specific expected subdirectories
                expected_dirs = ['characters', 'locations', 'events', 'organizations', 'items', 'families', 'notes', 'races']
                found_dirs = [d for d in contents if os.path.isdir(os.path.join(absolute_input_folder, d))]
                logger.info(f"   📂 Found subdirectories: {found_dirs}")
                
                missing_dirs = [d for d in expected_dirs if d not in found_dirs]
                if missing_dirs:
                    logger.warning(f"   ⚠️ Missing expected subdirectories: {missing_dirs}")
                
            except Exception as e:
                logger.warning(f"   ⚠️ Could not list directory contents: {e}")
        else:
            logger.error(f"   ❌ Input folder exists but is not a directory!")
            return {}
    else:
        logger.error(f"   ❌ Input folder does not exist: {absolute_input_folder}")
        logger.error(f"   ❌ This is likely why no entities are being loaded!")
        
        # Try to find similar directories
        parent_dir = os.path.dirname(absolute_input_folder)
        if os.path.exists(parent_dir):
            logger.info(f"   🔍 Parent directory exists: {parent_dir}")
            try:
                parent_contents = os.listdir(parent_dir)
                logger.info(f"   📁 Parent directory contents: {parent_contents}")
                
                # Look for directories that might contain kanka data
                potential_dirs = [d for d in parent_contents if 'kanka' in d.lower() or 'json' in d.lower()]
                if potential_dirs:
                    logger.warning(f"   💡 Potential kanka directories found: {potential_dirs}")
            except Exception as e:
                logger.warning(f"   ⚠️ Could not list parent directory contents: {e}")
        else:
            logger.error(f"   ❌ Parent directory also does not exist: {parent_dir}")
        
        return {}
    
    # Check permissions
    try:
        test_file = os.path.join(absolute_input_folder, 'test_permissions.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info(f"   ✅ Directory is writable")
    except Exception as e:
        logger.warning(f"   ⚠️ Directory permission issue: {e}")
    
    logger.info(f"🔍 END PATH DIAGNOSTICS")
    
    entries = load_json_entries(absolute_input_folder)
    logger.info(f"Loaded {len(entries)} entities.")
    
    # AUTO-RETRY LOGIC: If no entities loaded, try to fix the issue
    if len(entries) == 0:
        logger.warning("⚠️ No entities loaded! Attempting automatic fix...")
        
        # Try to find any JSON files
        json_count = 0
        json_files = []
        for root, dirs, files in os.walk(absolute_input_folder):
            for file in files:
                if file.endswith('.json'):
                    json_count += 1
                    json_files.append(os.path.join(root, file))
        logger.info(f"📊 Found {json_count} JSON files in directory tree")
        
        if json_count > 0:
            logger.info(f"📄 Sample JSON files: {json_files[:5]}")
            
            # Try to read a sample file
            if json_files:
                sample_file = json_files[0]
                try:
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        sample_data = json.load(f)
                    logger.info(f"📄 Sample file structure: {type(sample_data)}")
                    if isinstance(sample_data, dict):
                        logger.info(f"📄 Sample file keys: {list(sample_data.keys())[:10]}")
                except Exception as e:
                    logger.warning(f"📄 Could not read sample file {sample_file}: {e}")
        
        # AUTO-FIX: Try alternative paths
        logger.info("🔄 Attempting automatic path correction...")
        
        # Try common alternative paths
        alternative_paths = [
            os.path.join(current_dir, "kanka_jsons"),
            os.path.join(current_dir, "kanka_to_md", "kanka_jsons"),
            os.path.join(os.path.dirname(current_dir), "kanka_to_md", "kanka_jsons"),
            os.path.join(current_dir, "..", "kanka_to_md", "kanka_jsons"),
            os.path.join(current_dir, "data", "kanka_jsons"),
        ]
        
        for alt_path in alternative_paths:
            alt_path_abs = os.path.abspath(alt_path)
            logger.info(f"🔄 Trying alternative path: {alt_path_abs}")
            
            if os.path.exists(alt_path_abs) and os.path.isdir(alt_path_abs):
                logger.info(f"✅ Found alternative directory: {alt_path_abs}")
                
                # Try loading from this alternative path
                try:
                    alt_entries = load_json_entries(alt_path_abs)
                    if len(alt_entries) > 0:
                        logger.info(f"🎉 Success! Loaded {len(alt_entries)} entities from alternative path")
                        logger.info(f"🔄 Using alternative path: {alt_path_abs}")
                        
                        # Update global INPUT_FOLDER for future runs
                        update_input_folder(alt_path_abs)
                        
                        # Use the alternative entries
                        entries = alt_entries
                        absolute_input_folder = alt_path_abs
                        break
                    else:
                        logger.info(f"⚠️ Alternative path exists but has no entities")
                except Exception as e:
                    logger.warning(f"⚠️ Error loading from alternative path: {e}")
            else:
                logger.info(f"❌ Alternative path does not exist: {alt_path_abs}")
        
        # If still no entities, try to trigger a fresh data fetch
        if len(entries) == 0:
            logger.warning("⚠️ Still no entities found. Attempting fresh data fetch...")
            try:
                from .kanka_function import fetch_and_save_updated_entities
                logger.info("🔄 Forcing fresh entity fetch...")
                fetch_and_save_updated_entities()
                
                # Try loading again after fresh fetch
                entries = load_json_entries(absolute_input_folder)
                logger.info(f"🔄 After fresh fetch: Loaded {len(entries)} entities")
                
                if len(entries) == 0:
                    logger.error("❌ Still no entities after fresh fetch. Manual intervention required.")
                    logger.error("❌ Please check:")
                    logger.error("   1. Kanka API configuration")
                    logger.error("   2. Network connectivity")
                    logger.error("   3. Campaign ID and API token")
                    logger.error("   4. Directory permissions")
                else:
                    logger.info("🎉 Fresh fetch successful!")
                    
            except Exception as e:
                logger.error(f"❌ Error during fresh fetch: {e}")
    
    type_id_sets = get_type_id_sets()
    
    # Define labels for each entity type
    type_labels = {
        'locations': 'Locations',
        'characters': 'Characters', 
        'charlocations': 'Character Locations',
        'organizations': 'Organizations',
        'events': 'Events',
        'notes': 'Notes',
        'items': 'Items',
        'families': 'Families',
        'races': 'Races',
        'journals': 'Journals',
        'tags': 'Tags',
        'quests': 'Quests',
        'maps': 'Maps',
        'timelines': 'Timelines',
        'calendars': 'Calendars',
    }
    
    # Use a dict to store all types
    entities_by_type = {}
    for key, type_ids in type_id_sets.items():
        if key.endswith('_DICT_IDS'):
            continue
        if key == 'LOCATION_TYPE_IDS':
            entities_by_type['locations'] = filter_entities_by_type_dict(entries, type_ids)
            entities_by_type['charlocations'] = filter_entities_by_type_dict(entries, type_ids)
        elif key == 'CHARACTER_TYPE_IDS':
            entities_by_type['characters'] = filter_entities_by_type(entries, type_ids)
        elif key == 'ORGANIZATION_TYPE_IDS':
            entities_by_type['organizations'] = filter_entities_by_type(entries, type_ids)
        elif key == 'EVENT_TYPE_IDS':
            entities_by_type['events'] = filter_entities_by_type(entries, type_ids)
        elif key == 'NOTE_TYPE_IDS':
            entities_by_type['notes'] = filter_entities_by_type(entries, type_ids)
        elif key == 'ITEM_TYPE_IDS':
            entities_by_type['items'] = filter_entities_by_type(entries, type_ids)
        elif key == 'FAMILY_TYPE_IDS':
            entities_by_type['families'] = filter_entities_by_type(entries, type_ids)
        elif key == 'RACE_TYPE_IDS':
            entities_by_type['races'] = filter_entities_by_type(entries, type_ids)
        elif key == 'JOURNAL_TYPE_IDS':
            entities_by_type['journals'] = filter_entities_by_type(entries, type_ids)
        elif key == 'TAG_TYPE_IDS':
            entities_by_type['tags'] = filter_entities_by_type(entries, type_ids)
        elif key == 'QUEST_TYPE_IDS':
            entities_by_type['quests'] = filter_entities_by_type(entries, type_ids)
        elif key == 'MAP_TYPE_IDS':
            entities_by_type['maps'] = filter_entities_by_type(entries, type_ids)
        elif key == 'TIMELINE_TYPE_IDS':
            entities_by_type['timelines'] = filter_entities_by_type(entries, type_ids)
        elif key == 'CALENDAR_TYPE_IDS':
            entities_by_type['calendars'] = filter_entities_by_type(entries, type_ids)
        else:
            # Handle any other types generically
            type_name = key.replace('_TYPE_IDS', '').lower()
            entities_by_type[type_name] = filter_entities_by_type(entries, type_ids)
    
    # Log counts for each type
    for entity_type, entities in entities_by_type.items():
        label = type_labels.get(entity_type, entity_type.title())
        if isinstance(entities, dict):
            count = len(entities)
        else:
            count = len(entities)
        logger.info(f"{label} found: {count}")
    
    # Load campaign data if available
    campaign_file = os.path.join(absolute_input_folder, 'campaign.json')
    campaign_data = {}
    if os.path.exists(campaign_file):
        try:
            with open(campaign_file, 'r', encoding='utf-8') as f:
                campaign_data = json.load(f)
            logger.info(f"Campaign data loaded: {campaign_data.get('name', 'Unknown Campaign')}")
        except Exception as e:
            logger.warning(f"Could not load campaign.json: {e}")
    
    # Build entity map and character mappings
    entity_map = build_entity_map(entries)
    character_id_to_entity_id = build_character_id_to_entity_id(entries)
    
    # Add these to the entities dict
    entities_by_type['campaign'] = campaign_data
    entities_by_type['entity_map'] = entity_map
    entities_by_type['character_id_to_entity_id'] = character_id_to_entity_id
    
    logger.info(f"Entity map built with {len(entity_map)} entities.")
    
    return entities_by_type

def generate_markdown(entities, include_private, OUTPUT_FILE, logger, language='en', include_posts=True):
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
    from .worldbook_generator import generate_worldbook
    from .io_utils import save_markdown
    markdown = generate_worldbook(entities, include_private=include_private, include_posts=include_posts, language=language)
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

def main_with_config(config=None):
    """
    MAIN WORKFLOW - This runs all the steps in order
    ================================================
    
    You can easily comment out any step you don't want to use!
    For example, to skip Google Drive upload, comment out the last line.
    """
    start_time = time.time()
    
    # Load configuration (like whether to include private content)
    from .io_utils import load_config
    if config is None:
        config = load_config(os.path.join("kanka_to_md", "config.json"))
    include_private = config.get("include_private", False)
    include_posts = config.get("include_posts", True)
    language = config.get("language", "en")
    logger.info(f"Loaded config: include_private = {include_private}, include_posts = {include_posts}, language = {language}")
    
    # Get current time for tracking when we last ran
    try:
        now = datetime.now(timezone.utc)
    except Exception as e:
        logger.error("datetime.now(timezone.utc) failed: %r", e)
        now = datetime.utcnow()
    
    # Track success/failure of each step
    step_results = {}
    
    # STEP 1: Fetch updated data from Kanka
    try:
        fetch_entities(now, logger)
        step_results['fetch_entities'] = 'SUCCESS'
    except Exception as e:
        logger.error(f"❌ Error during entity fetch: {e}")
        step_results['fetch_entities'] = f'FAILED: {e}'
    
    # STEP 2: Process and organize all entities
    try:
        entities = process_entities(INPUT_FOLDER, logger)
        step_results['process_entities'] = f'SUCCESS: {sum(len(v) if isinstance(v, (list, dict)) else 0 for k, v in entities.items() if k not in ["entity_map", "character_id_to_entity_id"])} entities processed'
    except Exception as e:
        logger.error(f"❌ Error during entity processing: {e}")
        step_results['process_entities'] = f'FAILED: {e}'
        entities = {}
    
    # STEP 3: Generate the markdown worldbook
    try:
        generate_markdown(entities, include_private, OUTPUT_FILE, logger, language, include_posts)
        step_results['generate_markdown'] = 'SUCCESS'
    except Exception as e:
        logger.error(f"❌ Error during markdown generation: {e}")
        step_results['generate_markdown'] = f'FAILED: {e}'
    
    # STEP 4: Convert to HTML with styling
    try:
        output_html = convert_to_html(OUTPUT_FILE, logger)
        step_results['convert_to_html'] = f'SUCCESS: {output_html}'
    except Exception as e:
        logger.error(f"❌ Error during HTML conversion: {e}")
        step_results['convert_to_html'] = f'FAILED: {e}'
        output_html = None
    
    # STEP 5: Convert to PDF with working links
    try:
        output_pdf = convert_to_pdf(output_html, logger)
        step_results['convert_to_pdf'] = f'SUCCESS: {output_pdf}'
    except Exception as e:
        logger.error(f"❌ Error during PDF conversion: {e}")
        step_results['convert_to_pdf'] = f'FAILED: {e}'
        output_pdf = None
    
    # STEP 6: Upload to Google Drive (OPTIONAL - COMMENT OUT TO DISABLE)
    # To disable Google Drive upload, comment out the next line:
    if output_pdf:
        try:
            upload_to_drive(output_pdf, logger)
            step_results['upload_to_drive'] = 'SUCCESS'
        except Exception as e:
            logger.error(f"❌ Error during Google Drive upload: {e}")
            step_results['upload_to_drive'] = f'FAILED: {e}'
    else:
        step_results['upload_to_drive'] = 'SKIPPED: No PDF generated'
    
    # Show how long everything took
    elapsed = time.time() - start_time
    logger.info(f"\nTotal elapsed time: {elapsed:.2f} seconds")
    
    # Print summary
    logger.info(f"\n📊 WORKFLOW SUMMARY:")
    logger.info(f"   {'='*50}")
    for step, result in step_results.items():
        status_icon = "✅" if result.startswith('SUCCESS') else "❌" if result.startswith('FAILED') else "⚠️"
        logger.info(f"   {status_icon} {step.replace('_', ' ').title()}: {result}")
    logger.info(f"   {'='*50}")
    
    # Check for critical issues
    failed_steps = [step for step, result in step_results.items() if result.startswith('FAILED')]
    if failed_steps:
        logger.warning(f"⚠️ Critical issues detected in steps: {failed_steps}")
        logger.warning(f"⚠️ Check the logs above for detailed error information")
    else:
        logger.info(f"🎉 All steps completed successfully!")


def main():
    """
    MAIN WORKFLOW - This runs all the steps in order
    ================================================
    
    You can easily comment out any step you don't want to use!
    For example, to skip Google Drive upload, comment out the last line.
    """
    main_with_config()


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
    parser.add_argument('--language', choices=['hu', 'en'], help='Language for chapter titles (hu=Hungarian, en=English)')
    args = parser.parse_args()
    global INPUT_FOLDER, OUTPUT_FILE
    OUTPUT_FILE = args.output
    
    # Load config
    from .io_utils import load_config
    config = load_config(args.config)
    
    # Only override language if explicitly provided via CLI
    if args.language is not None:
        config['language'] = args.language
    
    # Call main with the updated config
    main_with_config(config)


if __name__ == '__main__':
    cli() 