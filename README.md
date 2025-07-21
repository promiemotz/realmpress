# RealmPress - Turn Your Kanka Campaign Into Beautiful Documents

**RealmPress** is a tool that takes all your Kanka campaign data (characters, locations, events, etc.) and turns it into beautiful, professional documents that you can share with your players or print out.

## What Does RealmPress Do?

RealmPress connects to your Kanka campaign and:

1. **Downloads your campaign data** - Characters, locations, events, items, and more
2. **Creates a beautiful markdown document** - Organized and formatted like a professional worldbook
3. **Supports multiple languages** - English and Hungarian chapter titles and UI elements
4. **Converts it to HTML** - With beautiful styling that matches Kanka's look
5. **Creates a PDF** - With working links that players can click on
6. **Optionally uploads to Google Drive** - So you can share it with your players

## What You Get

After running RealmPress, you'll have:
- `worldbook.md` - A markdown file with all your campaign content
- `worldbook_styled.html` - A beautiful HTML version you can view in a browser
- `worldbook.pdf` - A professional PDF with working links
- A shareable Google Drive link (if you enable this feature)

## Quick Start Guide

### Step 1: Install Python
First, you need Python installed on your computer:
- **Windows**: Download from [python.org](https://python.org) or use the Microsoft Store
- **Mac**: Download from [python.org](https://python.org) or use Homebrew
- **Linux**: Usually comes pre-installed, or use your package manager

### Step 2: Download RealmPress
1. Download this project to your computer
2. Open a command prompt/terminal in the project folder

### Step 3: Install Dependencies
Run this command to install the required packages:
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Your Kanka API
1. Go to your Kanka campaign
2. Click on your profile picture → "API"
3. Create a new API token
4. Copy the token

### Step 5: Configure RealmPress

#### Option A: Using API (Recommended for small campaigns)
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

#### Option B: Using Manual ZIP Export (Recommended for large campaigns)
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

**Why use manual export?**
- **Faster**: No API rate limits to wait for
- **Complete**: Gets all data at once
- **Reliable**: No network issues or timeouts
- **Offline**: Works without internet connection

**When to use API vs Manual Export:**
- **Use API**: Small campaigns (< 100 entities), frequent updates
- **Use Manual Export**: Large campaigns (> 100 entities), one-time exports, slow internet

### Step 6: Run RealmPress
Choose one of these methods:

**Option A: Simple Command Line**
```bash
python -m kanka_to_md.main
```

> **Note:** RealmPress currently requires running as a package/module. Right now do not run with `python kanka_to_md/main.py`.

**Option B: GUI (Coming Soon)**
```bash
# GUI is not yet implemented - use Option A instead
python -m kanka_to_md.main
```

**Option C: Windows Batch File**
```bash
convert_to_pdf.bat
```

## Understanding the Output

### The Markdown File (`worldbook.md`)
This is a text file with all your campaign content in a readable format. It includes:
- Table of contents with links
- Organized sections for each type of content
- Cross-references between related items
- Proper formatting and structure

### The HTML File (`worldbook_styled.html`)
This is a beautiful web page version of your worldbook that:
- Looks professional and matches Kanka's styling
- Has working internal links
- Can be viewed in any web browser
- Is ready to be converted to PDF

### The PDF File (`worldbook.pdf`)
This is the final product - a professional document that:
- Has all internal links working (clickable)
- Opens external links in your browser
- Looks great when printed
- Can be shared with your players

## Customizing What Gets Included

### Excluding Private Content
By default, RealmPress only includes public content. To include private content:
1. Edit `kanka_to_md/config.json`
2. Change `"include_private": false` to `"include_private": true`

### Language Localization
RealmPress supports multiple languages for chapter titles and UI elements. Currently supported languages:
- **English (en)** - Default language
- **Hungarian (hu)** - Magyar nyelv

#### Setting the Language

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

#### What Gets Translated
- Chapter titles (Locations, Characters, Events, etc.)
- UI elements (Generation Settings, Details, etc.)
- Section headers and navigation
- Configuration labels

#### Adding New Languages
To add support for additional languages:
1. Edit `kanka_to_md/translations.json`
2. Add a new language section with translations
3. Update `SUPPORTED_LANGUAGES` in `kanka_to_md/localization.py`

### Disabling Google Drive Upload
If you don't want to upload to Google Drive:
1. Open `kanka_to_md/main.py` in a text editor
2. Find the line that says `upload_to_drive(output_pdf, logger)`
3. Add `#` at the beginning of the line to comment it out:
```python
# upload_to_drive(output_pdf, logger)
```

## Troubleshooting

### "API token not found"
- Make sure you've set up your API token in `kanka_to_md/config.json`
- Check that the token is correct and hasn't expired

### "PDF conversion failed"
- On Windows, install wkhtmltopdf: `winget install wkhtmltopdf`
- On Mac/Linux, install wkhtmltopdf through your package manager

### "Google Drive upload failed"
- Make sure you have the Google Drive credentials file (`google/client_secret.json`)
- The first time you run it, it will open a browser for authentication

### "No entities found"
- Check that your campaign ID is correct in the config file
- Make sure your API token has access to the campaign
- Try running the script again (it might need to download data first)
- If using manual export, make sure the ZIP file is extracted to `kanka_to_md/kanka_jsons/`

### "API rate limit exceeded" or "Download taking too long"
- Consider using manual ZIP export instead of API
- Large campaigns can take hours to download via API due to rate limits
- Manual export gets all data at once and is much faster

## Configuration Details

### Last Run Configuration
The `last_run.json` file tells RealmPress when it last downloaded data. This helps it only download new or updated content:

**File:** `kanka_to_md/last_run.json`
```json
{
    "last_run": "2000-01-01T00:00:00+00:00"
}
```

**What this means:**
- **First time**: Use `"2000-01-01T00:00:00+00:00"` to download everything
- **Subsequent runs**: The script automatically updates this timestamp
- **Manual export**: Set to `"2000-01-01T00:00:00+00:00"` to process all files

**Performance impact:**
- **API mode**: Only downloads entities changed since last run (faster)
- **Manual mode**: Processes all files in the `kanka_jsons/` folder

### Performance Tips

#### For Large Campaigns (> 100 entities)
1. **Use manual ZIP export** instead of API
2. **Extract ZIP to `kanka_to_md/kanka_jsons/`**
3. **Set `manual_export: true` in config**
4. **This can save hours of waiting time**

#### For Small Campaigns (< 100 entities)
1. **Use API mode** for automatic updates
2. **Set `last_run` to `"2000-01-01T00:00:00+00:00"` for first run**
3. **Subsequent runs will be faster** (only new content)

#### API Rate Limits
- Kanka limits API calls to prevent server overload
- Large campaigns can take 2-6 hours to download via API
- Manual export bypasses these limits entirely

## Advanced Features

### Using the GUI
**Note: GUI is not yet implemented**

A graphical interface is planned but not yet available. For now, please use the command line interface:

```bash
python -m kanka_to_md.main
```

Future GUI features will include:
- Select which features to enable/disable
- Set your API credentials
- Customize the chapter order
- Run the workflow with a button click

### Custom Output Names
You can specify custom output files:
```bash
python -m kanka_to_md.main --output my_campaign.md
```

### Running Tests
To make sure everything is working:
```bash
python -m unittest discover test
```

## File Structure

```
kanka_to_md/
├── main.py                    # Main script (what you run)
├── gui.py                     # Graphical interface (not yet implemented)
├── config.json               # Your Kanka settings
├── translations.json         # Language translations
├── localization.py           # Localization support
├── kanka_jsons/              # Downloaded campaign data
├── html_converter.py         # Converts markdown to HTML
├── pdf_converter_wkhtmltopdf.py  # Creates PDFs
└── publish_to_drive_oauth.py # Uploads to Google Drive

output/                        # Generated files (created when you run)
├── worldbook.md              # Markdown version
├── worldbook_styled.html     # HTML version
└── worldbook.pdf             # PDF version

logs/                         # Log files (for troubleshooting)
config/                       # Configuration files
```

## Getting Help

If you run into problems:
1. Check the log files in the `logs/` folder
2. Make sure all your configuration is correct
3. Try running the script again
4. Check that you have the latest version of Python

## Contributing

This project is open source! If you find bugs or want to add features:
1. Check the existing issues
2. Create a new issue or pull request
3. Follow the coding standards in the project

## License

This project is licensed under the **MIT License**. This means:
- ✅ You can use it for free for any purpose (including commercial)
- ✅ You can modify and share it
- ✅ You can sell it or use it in commercial projects
- 📝 You must include the original license and copyright notice

The MIT License is one of the most permissive open source licenses, giving you maximum freedom to use, modify, and distribute the software.

See the LICENSE file for full details. 