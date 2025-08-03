# Changelog

All notable changes to the Telegram Job Scraper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Enhanced salary extraction with support for multiple currencies (USD, EUR, GBP, RUB, UAH, KZT, etc.)
- Advanced salary pattern recognition (ranges, periods, text-based currencies)
- Comprehensive logging system with structured logging and error tracking
- Docker containerization with multi-stage builds
- Docker Compose configuration for easy deployment
- Pre-commit hooks for code quality enforcement
- Comprehensive test suite with high coverage
- Development tools and dependencies
- Deployment scripts and automation
- Cron job examples for scheduled scraping
- Contributing guidelines and development standards
- Enhanced configuration validation with detailed error reporting
- Performance monitoring and optimization tools
- Security enhancements and best practices
- Modular architecture for extensibility

### Changed

- Refactored salary extraction logic to use dedicated module
- Enhanced error handling and logging across all modules
- Improved configuration validation with comprehensive checks
- Updated project structure for better maintainability
- Enhanced test coverage and testing infrastructure
- Improved documentation and code comments

### Fixed

- Salary parsing edge cases and currency detection
- Configuration validation issues
- Logging inconsistencies
- Test reliability and coverage gaps

## [1.0.0] - 2024-01-15

### Added

- Initial release of Telegram Job Scraper
- Basic keyword filtering functionality
- Date-based message filtering
- Multiple output methods (Telegram, file, database)
- Web UI for job management
- Russian job filter with experience requirements
- Basic salary extraction (limited currencies)
- Configuration management with environment variables
- Basic logging and error handling
- Simple test suite

### Features

- Monitor 15-17 Telegram channels for job postings
- Filter jobs by keywords, date, and experience level
- Send matching jobs to personal Telegram chat
- Store jobs in SQLite database
- Web interface for viewing and managing jobs
- Support for Russian job market requirements
- Basic salary range filtering

### Technical Details

- Built with Python 3.8+
- Uses Telethon for Telegram API integration
- Flask-based web interface
- SQLite database for job storage
- Environment-based configuration
- Basic error handling and logging

## [0.9.0] - 2024-01-10

### Added

- Beta version with core functionality
- Telegram client integration
- Basic message filtering
- Simple output methods

### Known Issues

- Limited salary extraction capabilities
- Basic error handling
- Minimal test coverage
- No containerization support

## [0.8.0] - 2024-01-05

### Added

- Alpha version with proof of concept
- Basic Telegram message retrieval
- Simple keyword matching
- File output functionality

---

## Migration Guide

### From 1.0.0 to Unreleased

#### Breaking Changes

- Enhanced salary extraction may require configuration updates
- New logging system requires environment variable updates
- Docker deployment is now the recommended approach

#### Configuration Updates

Add these new environment variables to your `.env` file:

```env
# Enhanced logging
LOG_JSON=false
LOG_COLORS=true

# Performance settings
BATCH_SIZE=50
MAX_RETRIES=3

# Security
ENABLE_SSL_VERIFICATION=true

# Scheduling (optional)
SCHEDULE_INTERVAL_MINUTES=30
SCHEDULE_START_TIME=09:00
SCHEDULE_END_TIME=18:00
SCHEDULE_DAYS_OF_WEEK=0,1,2,3,4,5,6
SCHEDULE_MAX_RUNS_PER_DAY=0
```

#### Docker Deployment

1. Install Docker and Docker Compose
2. Copy the new `docker-compose.yml` and `Dockerfile`
3. Run: `./scripts/deploy.sh deploy production`

#### Local Development

1. Install development dependencies: `pip install -r requirements-dev.txt`
2. Set up pre-commit hooks: `pre-commit install`
3. Run tests: `pytest --cov=src`

---

## Release Process

### Version Numbering

- **MAJOR**: Breaking changes or major feature additions
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and minor improvements

### Release Checklist

- [ ] Update version in `src/__init__.py`
- [ ] Update this CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create GitHub release
- [ ] Deploy to production
- [ ] Announce release

### Release Types

#### Major Release (X.0.0)

- Breaking changes
- Major architectural changes
- Significant new features
- Requires migration guide

#### Minor Release (0.X.0)

- New features
- Backward compatible
- May include deprecation warnings
- Optional migration steps

#### Patch Release (0.0.X)

- Bug fixes
- Performance improvements
- Documentation updates
- No breaking changes

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

## Acknowledgments

- Contributors and maintainers
- Open source libraries and tools
- Telegram API and Telethon library
- Python community and ecosystem
