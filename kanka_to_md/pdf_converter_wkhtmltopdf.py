#!/usr/bin/env python3
"""
pdf_converter_wkhtmltopdf.py
----------------------------
Convert HTML to PDF with perfect fidelity using wkhtmltopdf.

This module provides functions to:
- Check for the presence of wkhtmltopdf (Windows-friendly)
- Convert HTML files to PDF, preserving all HTML features
- Convert Markdown files to PDF by first converting to HTML
- Provide a CLI for direct usage

Intended for use in the Kanka to Markdown/HTML/PDF workflow.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_wkhtmltopdf():
    """Check if wkhtmltopdf is installed and available."""
    # Common installation paths
    wkhtmltopdf_paths = [
        'wkhtmltopdf',  # If in PATH
        r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
        r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
    ]
    
    for path in wkhtmltopdf_paths:
        try:
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ wkhtmltopdf found: {result.stdout.strip()}")
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("❌ wkhtmltopdf not found")
    print("   Install with: winget install wkhtmltopdf")
    return None

def convert_html_to_pdf(html_file_path, output_pdf_path=None, title="Worldbook"):
    """
    Convert HTML file to PDF using wkhtmltopdf.
    
    Args:
        html_file_path (str): Path to the input HTML file
        output_pdf_path (str): Path for the output PDF file (optional)
        title (str): Title for the PDF document
    
    Returns:
        str: Path to the generated PDF file
    """
    if not os.path.exists(html_file_path):
        raise FileNotFoundError(f"HTML file not found: {html_file_path}")
    
    # Generate output path if not provided
    if output_pdf_path is None:
        html_path = Path(html_file_path)
        output_pdf_path = html_path.with_suffix('.pdf')
    
    # Get wkhtmltopdf path
    wkhtmltopdf_path = check_wkhtmltopdf()
    if not wkhtmltopdf_path:
        raise RuntimeError("wkhtmltopdf not found")
    
    print(f"🔄 Converting {html_file_path} to PDF using wkhtmltopdf...")
    
    try:
        # Build wkhtmltopdf command with optimal settings
        cmd = [
            wkhtmltopdf_path,
            '--page-size', 'A4',
            '--margin-top', '20mm',
            '--margin-right', '20mm',
            '--margin-bottom', '20mm',
            '--margin-left', '20mm',
            '--encoding', 'UTF-8',
            '--enable-local-file-access',
            '--enable-internal-links',
            '--enable-external-links',
            '--print-media-type',
            '--no-stop-slow-scripts',
            '--javascript-delay', '1000',
            '--title', title,
            html_file_path,
            output_pdf_path
        ]
        
        # Run the conversion
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"✅ PDF created successfully: {output_pdf_path}")
        return str(output_pdf_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting to PDF: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

def convert_markdown_to_pdf(markdown_file_path, output_pdf_path=None, title="Worldbook"):
    """
    Convert Markdown file directly to PDF by first converting to HTML.
    
    Args:
        markdown_file_path (str): Path to the input Markdown file
        output_pdf_path (str): Path for the output PDF file (optional)
        title (str): Title for the PDF document
    
    Returns:
        str: Path to the generated PDF file
    """
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"Markdown file not found: {markdown_file_path}")
    
    # Generate temporary HTML file
    temp_html_path = markdown_file_path.replace('.md', '_temp.html')
    
    try:
        # Import and use the HTML converter
        from html_converter import convert_markdown_file_to_html
        convert_markdown_file_to_html(markdown_file_path, temp_html_path)
        
        # Convert HTML to PDF
        pdf_path = convert_html_to_pdf(temp_html_path, output_pdf_path, title)
        
        # Clean up temporary HTML file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        
        return pdf_path
        
    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        raise

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert HTML or Markdown to PDF with perfect fidelity using wkhtmltopdf')
    parser.add_argument('input_file', help='Input HTML or Markdown file')
    parser.add_argument('-o', '--output', help='Output PDF file path (optional)')
    parser.add_argument('-t', '--title', default='Worldbook', help='PDF title (default: Worldbook)')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output
    title = args.title
    
    # Check if wkhtmltopdf is available
    if not check_wkhtmltopdf():
        sys.exit(1)
    
    try:
        if input_file.endswith('.html'):
            convert_html_to_pdf(input_file, output_file, title)
        elif input_file.endswith('.md'):
            convert_markdown_to_pdf(input_file, output_file, title)
        else:
            print("❌ Unsupported file format. Please provide an HTML (.html) or Markdown (.md) file.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 