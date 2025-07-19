# Creating PDFs from Your Kanka Worldbook

This guide explains how to turn your Kanka campaign data into a beautiful PDF that you can share with your players or print out.

## What You Get

When you create a PDF with RealmPress, you get:
- ✅ **Working Links** - All internal links (like character references) are clickable
- ✅ **Beautiful Styling** - Looks professional and matches Kanka's design
- ✅ **Cross-Platform** - Works on Windows, Mac, and Linux
- ✅ **Print-Ready** - Perfect for printing or sharing digitally

## Quick Start - Choose Your Method

### Method 1: Windows Users (Easiest)
Double-click the `convert_to_pdf.bat` file, or run it from the command line:
```bash
convert_to_pdf.bat
```

### Method 2: All Platforms (Python)
Run the main script which includes PDF creation:
```bash
python kanka_to_md/main.py
```

### Method 3: Just PDF Conversion
If you already have the HTML file:
```bash
python kanka_to_md/pdf_converter_wkhtmltopdf.py worldbook_styled.html
```

## What Files Are Created

The PDF creation process creates these files in order:
1. **`worldbook.md`** - Your campaign content in markdown format
2. **`worldbook_styled.html`** - A beautiful HTML version with styling
3. **`worldbook.pdf`** - The final PDF with working links

## Requirements

### What You Need
- **Python** - The programming language that runs RealmPress
- **wkhtmltopdf** - A tool that converts HTML to PDF (we'll help you install this)

### Automatic Installation
The script will try to install required packages automatically. If it fails, you can install them manually:
```bash
pip install markdown beautifulsoup4
```

### Installing wkhtmltopdf

**Windows:**
```bash
winget install wkhtmltopdf
```
Or download from: https://wkhtmltopdf.org/downloads.html

**Mac:**
```bash
brew install wkhtmltopdf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install wkhtmltopdf
```

**Linux (Fedora):**
```bash
sudo dnf install wkhtmltopdf
```

## Troubleshooting Common Problems

### "wkhtmltopdf not found"
**Solution:** Install wkhtmltopdf using the commands above.

**Windows users:** After installing, you might need to restart your command prompt.

### "PDF conversion failed"
**Common causes:**
1. wkhtmltopdf not installed
2. Not enough disk space
3. File permissions issue

**Solutions:**
1. Install wkhtmltopdf (see above)
2. Check you have at least 100MB free space
3. Try running as administrator (Windows) or with sudo (Mac/Linux)

### "Font issues" or "Text looks wrong"
**Solution:** The PDF will use system fonts. If you want the exact Kanka fonts:
1. Install the Inter font family on your system
2. Or the PDF will automatically use similar fonts

### "Large file size"
**Causes:**
- Many images in your campaign
- High-resolution images
- Large amount of content

**Solutions:**
1. Optimize images in your Kanka campaign (compress them)
2. Consider splitting into multiple PDFs
3. Use a lower quality setting (advanced users)

### "Links not working in PDF"
**Solutions:**
1. Use a PDF viewer that supports links (Adobe Reader, Chrome PDF viewer)
2. Make sure the HTML file was generated correctly
3. Check that your Kanka entities have proper names

## Platform-Specific Notes

### Windows
- **Easiest method:** Use `convert_to_pdf.bat`
- **Install wkhtmltopdf:** `winget install wkhtmltopdf`
- **If fonts look wrong:** Install Inter font family

### Mac
- **Install wkhtmltopdf:** `brew install wkhtmltopdf`
- **If you get permission errors:** Use `sudo` before commands
- **Font issues:** Mac usually handles fonts well

### Linux
- **Install wkhtmltopdf:** Use your package manager (apt, dnf, etc.)
- **Permission issues:** Use `sudo` if needed
- **Font issues:** Install additional fonts if needed

## Advanced Usage

### Custom PDF Names
```bash
python kanka_to_md/pdf_converter_wkhtmltopdf.py worldbook_styled.html -o my_campaign.pdf
```

### Custom PDF Titles
```bash
python kanka_to_md/pdf_converter_wkhtmltopdf.py worldbook_styled.html -t "My Campaign Worldbook"
```

### Converting Markdown Directly
```bash
python kanka_to_md/pdf_converter_wkhtmltopdf.py worldbook.md
```

## Understanding the Process

### Step 1: Markdown Creation
RealmPress downloads your Kanka data and creates a markdown file with:
- Table of contents
- Organized sections (characters, locations, events, etc.)
- Cross-references between related content
- Proper formatting

### Step 2: HTML Conversion
The markdown is converted to HTML with:
- Beautiful styling that matches Kanka
- Working internal links
- Responsive design
- Professional layout

### Step 3: PDF Creation
The HTML is converted to PDF with:
- All links preserved and working
- Professional formatting
- Print-ready layout
- Optimized file size

## Link Types That Work

### Internal Links (Clickable in PDF)
- **Character references:** `[Gandalf](#gandalf)` → Jumps to character section
- **Location references:** `[Rivendell](#rivendell)` → Jumps to location section
- **Session references:** `[Session 1](#session-1)` → Jumps to session notes

### External Links (Opens in Browser)
- **Website links:** `[D&D Beyond](https://dndbeyond.com)` → Opens in your browser
- **Image links:** `[Map](https://example.com/map.jpg)` → Opens image in browser

## Performance Tips

### For Large Campaigns
- **Time:** PDF creation may take 2-5 minutes for campaigns with many entities
- **Memory:** Close other applications if you get memory errors
- **Storage:** Ensure you have at least 100MB free space

### For Better Quality
- **Images:** Use high-quality images in your Kanka campaign
- **Content:** Well-organized content creates better PDFs
- **Links:** Proper entity names create working links

## File Locations

After running the script, you'll find these files:
```
your-project/
├── worldbook.md              # Markdown version
├── worldbook_styled.html     # HTML version  
├── worldbook.pdf             # Final PDF
├── logs/                     # Log files (for troubleshooting)
└── kanka_to_md/
    ├── main.py               # Main script
    ├── pdf_converter_wkhtmltopdf.py  # PDF conversion
    └── html_converter.py     # HTML conversion
```

## Getting Help

If you're having trouble:

1. **Check the logs:** Look in the `logs/` folder for error messages
2. **Verify installation:** Make sure wkhtmltopdf is installed correctly
3. **Test step by step:** Try running just the HTML conversion first
4. **Check file permissions:** Make sure you can write to the current folder

### Common Error Messages

**"wkhtmltopdf not found"**
- Install wkhtmltopdf using the commands above
- Restart your command prompt/terminal

**"Permission denied"**
- Windows: Run as administrator
- Mac/Linux: Use `sudo` before the command

**"File not found"**
- Make sure you're in the correct folder
- Check that the HTML file exists

**"Out of memory"**
- Close other applications
- Try with a smaller campaign first

## Support

If you're still having issues:
1. Check that all dependencies are installed
2. Verify your Kanka API token is valid
3. Ensure you have sufficient disk space
4. Look at the console output for specific error messages
5. Try running the script again

The PDF creation process is designed to be reliable and user-friendly, but if you encounter problems, the error messages should help you identify the issue. 