# RealmPress Package Documentation

This folder contains the main RealmPress application that converts your Kanka campaign data into beautiful documents.

> **For users**: See the main [README.md](../README.md) for quick start instructions and [SETUP.md](../SETUP.md) for detailed setup.

## 📁 Package Structure

### Main Scripts
- **`main.py`** - The main script that orchestrates everything
- **`gui.py`** - Graphical interface (planned for future release)

### Configuration
- **`config.json`** - Your Kanka API settings (API token, campaign ID, etc.)
- **`requirements.txt`** - List of Python packages needed
- **`translations.json`** - Language translations for UI elements

### Core Functions
- **`kanka_function.py`** - Connects to Kanka and downloads your campaign data
- **`worldbook_generator.py`** - Creates the beautiful markdown document
- **`html_converter.py`** - Converts markdown to HTML with styling
- **`pdf_converter_wkhtmltopdf.py`** - Creates PDFs with working links
- **`publish_to_drive_oauth.py`** - Uploads files to Google Drive

### Helper Functions
- **`entity_processing.py`** - Organizes and processes your campaign data
- **`markdown_utils.py`** - Handles markdown formatting and links
- **`io_utils.py`** - Reads and writes files
- **`localization.py`** - Handles multi-language support

### Data Storage
- **`kanka_jsons/`** - Folder where your downloaded Kanka data is stored
- **`entities/`** - Individual entity files
- **`characters/`** - Character data
- **`locations/`** - Location data
- **`events/`** - Event data
- And more folders for other content types...

## 🚀 Quick Usage

```bash
# Run the main application
python -m kanka_to_md.main

# Run with custom language
python -m kanka_to_md.main --language hu

# Run with custom output name
python -m kanka_to_md.main --output my_campaign.md
```

## 🔧 Development

### Running Individual Components
You can run individual parts of the process for testing:

```bash
# Just download data from Kanka
python -c "from kanka_to_md.kanka_function import fetch_and_save_updated_entities; fetch_and_save_updated_entities()"

# Just convert existing markdown to HTML
python kanka_to_md/html_converter.py

# Just convert HTML to PDF
python kanka_to_md/pdf_converter_wkhtmltopdf.py worldbook_styled.html
```

### Running Tests
```bash
python -m unittest discover test
```

### Adding New Languages
1. Edit `translations.json` and add a new language section
2. Update `SUPPORTED_LANGUAGES` in `localization.py`
3. Test with `python -m kanka_to_md.main --language your_language_code`

## 📋 File Descriptions

### `main.py`
The main script that orchestrates everything. It's heavily commented so you can easily understand what each part does and disable features you don't want.

### `kanka_function.py`
Handles all communication with the Kanka API. It:
- Downloads your campaign data
- Only downloads what's changed since last time
- Handles API rate limits and errors
- Saves data in organized folders

### `worldbook_generator.py`
Creates the beautiful markdown document. It:
- Organizes content by type
- Creates a table of contents
- Adds cross-references between related content
- Formats everything professionally

### `html_converter.py`
Converts markdown to HTML with beautiful styling. It:
- Applies Kanka-like styling
- Makes all links work properly
- Creates a responsive design
- Prepares the document for PDF conversion

### `pdf_converter_wkhtmltopdf.py`
Creates PDFs with working links. It:
- Uses wkhtmltopdf for high-quality output
- Preserves all styling and formatting
- Makes internal links clickable
- Opens external links in your browser

### `publish_to_drive_oauth.py`
Uploads files to Google Drive. It:
- Uses OAuth for secure authentication
- Creates shareable links
- Updates existing files (keeps the same link)
- Sets proper sharing permissions

## 📚 Related Documentation

- **[Main README](../README.md)** - Quick start and overview
- **[SETUP.md](../SETUP.md)** - Complete setup instructions
- **[USAGE.md](../USAGE.md)** - Usage and customization guide
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Common issues and solutions
- **[CHANGELOG.md](../CHANGELOG.md)** - Release notes and updates

## 🆘 Support

If you need help:
1. Check the main [README.md](../README.md) file
2. Look at the log files in the `logs/` folder
3. Make sure your configuration is correct
4. Try running the script again

The code is heavily commented to help you understand what's happening and customize it for your needs. 