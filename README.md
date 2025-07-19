# realmpress
A kanka.io exporter, which can turn your RPG world's data into different file format and upload it to some repository for your palyers

# RealmPress - Turn Your Kanka Campaign Into Beautiful Documents

**RealmPress** is a tool that takes all your Kanka campaign data (characters, locations, events, etc.) and turns it into beautiful, professional documents that you can share with your players or print out.

## What Does RealmPress Do?

RealmPress connects to your Kanka campaign and:

1. **Downloads your campaign data** - Characters, locations, events, items, and more
2. **Creates a beautiful markdown document** - Organized and formatted like a professional worldbook
3. **Converts it to HTML** - With beautiful styling that matches Kanka's look
4. **Creates a PDF** - With working links that players can click on
5. **Optionally uploads to Google Drive** - So you can share it with your players

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
1. Open `kanka_to_md/config.json` in a text editor
2. Replace the placeholder values with your actual Kanka information:
```json
{
    "api_token": "your-kanka-api-token-here",
    "campaign_id": "your-campaign-id-here",
    "include_private": false
}
```

### Step 6: Run RealmPress
Choose one of these methods:

**Option A: Simple Command Line**
```bash
python kanka_to_md/main.py
```

**Option B: GUI (if available)**
```bash
python kanka_to_md/gui.py
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

## Advanced Features

### Using the GUI
If you prefer a graphical interface:
```bash
python kanka_to_md/gui.py
```
This opens a window where you can:
- Select which features to enable/disable
- Set your API credentials
- Customize the chapter order
- Run the workflow with a button click

### Custom Output Names
You can specify custom output files:
```bash
python kanka_to_md/main.py --output my_campaign.md
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
├── gui.py                     # Graphical interface
├── config.json               # Your Kanka settings
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