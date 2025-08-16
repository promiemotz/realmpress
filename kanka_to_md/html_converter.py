#!/usr/bin/env python3
"""
html_converter.py
-----------------
Convert Markdown to HTML with Kanka styling and working hyperlinks.

This module provides functions to:
- Clean and preprocess Markdown content (remove Kanka-specific slug references, fix links)
- Convert Markdown to HTML with custom handling for headings and links
- Apply Kanka/Worldbook CSS styling to the output HTML
- Generate a complete HTML document for viewing or further conversion

Intended for use in the Kanka to Markdown/HTML workflow.
"""

import markdown
from bs4 import BeautifulSoup
import re
import logging
import os
import base64
from .markdown_utils import create_anchor_label

# Logging setup (if not already set by main)
if not logging.getLogger().hasHandlers():
    import os
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('logs/realmpress.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)


def embed_images_as_base64(html_content):
    """Convert image references to embedded base64 data."""
    import os
    
    # Find all img tags with gallery references
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    
    for img in img_tags:
        src = img.get('src', '')
        if src.startswith('gallery/'):
            # Construct the full path to the image file
            gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
            image_path = os.path.join(gallery_dir, src.replace('gallery/', ''))
            
            if os.path.exists(image_path):
                try:
                    # Read the image file and convert to base64
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        
                        # Determine the MIME type based on file extension
                        ext = os.path.splitext(image_path)[1].lower()
                        mime_type = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif',
                            '.webp': 'image/webp'
                        }.get(ext, 'image/jpeg')
                        
                        # Update the src attribute with base64 data
                        img['src'] = f'data:{mime_type};base64,{img_base64}'
                        logger.info(f"Embedded image: {src}")
                        
                except Exception as e:
                    logger.error(f"Failed to embed image {src}: {e}")
                    # Keep the original src if embedding fails
            else:
                logger.warning(f"Image file not found: {image_path}")
    
    return str(soup)


def clean_markdown_content(md):
    """Remove slug references like ((++++++city)) from headings while preserving the heading text."""
    lines = md.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('#'):
            cleaned_line = re.sub(r'\s*\(\(\++[^)]+\)\)\s*$', '', line)
            cleaned_line = re.sub(r'\s*\(\(\+{5,}[^)]+\)\)\s*$', '', cleaned_line)
            cleaned_line = cleaned_line.rstrip()
            cleaned_lines.append(cleaned_line)
        else:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def preprocess_links(md):
    """Convert [text](#anchor) and [text](http...) to <a href="...">text</a> everywhere, even inside <p> or <span>."""
    # Don't convert image syntax, only regular links
    pattern = re.compile(r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)')
    return pattern.sub(r'<a href="\2">\1</a>', md)


def detect_hierarchy_level(text):
    """Detect hierarchy level from the plus signs in anchor labels like ((+++anchor))."""
    # Look for patterns like ((+++anchor)) and count the plus signs
    match = re.search(r'\(\(\++([^)]+)\)\)', text)
    if match:
        # Count the plus signs in the matched group
        full_match = match.group(0)  # e.g., "((+++teszt-journal-2))"
        # Remove the (( and )) to get just the plus signs and anchor
        inner_content = full_match[2:-2]  # e.g., "+++teszt-journal-2"
        # Count consecutive plus signs at the beginning
        plus_count = 0
        for char in inner_content:
            if char == '+':
                plus_count += 1
            else:
                break
        return min(plus_count, 5)  # Cap at level 5
    return 1

def convert_markdown_to_html(markdown_content):
    """Convert Markdown to HTML using the markdown package, then post-process links for custom classes and add ids to headings. Also handle h7/h8 as custom divs and hierarchy levels."""
    
    # Parse hierarchy levels from original markdown BEFORE cleaning
    hierarchy_levels = {}
    lines = markdown_content.split('\n')
    for line in lines:
        if line.strip().startswith('#'):
            # Look for patterns like ## Teszt Journal ((++teszt-journal))
            match = re.search(r'^(#+)\s*(.*?)\s*\(\((\++)([^)]+)\)\)', line)
            if match:
                header_level = len(match.group(1))  # Count # symbols
                title = match.group(2).strip()
                pluses = match.group(3)  # The plus signs
                anchor = match.group(4)  # The anchor without plus signs
                # Count plus signs
                hierarchy_level = len(pluses)
                hierarchy_levels[title] = hierarchy_level
    
    # Now clean the markdown content
    markdown_content = clean_markdown_content(markdown_content)
    markdown_content = preprocess_links(markdown_content)
    markdown_content = re.sub(r'^(########)\s*(.*)', r'[[[H8]]] \2', markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^(#######)\s*(.*)', r'[[[H7]]] \2', markdown_content, flags=re.MULTILINE)
    
    html_content = markdown.markdown(markdown_content, extensions=[])
    
    # Now clean up the anchors
    html_content = re.sub(r'(<h[1-6][^>]*>)([^<]*?)(\(\(\+{1,}[^)]+\)\)[^<]*?)(</h[1-6]>)', r'\1\2\4', html_content)
    html_content = re.sub(r'(<h[1-6][^>]*>)([^<]*?)(\s*\+\+[^<]*?)(</h[1-6]>)', r'\1\2\4', html_content)
    html_content = re.sub(r'(<h[1-8][^>]*>)([^<]*?)(</h[1-8]>)', lambda m: m.group(1) + m.group(2).replace('#', '') + m.group(3), html_content)

    def replace_h7(match):
        text = match.group(1).strip()
        text = re.sub(r'^#+\s*', '', text)
        anchor = create_anchor_label(text)
        return f'<div class="h7" id="{anchor}">{text}</div>'
    def replace_h8(match):
        text = match.group(1).strip()
        text = re.sub(r'^#+\s*', '', text)
        anchor = create_anchor_label(text)
        return f'<div class="h8" id="{anchor}">{text}</div>'
    html_content = re.sub(r'<p>\[\[\[H7\]\]\]\s*([^<]*)</p>', replace_h7, html_content)
    html_content = re.sub(r'<p>\[\[\[H8\]\]\]\s*([^<]*)</p>', replace_h8, html_content)
    html_content = re.sub(r'\[\[\[H7\]\]\]\s*([^<\n]*)', replace_h7, html_content)
    html_content = re.sub(r'\[\[\[H8\]\]\]\s*([^<\n]*)', replace_h8, html_content)

    soup = BeautifulSoup(html_content, 'html.parser')

    for tag in soup.find_all(re.compile('^h[1-6]$')):
        if tag.has_attr('id'):
            del tag['id']

    for tag in soup.find_all(re.compile('^h[1-6]$')):
        text = tag.get_text().strip()
        anchor = create_anchor_label(text)
        tag['id'] = anchor
        
        # Apply hierarchy classes from stored levels
        if text in hierarchy_levels:
            level = hierarchy_levels[text]
            if level > 1:
                tag['class'] = tag.get('class', []) + [f'hierarchy-level-{level}']
                tag['class'] = tag.get('class', []) + ['child-entity']

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '')
        if href.startswith('#'):
            anchor = href[1:]
            clean_anchor = create_anchor_label(anchor)
            a_tag['href'] = f'#{clean_anchor}'
        elif href.startswith('http'):
            a_tag['target'] = '_blank'
            a_tag['rel'] = 'noopener noreferrer'
        a_tag['class'] = a_tag.get('class', []) + ['pointer']

    # Embed images as base64 data
    html_content = embed_images_as_base64(str(soup))

    return html_content


def create_html_document(html_content, title="Worldbook"):
    """Create a complete HTML document with Kanka styling."""
    css_styles = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    body { background: #000; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    #result { max-width: 1200px; margin: 1rem auto; }
    .bg-paper { background: #F4EEE0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 2rem; position: relative; }
    .page { padding: 2rem; }
    .content h1 { color: #5D0000; font-family: 'Inter', sans-serif; font-weight: 700; font-size: 2.5rem; margin-bottom: 1.5rem; border-bottom: 2px solid #5D0000; padding-bottom: 0.5rem; }
    .content h2 { color: #5D0000; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 2rem; margin: 1.5rem 0 1rem 0; border-bottom: 1px solid #5D0000; padding-bottom: 0.3rem; }
    .content h3 { color: #A76652; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 1.8rem; margin: 1.2rem 0 0.8rem 0; }
    .content h4 { color: #A76652; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 1.6rem; margin: 1.1rem 0 0.7rem 0; }
    .content h5 { color: #8B4513; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 1.4rem; margin: 1rem 0 0.5rem 0; background: #E6D8B0; padding: 0.5rem; border-radius: 4px; border-left: 4px solid #8B4513; }
    .content h6 { color: #2E8B57; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 1.3rem; margin: 0.9rem 0 0.4rem 0; text-decoration: underline; text-decoration-color: #2E8B57; }
    .content h7 { color: #4682B4; font-family: 'Inter', sans-serif; font-weight: 500; font-size: 1.2rem; margin: 0.8rem 0 0.3rem 0; font-style: italic; }
    .content h8 { color: #9370DB; font-family: 'Inter', sans-serif; font-weight: 500; font-size: 1.1rem; margin: 0.7rem 0 0.2rem 0; text-decoration: underline wavy #9370DB; }
    .content .h7 { color: #4682B4; font-family: 'Inter', sans-serif; font-weight: 500; font-size: 1.2rem; margin: 0.8rem 0 0.3rem 0; font-style: italic; }
    .content .h8 { color: #9370DB; font-family: 'Inter', sans-serif; font-weight: 500; font-size: 1.1rem; margin: 0.7rem 0 0.2rem 0; text-decoration: underline wavy #9370DB; }
    .content p { font-family: 'Inter', sans-serif; line-height: 1.6; margin-bottom: 1rem; color: #333; }
    .content ul, .content ol { font-family: 'Inter', sans-serif; margin-bottom: 1rem; padding-left: 2rem; }
    .content li { margin-bottom: 0.5rem; line-height: 1.5; }
    .content hr { background: #5D0000; border: none; height: 2px; margin: 2rem 0; }
    .pointer { color: rgb(172, 13, 74); text-decoration: none; font-weight: 500; transition: color 0.2s ease; }
    .pointer:hover { color: rgb(211, 126, 14); text-decoration: underline; }
    .page-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, rgba(93,0,0,0.05) 0%, rgba(167,102,82,0.05) 100%); pointer-events: none; border-radius: 8px; }
    
    /* Hierarchy indentation styles */
    .hierarchy-level-1 { margin-left: 0; }
    .hierarchy-level-2 { margin-left: 2rem; border-left: 4px solid #FF6B6B; padding-left: 1.5rem; background: linear-gradient(90deg, rgba(255,107,107,0.1) 0%, transparent 100%); }
    .hierarchy-level-3 { margin-left: 4rem; border-left: 4px solid #4ECDC4; padding-left: 1.5rem; background: linear-gradient(90deg, rgba(78,205,196,0.1) 0%, transparent 100%); }
    .hierarchy-level-4 { margin-left: 6rem; border-left: 4px solid #45B7D1; padding-left: 1.5rem; background: linear-gradient(90deg, rgba(69,183,209,0.1) 0%, transparent 100%); }
    .hierarchy-level-5 { margin-left: 8rem; border-left: 4px solid #96CEB4; padding-left: 1.5rem; background: linear-gradient(90deg, rgba(150,206,180,0.1) 0%, transparent 100%); }
    .child-entity { font-style: italic; }
    
    /* Image styling */
    .content img { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin: 1rem 0; display: block; }
    .content img:hover { transform: scale(1.02); transition: transform 0.2s ease; }
    
    @media (max-width: 768px) { .page { padding: 1rem; } #result { margin: 0.5rem; } }
    """
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1, maximum-scale=1, minimum-scale=1, shrink-to-fit=no">
<title>{title}</title>
<style>
{css_styles}
</style>
</head>
<body>
<div id="result">
<div class="bg-paper page" data-markdown="1">
<div class="page-overlay"></div>
<div class="content" data-markdown="1">
{html_content}
</div>
</div>
</div>
</body>
</html>"""
    
    return html_template


def convert_markdown_file_to_html(markdown_file_path, output_file_path):
    logger.info(f"Converting {markdown_file_path} to HTML...")
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    markdown_content = re.sub(r'^\s*=\s*$', '', markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'^\s*\|\s*$', '', markdown_content, flags=re.MULTILINE)
    markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
    html_content = convert_markdown_to_html(markdown_content)
    html_document = create_html_document(html_content, "Worldbook")
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(html_document)
    logger.info(f"✅ HTML file created: {output_file_path}")


if __name__ == "__main__":
    convert_markdown_file_to_html("worldbook.md", "worldbook_styled.html") 