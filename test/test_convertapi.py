#!/usr/bin/env python3
"""
Test script for ConvertAPI PDF conversion.
This will help you set up and test the ConvertAPI integration.
"""

import os
import sys

def test_convertapi():
    """Test ConvertAPI functionality."""
    print("🧪 Testing ConvertAPI PDF conversion...")
    
    # Check if ConvertAPI is installed
    try:
        import convertapi
        print("✅ ConvertAPI package is installed")
    except ImportError:
        print("❌ ConvertAPI not installed. Run: pip install convertapi")
        return False
    
    # Check for API key
    api_key = os.environ.get('CONVERTAPI_SECRET')
    if not api_key:
        print("⚠️  No ConvertAPI secret key found in environment")
        print("   Set it with: set CONVERTAPI_SECRET=your_key_here")
        print("   Get free key at: https://www.convertapi.com/a/auth")
        print("\n   Or edit this script and add your key directly:")
        print("   api_key = 'your_secret_key_here'")
        return False
    
    print(f"✅ ConvertAPI secret key found: {api_key[:8]}...")
    
    # Test with a simple HTML
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test PDF</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #5D0000; }
            .column { float: left; width: 45%; margin: 10px; }
        </style>
    </head>
    <body>
        <h1>Test PDF with Hungarian: ö ő ü ű</h1>
        <div class="column">
            <h2>Left Column</h2>
            <p>This is the left column with <a href="#test">internal link</a>.</p>
        </div>
        <div class="column">
            <h2>Right Column</h2>
            <p>This is the right column with <a href="https://example.com">external link</a>.</p>
        </div>
    </body>
    </html>
    """
    
    try:
        # Set the API key
        convertapi.api_secret = api_key
        
        # Convert HTML to PDF
        print("🔄 Converting test HTML to PDF...")
        result = convertapi.convert('pdf', {
            'File': test_html
        }, from_format='html')
        
        # Save test PDF
        test_pdf = "test_convertapi.pdf"
        result.file.save(test_pdf)
        
        print(f"✅ Test PDF created: {test_pdf}")
        print("🎉 ConvertAPI is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ConvertAPI test failed: {e}")
        if "unauthorized" in str(e).lower():
            print("💡 Check your ConvertAPI secret key")
        elif "quota" in str(e).lower():
            print("💡 You may have reached your ConvertAPI quota limit")
        return False

def main():
    """Main function."""
    print("=" * 50)
    print("ConvertAPI Test Script")
    print("=" * 50)
    
    if test_convertapi():
        print("\n🎉 Success! You can now use ConvertAPI for PDF conversion.")
        print("\nNext steps:")
        print("1. Run: python -m kanka_to_md.main")
        print("2. Your worldbook will be converted to PDF with perfect fidelity!")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 