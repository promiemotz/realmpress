# Usage Guide

This guide covers how to run RealmPress and customize its output.

## Running RealmPress

### Basic Usage
```bash
python -m kanka_to_md.main
```

> **Note:** RealmPress currently requires running as a package/module. Do not run with `python kanka_to_md/main.py`.

### Windows Batch File
```bash
convert_to_pdf.bat
```

## Understanding the Output

### Generated Files
After running RealmPress, you'll have:
- `worldbook.md` - A markdown file with all your campaign content
- `worldbook_styled.html` - A beautiful HTML version you can view in a browser
- `worldbook.pdf` - A professional PDF with working links
- A shareable Google Drive link (if you enable this feature)

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

## Customizing the Output

### Excluding Private Content
By default, RealmPress only includes public content. To include private content:
1. Edit `kanka_to_md/config.json`
2. Change `"include_private": false` to `"include_private": true`

### Custom Output Names
You can specify custom output files:
```bash
python -m kanka_to_md.main --output my_campaign.md
```

### Disabling Google Drive Upload
If you don't want to upload to Google Drive:
1. Open `kanka_to_md/main.py` in a text editor
2. Find the line that says `upload_to_drive(output_pdf, logger)`
3. Add `#` at the beginning of the line to comment it out:
```python
# upload_to_drive(output_pdf, logger)
```

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

## Performance Tips

### For Large Campaigns (> 100 entities)
1. **Use manual ZIP export** instead of API
2. **Extract ZIP to `kanka_to_md/kanka_jsons/`**
3. **Set `manual_export: true` in config**
4. **This can save hours of waiting time**

### For Small Campaigns (< 100 entities)
1. **Use API mode** for automatic updates
2. **Set `last_run` to `"2000-01-01T00:00:00+00:00"` for first run**
3. **Subsequent runs will be faster** (only new content)

### API Rate Limits
- Kanka limits API calls to prevent server overload
- When running for the first time, large campaigns can take hours to download via API
- Manual export bypasses these limits entirely

## Advanced Usage

### Running Individual Components
You can run individual parts of the process:

```bash
# Just download data from Kanka
python -c "from kanka_to_md.kanka_function import fetch_and_save_updated_entities; fetch_and_save_updated_entities()"

# Just convert existing markdown to HTML
python kanka_to_md/html_converter.py

# Just convert HTML to PDF
python kanka_to_md/pdf_converter_wkhtmltopdf.py worldbook_styled.html
```

### Running Tests
To make sure everything is working:
```bash
python -m unittest discover test
```

## What Gets Translated
When using different languages:
- Chapter titles (Locations, Characters, Events, etc.)
- UI elements (Generation Settings, Details, etc.)
- Section headers and navigation
- Configuration labels

## Adding New Languages
To add support for additional languages:
1. Edit `kanka_to_md/translations.json`
2. Add a new language section with translations
3. Update `SUPPORTED_LANGUAGES` in `kanka_to_md/localization.py`

## File Structure

```
kanka_to_md/
├── main.py                    # Main script (what you run)
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
```

## Next Steps

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues
- Check [CHANGELOG.md](CHANGELOG.md) for latest updates
- Review [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
