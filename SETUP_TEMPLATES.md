# Setup Templates Guide

This guide explains how to set up RealmPress using the template files provided.

## Template Files Overview

The following template files are provided to help you configure RealmPress:

- `kanka_to_md/config.template.json` - Kanka API configuration
- `kanka_to_md/last_run.template.json` - Last run timestamp tracking
- `drive_file_id_oauth.template.json` - Google Drive file ID
- `google/client_secret.template.json` - Google OAuth credentials
- `google/service_account.template.json` - Google service account credentials

## Step-by-Step Setup

### 1. Kanka Configuration

**File:** `kanka_to_md/config.template.json`

1. Copy the template file:
   ```bash
   cp kanka_to_md/config.template.json kanka_to_md/config.json
   ```

2. Edit `kanka_to_md/config.json` and replace the placeholders:
   ```json
   {
     "include_private": false,
     "api_token": "your-actual-kanka-api-token",
     "campaign_id": 123456,
     "export_dir": "./kanka_exports"
   }
   ```

3. Set up last run tracking:
   ```bash
   cp kanka_to_md/last_run.template.json kanka_to_md/last_run.json
   ```

**How to get your Kanka API token:**
1. Go to your Kanka campaign
2. Click on your profile picture → "API"
3. Create a new API token
4. Copy the token

**How to find your campaign ID:**
- Look at the URL when you're in your campaign
- It will be something like: `https://kanka.io/en/campaign/123456/`
- The number at the end is your campaign ID

### Alternative: Manual ZIP Export (Recommended for Large Campaigns)

If you have a large campaign with many entities, the API method can be very slow due to rate limits. You can use Kanka's manual export instead:

1. **Export from Kanka:**
   - Go to your Kanka campaign
   - Click on your profile picture → "Export"
   - Choose "Campaign Export" and download the ZIP file

2. **Extract the ZIP:**
   - Extract the ZIP file to `kanka_to_md/kanka_jsons/`
   - The folder structure should look like:
     ```
     kanka_to_md/kanka_jsons/
     ├── characters/
     ├── locations/
     ├── events/
     ├── items/
     ├── notes/
     └── ... (other folders)
     ```

3. **Configure for manual mode:**
   ```json
   {
     "include_private": false,
     "api_token": "not-needed-for-manual-export",
     "campaign_id": 123456,
     "export_dir": "./kanka_exports",
     "manual_export": true
   }
   ```

4. **Set up last run tracking:**
   ```bash
   cp kanka_to_md/last_run.template.json kanka_to_md/last_run.json
   ```

**Why use manual export?**
- **Faster**: No API rate limits to wait for
- **Complete**: Gets all data at once
- **Reliable**: No network issues or timeouts
- **Offline**: Works without internet connection

**When to use API vs Manual Export:**
- **Use API**: Small campaigns (< 100 entities), frequent updates
- **Use Manual Export**: Large campaigns (> 100 entities), one-time exports, slow internet

### 2. Google Drive Configuration (Optional)

If you want to upload PDFs to Google Drive, you'll need to set up Google OAuth.

#### Option A: OAuth Client (Recommended for personal use)

**File:** `google/client_secret.template.json`

1. Copy the template file:
   ```bash
   cp google/client_secret.template.json google/client_secret.json
   ```

2. Get your Google OAuth credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google Drive API
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file
   - Copy the contents to `google/client_secret.json`

#### Option B: Service Account (Recommended for automated use)

**File:** `google/service_account.template.json`

1. Copy the template file:
   ```bash
   cp google/service_account.template.json google/service_account.json
   ```

2. Get your service account credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Go to "IAM & Admin" → "Service Accounts"
   - Create a new service account
   - Give it "Editor" access to Google Drive
   - Create and download a JSON key
   - Copy the contents to `google/service_account.json`

### 3. Google Drive File ID (Optional)

**File:** `drive_file_id_oauth.template.json`

1. Copy the template file:
   ```bash
   cp drive_file_id_oauth.template.json drive_file_id_oauth.json
   ```

2. This file will be automatically created when you first upload a PDF to Google Drive.
   - The first time you run the script with Google Drive enabled, it will create a new file
   - The file ID will be saved here for future updates
   - You can leave this file as-is initially

## Configuration Options

### Kanka Configuration (`config.json`)

| Setting | Description | Default |
|---------|-------------|---------|
| `include_private` | Include private content in the worldbook | `false` |
| `api_token` | Your Kanka API token | Required (or "not-needed-for-manual-export") |
| `campaign_id` | Your Kanka campaign ID | Required |
| `export_dir` | Directory for Kanka exports | `./kanka_exports` |
| `manual_export` | Use manual ZIP export instead of API | `false` |

**About `last_run.json`:**
- **File location**: `kanka_to_md/last_run.json`
- **First time**: Use `"2000-01-01T00:00:00+00:00"` to process all data
- **API mode**: Script automatically updates this timestamp
- **Manual mode**: Set to `"2000-01-01T00:00:00+00:00"` to process all files

**About `manual_export`:**
- **`false`**: Use Kanka API (good for small campaigns, frequent updates)
- **`true`**: Use manual ZIP export (good for large campaigns, one-time exports)

### Google Drive Configuration

**OAuth Client (`client_secret.json`):**
- Used for personal/desktop applications
- Requires browser authentication the first time
- Good for individual users

**Service Account (`service_account.json`):**
- Used for automated/headless applications
- No browser interaction required
- Good for servers or automated scripts

## Security Notes

⚠️ **Important Security Information:**

1. **Never commit real credentials to git**
   - The `.gitignore` file is set up to exclude all credential files
   - Only the template files should be committed

2. **Keep your API tokens secure**
   - Don't share your Kanka API token
   - Don't share your Google credentials
   - Rotate tokens regularly

3. **File permissions**
   - Make sure credential files are readable only by you
   - On Linux/Mac: `chmod 600 google/*.json`

## Troubleshooting

### "API token not found"
- Make sure you've copied `config.template.json` to `config.json`
- Check that your API token is correct
- Verify your campaign ID

### "Google Drive credentials not found"
- Make sure you've copied the appropriate template file
- Check that the JSON file is valid
- Verify the file paths in the code

### "Permission denied"
- Check file permissions on credential files
- Make sure you have the correct Google Drive permissions
- Verify your service account has the right roles

## Next Steps

After setting up your configuration:

1. **Test the setup:**
   ```bash
   python kanka_to_md/main.py
   ```

2. **Check the logs:**
   - Look in the `logs/` folder for any error messages

3. **Customize further:**
   - Edit `main.py` to disable features you don't need
   - Modify the styling in `html_converter.py`
   - Adjust PDF settings in `pdf_converter_wkhtmltopdf.py`

## Support

If you need help with setup:
1. Check the main README.md file
2. Look at the log files in the `logs/` folder
3. Verify all configuration files are set up correctly
4. Make sure you have the required permissions 