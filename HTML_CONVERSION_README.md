# Creating Beautiful HTML from Your Kanka Worldbook

This guide explains how to turn your Kanka campaign data into a beautiful HTML document that you can view in a web browser or convert to PDF.

## What This Tool Does

RealmPress takes your Kanka campaign data and creates a professional HTML document that:

1. **Looks Beautiful** - Uses styling that matches Kanka's professional appearance
2. **Has Working Links** - All internal links (character references, locations, etc.) work properly
3. **Is Responsive** - Looks good on computers, tablets, and phones
4. **Is PDF-Ready** - Can be easily converted to PDF with working links

## What Files Are Created

When you run the HTML conversion, you get:
- **`worldbook_styled.html`** - A beautiful HTML file you can open in any web browser
- **Working internal links** - Click on character names to jump to their sections
- **Professional styling** - Looks like a published worldbook
- **Print-friendly layout** - Perfect for converting to PDF

## How to Use

### Method 1: Run the Complete Workflow (Recommended)
This creates everything including the HTML:
```bash
python kanka_to_md/main.py
```

### Method 2: Convert Existing Markdown
If you already have a `worldbook.md` file:
```bash
python kanka_to_md/html_converter.py
```

### Method 3: Windows Batch File
Double-click or run:
```bash
convert_md_to_html.bat
```

## What the Process Does

### Step 1: Extracts Styling
The tool looks at your Kanka HTML export and extracts:
- Professional fonts and typography
- Color schemes and styling
- Layout and spacing
- Additional PDF-friendly styling

### Step 2: Converts Markdown to HTML
Your campaign content is converted with:
- **Headers** - Proper heading hierarchy (#, ##, ###)
- **Bold and italic text** - **bold** and *italic* formatting
- **Lists** - Bullet points and numbered lists
- **Links** - Working internal and external links
- **Code blocks** - For any technical content

### Step 3: Fixes All Links
The tool makes sure all links work properly:
- **Internal links** - `[Character Name](#character-name)` become clickable
- **External links** - Website links open in new tabs
- **Anchor tags** - Creates proper targets for all linked content

### Step 4: Applies Professional Styling
The final HTML includes:
- **Kanka-like fonts** and typography
- **Professional layout** with proper spacing
- **Color-coded links** (different colors for different types)
- **Responsive design** that works on all devices

## Viewing Your HTML

### Opening in a Browser
1. Find the `worldbook_styled.html` file in your project folder
2. Double-click it (or right-click → "Open with" → your preferred browser)
3. The file will open and display your worldbook beautifully

### What You'll See
- **Professional layout** with proper margins and spacing
- **Working navigation** - click any link to jump to that section
- **Beautiful typography** that matches Kanka's style
- **Responsive design** - works on different screen sizes

## Converting to PDF

### Option 1: Browser Print to PDF (Easiest)
1. Open `worldbook_styled.html` in Chrome, Firefox, or Edge
2. Press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
3. Select "Save as PDF" from the destination dropdown
4. Click "Save"
5. All links will be clickable in the PDF!

### Option 2: Use RealmPress PDF Conversion
```bash
python kanka_to_md/main.py
```
This automatically creates the HTML and then converts it to PDF.

### Option 3: Use Pandoc (Advanced Users)
If you have Pandoc installed:
```bash
pandoc worldbook_styled.html -o worldbook.pdf --pdf-engine=wkhtmltopdf
```

## Understanding the Links

The HTML file automatically categorizes and styles different types of links:

### Internal Links (Clickable in HTML and PDF)
- **Character links** (blue): `[Gandalf](#gandalf)` → Jumps to character section
- **Location links** (blue): `[Rivendell](#rivendell)` → Jumps to location section
- **Session links** (red): `[Session 1](#session-1)` → Jumps to session notes
- **Item links** (blue): `[Sword](#sword)` → Jumps to item description

### External Links (Opens in New Tab)
- **Website links** (blue): `[D&D Beyond](https://dndbeyond.com)` → Opens in new tab
- **Image links** (blue): `[Map](https://example.com/map.jpg)` → Opens image

## Troubleshooting

### "HTML source file not found"
**Problem:** The tool can't find the Kanka HTML export file.

**Solution:**
1. Make sure you've run the main script first to download your Kanka data
2. Check that `kanka_to_md/worldbook-1752250347.htm` exists
3. If the file has a different name, update the path in the script

### "Markdown source file not found"
**Problem:** The tool can't find the markdown file to convert.

**Solution:**
1. Make sure `worldbook.md` exists in your project folder
2. Run the main script first to generate the markdown file
3. Check that you're in the correct directory

### "Links not working in PDF"
**Problem:** Links don't work when you convert to PDF.

**Solutions:**
1. Use a PDF viewer that supports links (Adobe Reader, Chrome PDF viewer)
2. Make sure the HTML file was generated correctly
3. Try the browser print-to-PDF method instead

### "Styling looks wrong"
**Problem:** The HTML doesn't look like Kanka.

**Solutions:**
1. The tool extracts CSS from your Kanka export, so styling should match
2. If fonts don't load, the browser will use fallback fonts
3. Make sure you're viewing in a modern web browser

## Customization Options

### Changing Link Colors
You can modify the CSS in `html_converter.py` to change:
- Character link colors
- Location link colors
- Session link colors
- External link colors

### Adding Custom CSS
You can add your own styling by editing the `css_styles` variable in the script.

### Modifying the HTML Structure
The script creates a clean HTML5 structure that you can customize for your needs.

## File Structure

After running the conversion, you'll have:
```
your-project/
├── worldbook.md                    # Your markdown file
├── worldbook_styled.html           # Beautiful HTML version
├── kanka_to_md/
│   ├── html_converter.py          # The conversion script
│   └── worldbook-1752250347.htm   # Kanka HTML export
└── HTML_CONVERSION_README.md       # This file
```

## Benefits Over Original Kanka HTML

### Working Links
- All internal links function properly
- Links work in PDF conversion
- External links open in new tabs

### Clean Structure
- Proper HTML5 semantic markup
- Easy to modify and customize
- Professional output ready for sharing

### PDF Compatibility
- Links work in PDF conversion
- Print-friendly layout
- Professional formatting

### Maintainable
- Easy to modify and customize
- Clean, readable code
- Well-documented process

## Performance Tips

### For Large Campaigns
- HTML generation is usually fast (under 30 seconds)
- File size depends on content amount
- Browser rendering is smooth even with large files

### For Better Quality
- Use high-quality images in your Kanka campaign
- Well-organized content creates better HTML
- Proper entity names create working links

## Getting Help

If you encounter issues:

1. **Check the logs** - Look in the `logs/` folder for error messages
2. **Verify files exist** - Make sure the required files are present
3. **Test step by step** - Try running just the markdown generation first
4. **Check browser compatibility** - Use a modern web browser

### Common Error Messages

**"File not found"**
- Make sure you're in the correct directory
- Check that the required files exist
- Run the main script first to generate files

**"Permission denied"**
- Check file permissions
- Make sure you can write to the current folder

**"Encoding error"**
- Make sure your Kanka content uses UTF-8 encoding
- Check for special characters in entity names

The HTML conversion process is designed to be reliable and create beautiful, professional output that you can share with your players or convert to PDF. 