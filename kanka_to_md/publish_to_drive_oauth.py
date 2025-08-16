"""
publish_to_drive_oauth.py
------------------------
Upload or update files on Google Drive using OAuth authentication.

Provides helpers to:
- Authenticate with Google Drive via OAuth
- Upload or update PDF files
- Set sharing permissions
- Store and reuse file IDs for consistent links
- Automatically handle expired tokens and re-authentication

Intended for use in the Kanka to Markdown/HTML/PDF workflow.
"""

import os
import pickle
import logging
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

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


def clear_expired_token():
    """Remove expired token file and inform user about re-authentication."""
    if os.path.exists(TOKEN_PATH):
        try:
            os.remove(TOKEN_PATH)
            logger.info("🗑️ Removed expired OAuth token.")
            logger.info("🔄 You will need to re-authenticate with Google on the next run.")
            return True
        except Exception as e:
            logger.error(f"Failed to remove expired token: {e}")
            return False
    return True


def get_drive_service():
    """
    Get Google Drive service with robust token handling.
    
    Returns:
        Google Drive service object
        
    Raises:
        Exception: If authentication fails completely
    """
    creds = None
    
    # Try to load existing token
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
            logger.info("📁 Loaded existing OAuth token.")
        except Exception as e:
            logger.warning(f"Failed to load existing token: {e}")
            clear_expired_token()
            creds = None
    
    # Check if token is valid
    if creds and creds.valid:
        logger.info("✅ OAuth token is valid.")
        return build('drive', 'v3', credentials=creds)
    
    # Try to refresh expired token
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("🔄 Refreshing expired OAuth token...")
            creds.refresh(Request())
            logger.info("✅ Token refreshed successfully.")
            
            # Save the refreshed token
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            
            return build('drive', 'v3', credentials=creds)
            
        except RefreshError as e:
            logger.warning(f"❌ Token refresh failed: {e}")
            logger.info("🔄 This usually means the refresh token has expired.")
            clear_expired_token()
        except Exception as e:
            logger.error(f"❌ Unexpected error during token refresh: {e}")
            clear_expired_token()
    
    # Need to get new token through OAuth flow
    logger.info("🔐 Starting OAuth authentication flow...")
    logger.info("📱 A browser window will open for Google authentication.")
    logger.info("   Please authorize the application when prompted.")
    
    try:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(f"OAuth credentials file not found: {CREDENTIALS_PATH}")
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the new token
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        
        logger.info("✅ OAuth authentication completed successfully!")
        logger.info("💾 New token saved for future use.")
        
        return build('drive', 'v3', credentials=creds)
        
    except Exception as e:
        logger.error(f"❌ OAuth authentication failed: {e}")
        logger.error("Please check your OAuth credentials and try again.")
        raise


def load_file_id():
    """Load the stored Google Drive file ID."""
    if os.path.exists(FILE_ID_PATH):
        try:
            with open(FILE_ID_PATH, 'r') as f:
                import json
                data = json.load(f)
                file_id = data.get('file_id')
                if file_id:
                    logger.info(f"📄 Found existing file ID: {file_id}")
                return file_id
        except Exception as e:
            logger.warning(f"Failed to load file ID: {e}")
    return None


def save_file_id(file_id):
    """Save the Google Drive file ID for future updates."""
    try:
        with open(FILE_ID_PATH, 'w') as f:
            import json
            json.dump({'file_id': file_id}, f)
        logger.info(f"💾 Saved file ID: {file_id}")
    except Exception as e:
        logger.error(f"Failed to save file ID: {e}")


def upload_or_update_file():
    """Upload or update file on Google Drive with error handling."""
    try:
        service = get_drive_service()
    except Exception as e:
        logger.error(f"❌ Failed to authenticate with Google Drive: {e}")
        logger.error("Please check your OAuth credentials and try again.")
        return False
    
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

    # Try to update existing file
    if file_id:
        try:
            logger.info(f"🔄 Updating existing file on Drive (ID: {file_id})...")
            updated_file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            logger.info("✅ File updated successfully.")
            file_id = updated_file['id']
        except Exception as e:
            logger.warning(f"⚠️ Failed to update file: {e}")
            logger.info("🔄 Will try to upload as new file.")
            file_id = None

    # Upload new file if update failed or no existing file
    if not file_id:
        try:
            logger.info("📤 Uploading new file to Drive...")
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            file_id = uploaded_file['id']
            logger.info("✅ File uploaded successfully.")
            save_file_id(file_id)
        except Exception as e:
            logger.error(f"❌ Failed to upload file: {e}")
            return False

    # Set sharing permissions
    if SHARE_WITH_ANYONE:
        try:
            logger.info("🔗 Setting sharing permissions (anyone with link can view)...")
            permission = {
                'type': 'anyone',
                'role': 'reader',
            }
            service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id'
            ).execute()
            logger.info("✅ Sharing permissions set.")
        except Exception as e:
            logger.warning(f"⚠️ Failed to set sharing permissions: {e}")

    # Get and display file links
    try:
        file = service.files().get(fileId=file_id, fields='webViewLink, webContentLink').execute()
        logger.info("🎉 Upload completed successfully!")
        logger.info(f"📄 File is available at: {file['webViewLink']}")
        logger.info(f"⬇️ Direct download link: {file['webContentLink']}")
        logger.info("💡 Share this link. Future updates will keep the same link!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to get file links: {e}")
        return False


def main():
    """Main function with comprehensive error handling."""
    logger.info("🚀 Starting Google Drive upload process...")
    
    # Check if file exists
    if not os.path.exists(FILE_PATH):
        logger.error(f"❌ File not found: {FILE_PATH}")
        logger.error("Please ensure the file exists before running this script.")
        return False
    
    # Check if OAuth credentials exist
    if not os.path.exists(CREDENTIALS_PATH):
        logger.error(f"❌ OAuth client credentials not found: {CREDENTIALS_PATH}")
        logger.error("Please set up your Google OAuth credentials first.")
        return False
    
    # Perform upload
    try:
        success = upload_or_update_file()
        if success:
            logger.info("🎉 Google Drive upload workflow completed successfully!")
        else:
            logger.error("❌ Google Drive upload workflow failed.")
        return success
    except KeyboardInterrupt:
        logger.info("⏹️ Upload cancelled by user.")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during upload: {e}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 