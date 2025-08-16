# Changelog

All notable changes to RealmPress will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.2] - 2025-08-16

### Added
- Support for post handling
- Images
- Campaign overview as first chapter

### Changed
- Restructured documentation for better organization

### Fixed
- Some error handling for specific cases

## [v1.1] - 2025-07-21

### Added
- Support for manual ZIP export from Kanka (faster for large campaigns)
- Hungarian language support
- Improved error handling and logging
- Better cross-references between entities

### Changed
- Restructured documentation for better organization
- Improved PDF generation with working links

### Fixed
- API rate limiting issues for large campaigns
- PDF link generation problems
- Character relationship display issues

## [1.0] - 2025-07-19

### Added
- Initial release of RealmPress
- Kanka API integration
- Markdown generation from campaign data
- HTML conversion with styling
- PDF generation with wkhtmltopdf
- Google Drive upload functionality
- Support for multiple entity types (characters, locations, events, items, notes)
- Cross-references between related content
- Table of contents generation
- Configurable privacy settings
- Last run tracking for incremental updates

### Features
- Downloads campaign data from Kanka API
- Creates organized markdown documents
- Converts to beautiful HTML with Kanka-like styling
- Generates PDFs with working internal links
- Optional Google Drive integration for sharing
- Support for both public and private content
- Incremental updates (only downloads changed content)
- Multiple language support (English, Hungarian)
