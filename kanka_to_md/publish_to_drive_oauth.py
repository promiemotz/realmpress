"""
publish_to_drive_oauth.py
------------------------
Upload or update files on Google Drive using OAuth authentication.

Provides helpers to:
- Authenticate with Google Drive via OAuth
- Upload or update PDF files
- Set sharing permissions
- Store and reuse file IDs for consistent links

Intended for use in the Kanka to Markdown/HTML/PDF workflow.
"""

import os
import pickle
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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

# CONFIGURABLES
FILE_PATH = 'worldbook.pdf'  # File to upload
FILE_ID_PATH = 'drive_file_id_oauth.json'  # Where to store the Google Drive file ID
CREDENTIALS_PATH = 'google/client_secret.json'  # OAuth client credentials
TOKEN_PATH = 'token.pickle'  # Where to store the user's access/refresh token
DRIVE_FOLDER_ID = '1tVLcOG9NJJsP4vkBcrCYEG6EqIHwVcDB'  # Your folder ID
SHARE_WITH_ANYONE = True

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)


def load_file_id():
    if os.path.exists(FILE_ID_PATH):
        with open(FILE_ID_PATH, 'r') as f:
            import json
            data = json.load(f)
            return data.get('file_id')
    return None


def save_file_id(file_id):
    with open(FILE_ID_PATH, 'w') as f:
        import json
        json.dump({'file_id': file_id}, f)


def upload_or_update_file():
    service = get_drive_service()
    file_id = load_file_id()
    file_metadata = {
        'name': os.path.basename(FILE_PATH),
        'parents': [DRIVE_FOLDER_ID]
    }
    if FILE_PATH.endswith('.pdf'):
        mimetype = 'application/pdf'
    else:
        mimetype = 'application/octet-stream'
    media = MediaFileUpload(FILE_PATH, mimetype=mimetype, resumable=True)

    if file_id:
        try:
            logger.info(f"Updating existing file on Drive (ID: {file_id})...")
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            logger.info("File updated.")
            file_id = updated_file['id']
        except Exception as e:
            logger.warning(f"Failed to update file: {e}. Will try to upload as new file.")
            file_id = None

    if not file_id:
        logger.info("Uploading new file to Drive...")
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()
        file_id = uploaded_file['id']
        logger.info("File uploaded.")
        save_file_id(file_id)

    if SHARE_WITH_ANYONE:
        logger.info("Setting sharing permissions (anyone with link can view)...")
        permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()

    file = service.files().get(fileId=file_id, fields='webViewLink, webContentLink').execute()
    logger.info(f"\nFile is available at: {file['webViewLink']}")
    logger.info(f"Direct download link: {file['webContentLink']}")
    logger.info("Share this link. Future updates will keep the same link!")


def main():
    if not os.path.exists(FILE_PATH):
        logger.error(f"File not found: {FILE_PATH}")
    elif not os.path.exists(CREDENTIALS_PATH):
        logger.error(f"OAuth client credentials not found: {CREDENTIALS_PATH}")
    else:
        upload_or_update_file()


if __name__ == '__main__':
    main() 