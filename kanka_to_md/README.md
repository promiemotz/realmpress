# RealmPress - Kanka to Markdown Converter

This folder contains the main RealmPress application that converts your Kanka campaign data into beautiful documents.

## What's in This Folder

### Main Scripts (What You Run)
- **`main.py`** - The main script that does everything (downloads data, creates documents, etc.)
- **`gui.py`** - A graphical interface for easier use (if you prefer clicking buttons)

### Configuration
- **`config.json`** - Your Kanka API settings (API token, campaign ID, etc.)
- **`requirements.txt`** - List of Python packages needed

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

### Data Storage
- **`kanka_jsons/`** - Folder where your downloaded Kanka data is stored
- **`entities/`** - Individual entity files
- **`characters/`** - Character data
- **`locations/`** - Location data
- **`events/`** - Event data
- And more folders for other content types...

## Quick Start

1. **Set up your configuration:**
   ```bash
   # Edit config.json with your Kanka API details
   ```

2. **Run the main script:**
   ```bash
   python main.py
   ```

3. **Or use the GUI:**
   ```bash
   python gui.py
   ```

## Understanding the Process

When you run `main.py`, it does these steps in order:

1. **Downloads Data** - Gets all your campaign content from Kanka
2. **Processes Data** - Organizes everything by type (characters, locations, etc.)
3. **Creates Markdown** - Builds a beautiful, organized document
4. **Converts to HTML** - Makes it look professional with styling
5. **Creates PDF** - Generates a PDF with working links
6. **Uploads to Drive** - (Optional) Shares it on Google Drive

## Customizing the Output

### Changing What Gets Included
Edit `config.json`:
```json
{
    "api_token": "your-token",
    "campaign_id": "your-campaign",
    "include_private": false  // Set to true to include private content
}
```

### Disabling Features
Edit `main.py` and comment out lines you don't want:
```python
# To skip Google Drive upload, comment out this line:
# upload_to_drive(output_pdf, logger)
```

## Troubleshooting

### Common Issues
- **"API token not found"** - Check your `config.json` file
- **"PDF conversion failed"** - Install wkhtmltopdf: `winget install wkhtmltopdf`
- **"No data found"** - Make sure your campaign ID is correct

### Log Files
Check the `logs/` folder for detailed error messages and progress information.

## File Descriptions

### `main.py`
The main script that orchestrates everything. It's heavily commented so you can easily understand what each part does and disable features you don't want.

### `gui.py`
A graphical interface built with Tkinter. Provides a user-friendly way to:
- Set your API credentials
- Choose which features to enable
- Customize the output
- Run the workflow with a button click

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

## Advanced Usage

### Running Individual Components
You can run individual parts of the process:

```bash
# Just download data from Kanka
python -c "from kanka_function import fetch_and_save_updated_entities; fetch_and_save_updated_entities()"

# Just convert existing markdown to HTML
python html_converter.py

# Just convert HTML to PDF
python pdf_converter_wkhtmltopdf.py worldbook_styled.html
```

### Custom Output Names
```bash
python main.py --output my_campaign.md
```

### Using the GUI
The GUI provides a visual way to:
- Set your API credentials
- Choose which features to enable/disable
- Customize chapter order
- Set conditions for content inclusion
- Run the workflow with progress feedback

## Support

If you need help:
1. Check the main README.md file
2. Look at the log files in the `logs/` folder
3. Make sure your configuration is correct
4. Try running the script again

The code is heavily commented to help you understand what's happening and customize it for your needs. 