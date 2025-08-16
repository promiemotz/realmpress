# Troubleshooting Guide

This guide helps you solve common issues with RealmPress.

## Common Issues

### "API token not found"
- Make sure you've set up your API token in `kanka_to_md/config.json`
- Check that the token is correct and hasn't expired

### "PDF conversion failed"
- On Windows, install wkhtmltopdf: `winget install wkhtmltopdf`
- On Mac/Linux, install wkhtmltopdf through your package manager

### "Google Drive upload failed"
- Make sure you have the Google Drive credentials file (`google/client_secret.json`)
- The first time you run it, it will open a browser for authentication
- See [OAUTH_TROUBLESHOOTING.md](OAUTH_TROUBLESHOOTING.md) for detailed help

### "No entities found"
- Check that your campaign ID is correct in the config file
- Make sure your API token has access to the campaign
- Try running the script again (it might need to download data first)
- If using manual export, make sure the ZIP file is extracted to `kanka_to_md/kanka_jsons/`

### "API rate limit exceeded" or "Download taking too long"
- Consider using manual ZIP export instead of API
- Large campaigns can take hours to download via API due to rate limits
- Manual export gets all data at once and is much faster

### "Module not found" errors
- Make sure you're running with `python -m kanka_to_md.main`
- Don't run with `python kanka_to_md/main.py`
- Check that all dependencies are installed: `pip install -r requirements.txt`

### "Permission denied" errors
- Make sure you have write permissions in the project directory
- On Windows, try running as administrator
- Check that the `output/` and `logs/` directories exist and are writable

## Performance Issues

### Slow Downloads
- **Large campaigns**: Use manual ZIP export instead of API
- **Network issues**: Try again later or use manual export
- **Rate limits**: Kanka limits API calls; manual export bypasses this

### Memory Issues
- Close other applications while running RealmPress
- For very large campaigns, consider processing in smaller chunks
- Check available RAM on your system

### Disk Space
- Ensure you have enough free disk space for:
  - Downloaded JSON files (in `kanka_to_md/kanka_jsons/`)
  - Generated output files (in `output/`)
  - Temporary files during processing

## Log Files

Check the `logs/` folder for detailed error messages and progress information. Log files contain:
- Detailed error messages
- Progress information
- API response details
- Performance metrics

## Getting Help

If you're still having issues:

1. **Check the logs**: Look in the `logs/` folder for detailed error messages
2. **Verify configuration**: Make sure your `config.json` is set up correctly
3. **Test individual components**: Try running parts of the process separately
4. **Check dependencies**: Ensure all required packages are installed
5. **Update Python**: Make sure you're using a recent version of Python

## Related Documentation

- [SETUP.md](SETUP.md) - Complete setup instructions
- [USAGE.md](USAGE.md) - Usage and customization guide
- [OAUTH_TROUBLESHOOTING.md](OAUTH_TROUBLESHOOTING.md) - Google Drive OAuth issues
- [HTML_CONVERSION_README.md](HTML_CONVERSION_README.md) - HTML conversion details
- [PDF_CONVERSION_README.md](PDF_CONVERSION_README.md) - PDF conversion details
