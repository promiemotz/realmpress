"""
kanka_function.py
-----------------
Core functions for interacting with the Kanka API and managing entity data.

Provides helpers to:
- Load and save configuration and run state
- Fetch and update entities from Kanka (with retry logic)
- Download and organize entity data for downstream processing

Intended for use in the Kanka to Markdown/HTML/PDF workflow.
"""

import os
import time
import zipfile
import requests
import json
import logging
from datetime import datetime, timezone
from markdown_utils import create_anchor_label

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
LAST_RUN_PATH = os.path.join(os.path.dirname(__file__), 'last_run.json')

# Logging setup (if not already set by main)
if not logging.getLogger().hasHandlers():
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


def load_config():
    """Load API configuration from config.json"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_last_run_time(dt: datetime):
    """Save the current run time to last_run.json for future comparisons"""
    logger.info(f"Saving last run time to: {LAST_RUN_PATH}")
    try:
        with open(LAST_RUN_PATH, 'w', encoding='utf-8') as f:
            json.dump({'last_run': dt.isoformat()}, f)
        logger.info("last_run.json updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update last_run.json: {e}")


def load_last_run_time():
    """Load the last run time from last_run.json, make it timezone-aware"""
    if not os.path.exists(LAST_RUN_PATH):
        return None
    with open(LAST_RUN_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        dt = datetime.fromisoformat(data['last_run'])
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt


def download_kanka_export():
    """
    DEPRECATED: This function was for downloading full campaign exports as ZIP files.
    Not used in the current entity-by-entity approach.
    """
    config = load_config()
    api_token = config['api_token']
    campaign_id = config['campaign_id']
    export_dir = config['export_dir']
    poll_interval = config.get('poll_interval', 5)

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json',
    }

    logger.info(f"Triggering export for campaign {campaign_id}...")
    export_url = f'https://api.kanka.io/1.0/campaigns/{campaign_id}/exports'
    resp = requests.post(export_url, headers=headers)
    resp.raise_for_status()
    export = resp.json()['data']
    export_id = export['id']
    logger.info(f"Export triggered (Export ID: {export_id}). Waiting for completion...")

    status_url = f'https://api.kanka.io/1.0/campaigns/{campaign_id}/exports/{export_id}'
    while True:
        status_resp = requests.get(status_url, headers=headers)
        status_resp.raise_for_status()
        export_status = status_resp.json()['data']
        status = export_status['status']
        logger.info(f"Current export status: {status}")
        if status == 'finished':
            break
        elif status == 'failed':
            raise Exception("Export failed.")
        time.sleep(poll_interval)

    download_url = export_status.get('url')
    if not download_url:
        raise Exception("Export completed but no download URL provided.")

    logger.info(f"Downloading export from: {download_url}")
    response = requests.get(download_url)
    response.raise_for_status()

    os.makedirs(export_dir, exist_ok=True)
    zip_path = os.path.join(export_dir, f'kanka_export_{campaign_id}.zip')
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    logger.info(f"Export downloaded to: {zip_path}")

    logger.info(f"Extracting ZIP to: {export_dir}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(export_dir)
    logger.info(f"Extraction complete.")

    os.remove(zip_path)
    logger.info(f"Cleaned up ZIP file.")

    now = datetime.utcnow()
    save_last_run_time(now)
    logger.info(f"Saved last run time: {now.isoformat()} (UTC)")


type_endpoint_map = {
    'location': 'locations',
    'character': 'characters',
    'family': 'families',
    'organisation': 'organisations',
    'item': 'items',
    'note': 'notes',
    'event': 'events',
    'calendar': 'calendars',
    'timeline': 'timelines',
    'creature': 'creatures',
    'race': 'races',
    'quest': 'quests',
    'map': 'maps',
}


def fetch_with_retries(url, headers, max_retries=6, delay=20):
    """
    Fetch data from URL with retry logic to handle Kanka's API rate limits.
    Args:
        url: The URL to fetch
        headers: Request headers (including API token)
        max_retries: Maximum number of retry attempts (default: 6)
        delay: Seconds to wait between retries (default: 20)
    Returns:
        requests.Response object if successful, None if all retries failed
    """
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return resp
            else:
                logger.warning(f"Attempt {attempt}: Failed to fetch {url} (status {resp.status_code})")
        except Exception as e:
            logger.warning(f"Attempt {attempt}: Exception while fetching {url}: {e}")
        if attempt < max_retries:
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    logger.error(f"All {max_retries} attempts failed for {url}")
    return None


def fetch_all_entities(base_url, headers, per_page=100):
    """Fetch all entities from the Kanka API, handling pagination."""
    page = 1
    all_entities = []
    while True:
        params = {'page': page, 'limit': per_page}
        resp = requests.get(base_url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        entities = data.get('data', [])
        if not entities:
            break
        all_entities.extend(entities)
        if not data.get('links', {}).get('next'):
            break
        page += 1
    return all_entities


def filter_updated_entities(entities, last_run):
    """Yield entities that have been updated since last_run."""
    for entity in entities:
        updated_at = entity.get('updated_at')
        if updated_at and last_run:
            updated_at_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            if updated_at_dt <= last_run:
                continue
        yield entity


def fetch_full_entity_data(entity, campaign_id, headers):
    """Fetch the full child data for an entity from the type-specific endpoint."""
    entity_type = entity.get('type')
    child_id = entity.get('child_id')
    if not entity_type or not child_id:
        return None, None, None
    endpoint = type_endpoint_map.get(entity_type)
    if not endpoint:
        logger.warning(f"Unknown entity type: {entity_type}, skipping entity {entity['id']}")
        return None, None, None
    child_url = f'https://api.kanka.io/1.0/campaigns/{campaign_id}/{endpoint}/{child_id}'
    child_resp = fetch_with_retries(child_url, headers)
    if not child_resp or child_resp.status_code != 200:
        logger.warning(f"Failed to fetch {entity_type} {child_id} for entity {entity['id']} after retries.")
        return None, None, None
    child_data = child_resp.json().get('data')
    return endpoint, child_id, child_data


def save_raw_child_data(raw_out_dir, child_id, child_data):
    os.makedirs(raw_out_dir, exist_ok=True)
    raw_out_path = os.path.join(raw_out_dir, f'{child_id}.json')
    with open(raw_out_path, 'w', encoding='utf-8') as f:
        json.dump(child_data, f, ensure_ascii=False, indent=2)


def save_combined_entity_data(combined_out_dir, entity, child_data):
    os.makedirs(combined_out_dir, exist_ok=True)
    entity_name = entity.get('name', f'entity_{entity["id"]}')
    safe_name = create_anchor_label(entity_name)
    combined_out_path = os.path.join(combined_out_dir, f'{safe_name}.json')
    combined_data = child_data.copy()
    combined_data['entity'] = entity
    with open(combined_out_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)


def save_all_entity_metadata(entities_dir, all_entities):
    os.makedirs(entities_dir, exist_ok=True)
    for entity in all_entities:
        entity_id = entity.get('id')
        if entity_id:
            out_path = os.path.join(entities_dir, f'{entity_id}.json')
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(entity, f, ensure_ascii=False, indent=2)


def fetch_and_save_updated_entities():
    """
    MAIN FUNCTION: Fetch all entities from Kanka, check which ones were updated since last run,
    and download their full data to local JSON files.
    """
    config = load_config()
    api_token = config['api_token']
    campaign_id = config['campaign_id']
    base_url = f'https://api.kanka.io/1.0/campaigns/{campaign_id}/entities'
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Accept': 'application/json',
    }
    last_run = load_last_run_time()
    logger.info(f"Last run time: {last_run}")
    logger.info("Fetching entities that were updated since last run...")
    kanka_raw_jsons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kanka_raw_jsons')
    kanka_jsons_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons')
    all_entities = fetch_all_entities(base_url, headers)
    total_saved = 0
    for entity in filter_updated_entities(all_entities, last_run):
        endpoint, child_id, child_data = fetch_full_entity_data(entity, campaign_id, headers)
        if not endpoint or not child_id or not child_data:
            continue
        raw_out_dir = os.path.join(kanka_raw_jsons_dir, endpoint)
        save_raw_child_data(raw_out_dir, child_id, child_data)
        combined_out_dir = os.path.join(kanka_jsons_dir, endpoint)
        save_combined_entity_data(combined_out_dir, entity, child_data)
        total_saved += 1
    logger.info(f"Saving {len(all_entities)} entity metadata files...")
    entities_dir = os.path.join(kanka_raw_jsons_dir, 'entities')
    save_all_entity_metadata(entities_dir, all_entities)
    logger.info(f"Done! Total updated entities saved: {total_saved}")
    logger.info(f"Files saved in: {os.path.join(kanka_raw_jsons_dir, '*/')}")
    logger.info(f"Combined data saved in: {os.path.join(kanka_jsons_dir, '*/')}") 