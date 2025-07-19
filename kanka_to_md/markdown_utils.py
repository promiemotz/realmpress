"""
markdown_utils.py
----------------
Utility functions for processing and converting markdown and HTML content.

Provides helpers to:
- Convert Kanka mentions and HTML to markdown
- Create anchor labels for internal links
- Escape markdown-sensitive characters

Intended for use in the Kanka to Markdown/HTML workflow.
"""

import re
import unicodedata
from bs4 import BeautifulSoup
from typing import Optional, Dict


def convert_mentions_in_html(html_text: str) -> str:
    """Replace Kanka <a class='mention'> links with markdown links from data-mention and convert HTML to markdown."""
    soup = BeautifulSoup(html_text, 'html.parser')
    for a_tag in soup.find_all('a', class_='mention'):
        data_mention = a_tag.get('data-mention')
        if data_mention:
            a_tag.replace_with(data_mention)
        else:
            a_tag.unwrap()  # fallback
    result = str(soup)
    result = re.sub(r'<p>(.*?)</p>', r'\1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<br/?>', '\n', result)
    result = re.sub(r'<hr/?>', '\n---\n', result)
    result = re.sub(r'<strong>(.*?)</strong>', r'**\1**', result, flags=re.DOTALL)
    result = re.sub(r'<b>(.*?)</b>', r'**\1**', result, flags=re.DOTALL)
    result = re.sub(r'<em>(.*?)</em>', r'*\1*', result, flags=re.DOTALL)
    result = re.sub(r'<i>(.*?)</i>', r'*\1*', result, flags=re.DOTALL)
    result = re.sub(r'<ul>(.*?)</ul>', r'\1', result, flags=re.DOTALL)
    result = re.sub(r'<ol>(.*?)</ol>', r'\1', result, flags=re.DOTALL)
    result = re.sub(r'<li>(.*?)</li>', r'- \1\n', result, flags=re.DOTALL)
    result = re.sub(r'<h1>(.*?)</h1>', r'# \1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<h2>(.*?)</h2>', r'## \1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<h3>(.*?)</h3>', r'### \1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<h4>(.*?)</h4>', r'#### \1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<h5>(.*?)</h5>', r'##### \1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<h6>(.*?)</h6>', r'###### \1\n\n', result, flags=re.DOTALL)
    result = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', result, flags=re.DOTALL)
    result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
    return result


def create_anchor_label(name: Optional[str]) -> str:
    """Create a markdown-friendly, ASCII-only anchor slug from name."""
    if not name:
        return ""
    slug = name.strip().lower()
    slug = unicodedata.normalize('NFKD', slug)
    slug = ''.join(c for c in slug if not unicodedata.combining(c))
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'[^\w\-]', '', slug)
    return slug


def replace_mentions(text: str, entity_map: Dict[int, Dict[str, str]]) -> str:
    """Replace Kanka mentions like [character:12345] with markdown links."""
    def replacer(match):
        entity_id = int(match.group(2))
        entity = entity_map.get(entity_id)
        if entity:
            anchor = create_anchor_label(entity['name'])
            return f"[{entity['name']}](#{anchor})"
        else:
            return f"**Entity_{entity_id}**"
    return re.sub(r'\[(\w+):(\d+)\]', replacer, text)


def md_escape(text: Optional[str]) -> str:
    """Escape underscores and other markdown sensitive characters."""
    if not text:
        return ""
    return text.replace('_', '\\_') 