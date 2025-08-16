# Setup Guide

This guide will help you set up RealmPress to work with your Kanka campaign.

## Prerequisites

### Python Installation
First, you need Python installed on your computer:
- **Windows**: Download from [python.org](https://python.org) or use the Microsoft Store
- **Mac**: Download from [python.org](https://python.org) or use Homebrew
- **Linux**: Usually comes pre-installed, or use your package manager

### Install Dependencies
Run this command to install the required packages:
```bash
pip install -r requirements.txt
```

## Getting Your Kanka API Token

1. Go to your Kanka campaign
2. Click on your profile picture → "API"
3. Create a new API token
4. Copy the token

## Configuration Options

### Option A: Using API (Recommended for small campaigns)

1. Copy the template file:
   ```bash
   cp kanka_to_md/config.template.json kanka_to_md/config.json
   ```

2. Edit `kanka_to_md/config.json` and replace the placeholder values:
   ```json
   {
       "api_token": "your-kanka-api-token-here",
       "campaign_id": "your-campaign-id-here",
       "include_private": false
   }
   ```

3. Copy the last run template:
   ```bash
   cp kanka_to_md/last_run.template.json kanka_to_md/last_run.json
   ```

### Option B: Using Manual ZIP Export (Recommended for large campaigns)

If you have a large campaign with many entities, the API method can be slow due to rate limits. You can use Kanka's manual export instead:

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
       "api_token": "not-needed-for-manual-export",
       "campaign_id": "your-campaign-id-here",
       "include_private": false,
       "last_run": "2000-01-01T00:00:00+00:00",
       "manual_export": true
   }
   ```

4. **Set up last run tracking:**
   ```bash
   cp kanka_to_md/last_run.template.json kanka_to_md/last_run.json
   ```

## When to Use API vs Manual Export

- **Use API**: Small campaigns (< 100 entities), frequent updates
- **Use Manual Export**: Large campaigns (> 100 entities), one-time exports, slow internet

**Why use manual export?**
- **Faster**: No API rate limits to wait for
- **Complete**: Gets all data at once
- **Reliable**: No network issues or timeouts
- **Offline**: Works without internet connection

## Language Configuration

RealmPress supports multiple languages for chapter titles and UI elements. Currently supported languages:
- **English (en)** - Default language
- **Hungarian (hu)** - Magyar nyelv

### Setting the Language

**Option 1: Config File (Recommended)**
Edit `kanka_to_md/config.json` and add or modify the language setting:
```json
{
    "include_private": false,
    "language": "en",
    "api_token": "your-kanka-api-token-here",
    "campaign_id": "your-campaign-id-here"
}
```

**Option 2: Command Line**
Override the config file language using the CLI:
```bash
# Use English
python -m kanka_to_md.main --language en

# Use Hungarian
python -m kanka_to_md.main --language hu
```

## Google Drive Setup (Optional)

If you want to upload your documents to Google Drive:

1. Follow the instructions in [SETUP_TEMPLATES.md](SETUP_TEMPLATES.md)
2. Set up OAuth credentials in the `google/` folder
3. The first time you run RealmPress, it will open a browser for authentication

## PDF Generation Setup

To create PDFs, you need wkhtmltopdf installed:

- **Windows**: `winget install wkhtmltopdf`
- **Mac**: `brew install wkhtmltopdf`
- **Linux**: `sudo apt-get install wkhtmltopdf` (Ubuntu/Debian)

## Next Steps

Once you've completed the setup, see [USAGE.md](USAGE.md) for how to run RealmPress and customize the output.
