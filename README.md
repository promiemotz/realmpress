# RealmPress - Turn Your Kanka Campaign Into Beautiful Documents

**RealmPress** takes your Kanka campaign data and creates beautiful, professional documents you can share with your players or print out.

## ✨ What You Get

- 📄 **Markdown document** - Organized like a professional worldbook
- 🌐 **Beautiful HTML** - Styled to match Kanka's design
- 📖 **PDF with working links** - Professional document ready to share
- ☁️ **Google Drive upload** - Optional sharing with your players
- 🌍 **Multi-language support** - English and Hungarian

## 🚀 Quick Start

1. **Install Python** and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your Kanka API** (see [SETUP.md](SETUP.md)):
   ```bash
   cp kanka_to_md/config.template.json kanka_to_md/config.json
   # Edit config.json with your API token and campaign ID
   ```

3. **Run RealmPress**:
   ```bash
   python -m kanka_to_md.main
   ```

That's it! You'll find your documents in the `output/` folder.

## 📋 What's New

### Latest Release
- ✅ **Manual ZIP export** - Much faster for large campaigns
- ✅ **English and Hungarian language support** - Magyar nyelv támogatás
- ✅ **Improved error handling** - Better logging and troubleshooting
- ✅ **Enhanced cross-references** - Better links between content

See [CHANGELOG.md](CHANGELOG.md) for full release history.

## 🎯 Perfect For

- **Small campaigns** (< 100 entities) - Use API mode for automatic updates
- **Large campaigns** (> 100 entities) - Use manual ZIP export for speed
- **One-time exports** - Create beautiful documents for printing
- **Regular updates** - Keep your worldbook current with campaign changes

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Complete setup instructions
- **[USAGE.md](USAGE.md)** - How to run and customize
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solve common issues
- **[CHANGELOG.md](CHANGELOG.md)** - Release notes and updates

## 🔧 Advanced Features

- **Incremental updates** - Only downloads changed content
- **Privacy controls** - Include or exclude private content
- **Custom output names** - Name your files whatever you want
- **Multiple formats** - Markdown, HTML, and PDF output
- **Cross-references** - Automatic links between related content

## 🆘 Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Look in the `logs/` folder for detailed error messages
3. Make sure your configuration is correct
4. Try running the script again

## 🤝 Contributing

Found a bug or want to add a feature? See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help!

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

**Ready to turn your Kanka campaign into a beautiful worldbook?** Start with [SETUP.md](SETUP.md)! 