"""
oauth_token_manager.py
---------------------
Utility script for managing Google OAuth tokens.

This script helps you:
- Test OAuth authentication
- Clear expired tokens
- Re-authenticate when tokens expire
- Check token status

Usage:
    python oauth_token_manager.py [command]

Commands:
    test     - Test current token or authenticate
    clear    - Clear expired token
    status   - Check token status
    help     - Show this help
"""

import os
import pickle
import logging
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Configuration
CREDENTIALS_PATH = 'google/client_secret.json'
TOKEN_PATH = 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def check_token_status():
    """Check the status of the current OAuth token."""
    if not os.path.exists(TOKEN_PATH):
        logger.info("❌ No OAuth token found.")
        return False
    
    try:
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
        
        if creds.valid:
            logger.info("✅ OAuth token is valid and ready to use.")
            return True
        elif creds.expired and creds.refresh_token:
            logger.info("⚠️ OAuth token is expired but has refresh token.")
            return "expired"
        else:
            logger.info("❌ OAuth token is invalid or missing refresh token.")
            return False
    except Exception as e:
        logger.error(f"❌ Error reading token: {e}")
        return False


def clear_token():
    """Remove the OAuth token file."""
    if os.path.exists(TOKEN_PATH):
        try:
            os.remove(TOKEN_PATH)
            logger.info("🗑️ OAuth token removed successfully.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to remove token: {e}")
            return False
    else:
        logger.info("ℹ️ No token file found to remove.")
        return True


def authenticate():
    """Perform OAuth authentication flow."""
    if not os.path.exists(CREDENTIALS_PATH):
        logger.error(f"❌ OAuth credentials not found: {CREDENTIALS_PATH}")
        logger.error("Please ensure you have set up your Google OAuth credentials.")
        return False
    
    try:
        logger.info("🔐 Starting OAuth authentication...")
        logger.info("📱 A browser window will open for Google authentication.")
        logger.info("   Please authorize the application when prompted.")
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the new token
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
        
        logger.info("✅ OAuth authentication completed successfully!")
        logger.info("💾 New token saved for future use.")
        return True
        
    except Exception as e:
        logger.error(f"❌ OAuth authentication failed: {e}")
        return False


def test_token():
    """Test the current token or authenticate if needed."""
    status = check_token_status()
    
    if status is True:
        logger.info("✅ Token is valid - no action needed.")
        return True
    elif status == "expired":
        logger.info("🔄 Attempting to refresh expired token...")
        try:
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
            
            creds.refresh(Request())
            
            # Save the refreshed token
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
            
            logger.info("✅ Token refreshed successfully!")
            return True
            
        except RefreshError as e:
            logger.warning(f"❌ Token refresh failed: {e}")
            logger.info("🔄 This usually means the refresh token has expired.")
            logger.info("🔄 Clearing old token and starting fresh authentication...")
            clear_token()
            return authenticate()
        except Exception as e:
            logger.error(f"❌ Unexpected error during token refresh: {e}")
            clear_token()
            return authenticate()
    else:
        logger.info("🔄 No valid token found. Starting authentication...")
        return authenticate()


def show_help():
    """Show help information."""
    print(__doc__)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        logger.error("❌ No command specified.")
        show_help()
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "test":
        success = test_token()
        return 0 if success else 1
    elif command == "clear":
        success = clear_token()
        return 0 if success else 1
    elif command == "status":
        status = check_token_status()
        if status is True:
            return 0
        elif status == "expired":
            return 1
        else:
            return 2
    elif command == "help":
        show_help()
        return 0
    else:
        logger.error(f"❌ Unknown command: {command}")
        show_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
