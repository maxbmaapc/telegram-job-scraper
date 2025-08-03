# Telegram Job Scraper

A robust, production-ready Python-based Telegram job scraper that monitors groups/channels for job postings matching specific keywords and filters. Built with scalability, maintainability, and extensibility in mind.

## 🚀 Features

- 🔍 **Advanced Keyword Filtering**: Case-insensitive matching with exclusion keywords
- 💰 **Enhanced Salary Extraction**: Multi-currency support (USD, EUR, GBP, RUB, UAH, KZT, etc.)
- 📅 **Smart Date Filtering**: Configurable time windows with timezone support
- 📱 **Telegram Integration**: Uses Telethon for full user access to Telegram
- 💾 **Multiple Output Options**: Send to self, save to file, or store in database
- 🏗️ **Modular Architecture**: Plugin-ready design for easy extensions
- 🌐 **Modern Web UI**: Flask-based interface with real-time updates
- 🐳 **Docker Support**: Containerized deployment with Docker Compose
- 📊 **Comprehensive Logging**: Structured logging with error tracking
- 🧪 **Extensive Testing**: High test coverage with automated testing
- 🔒 **Security First**: Secure credential handling and SSL verification
- ⚡ **Performance Optimized**: Async processing and batch operations
- 📈 **Monitoring Ready**: Health checks and performance metrics

## 🎯 Core Features

- 🔍 **Advanced Keyword Filtering**: Case-insensitive matching with exclusion keywords
- 💰 **Enhanced Salary Extraction**: Multi-currency support with range detection
- 📅 **Smart Date Filtering**: Configurable time windows with timezone support
- 📱 **Telegram Integration**: Uses Telethon for full user access to Telegram
- 💾 **Multiple Output Options**: Send to self, save to file, or store in database
- 🏗️ **Modular Architecture**: Plugin-ready design for easy extensions
- 🌐 **Modern Web UI**: Flask-based interface with real-time updates

## 📁 Project Structure

```
telegram-job-scraper/
├── src/                     # Source code
│   ├── main.py              # Entry point
│   ├── config.py            # Enhanced configuration management
│   ├── filters.py           # Advanced filtering logic
│   ├── salary_extractor.py  # Enhanced salary extraction
│   ├── logging_config.py    # Centralized logging configuration
│   ├── telegram_client.py   # Telegram API client
│   ├── output.py            # Output delivery methods
│   ├── scheduler.py         # Job scheduling
│   └── utils.py             # Utility functions
├── tests/                   # Comprehensive test suite
│   ├── test_filters.py      # Filter tests
│   ├── test_salary_extractor.py  # Salary extraction tests
│   └── conftest.py          # Test configuration
├── web/                     # Modern web UI
│   ├── app.py               # Flask application
│   ├── templates/           # HTML templates
│   └── static/              # Static assets
├── scripts/                 # Deployment and utility scripts
│   ├── deploy.sh            # Deployment automation
│   └── cron_example.txt     # Cron job examples
├── docker/                  # Docker configuration
│   ├── Dockerfile           # Multi-stage Docker build
│   └── docker-compose.yml   # Service orchestration
├── docs/                    # Documentation
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .pre-commit-config.yaml  # Code quality hooks
├── .env.example            # Environment variables template
├── .gitignore
├── README.md
├── CONTRIBUTING.md          # Contribution guidelines
└── CHANGELOG.md            # Version history
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ or Docker
- Telegram account
- Telegram API credentials (API ID and API Hash)

### Option 1: Docker Deployment (Recommended)

1. **Clone and configure**:

   ```bash
   git clone https://github.com/maxbmaapc/telegram-job-scraper.git
   cd telegram-job-scraper
   cp config_template.txt .env
   # Edit .env with your credentials
   ```

2. **Deploy with Docker**:

   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh deploy production
   ```

3. **Access the application**:
   - Web UI: http://localhost:5000
   - Logs: `./scripts/deploy.sh logs`

### Option 2: Local Development

1. **Clone and setup**:

   ```bash
   git clone https://github.com/maxbmaapc/telegram-job-scraper.git
   cd telegram-job-scraper
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

3. **Get Telegram API credentials**:

   - Go to https://my.telegram.org/apps
   - Create a new application
   - Note your API ID and API Hash

4. **Configure environment**:

   ```bash
   cp config_template.txt .env
   # Edit .env with your credentials and settings
   ```

5. **Set up development tools**:

   ```bash
   pre-commit install
   ```

6. **Run tests**:
   ```bash
   pytest --cov=src
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Telegram API Credentials
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE_NUMBER=your_phone_number_here

# Target Groups/Channels (comma-separated)
TARGET_CHANNELS=channel1_id,channel2_id,channel3_id

# Filter Keywords (comma-separated)
FILTER_KEYWORDS=junior,remote,london,react,node.js,typescript,python,vue.js,ionic,aws,nosql,backend,frontend,full stack

# Date Filter (in hours, 0 = no filter)
DATE_FILTER_HOURS=24

# Output Settings
OUTPUT_METHOD=telegram  # Options: telegram, file, database
SEND_TO_SELF=true  # Set to false to send to target account instead

# Target Personal Account (where to send messages when SEND_TO_SELF=false)
# TARGET_USER_ID=123456789  # Your personal Telegram user ID
# TARGET_USERNAME=your_username  # Your personal Telegram username (without @)
# TARGET_PHONE_NUMBER=+1234567890  # Your personal phone number

# Database Settings (if using database output)
DATABASE_PATH=jobs.db

# Enhanced Logging
LOG_LEVEL=INFO
LOG_FILE=logs/telegram_scraper.log
LOG_JSON=false  # Enable structured JSON logging
LOG_COLORS=true  # Enable colored console output

# Web UI Settings
WEB_HOST=localhost
WEB_PORT=5000

# Performance Settings
BATCH_SIZE=50  # Messages to process in batches
MAX_RETRIES=3  # Max retries for failed operations

# Rate Limiting (to avoid Telegram bans)
MESSAGE_DELAY_MIN=2.0  # Minimum delay between messages
MESSAGE_DELAY_MAX=3.0  # Maximum delay between messages

# Scheduling (optional)
SCHEDULE_INTERVAL_MINUTES=30
SCHEDULE_START_TIME=09:00
SCHEDULE_END_TIME=18:00
SCHEDULE_DAYS_OF_WEEK=0,1,2,3,4,5,6  # 0=Sunday, 1=Monday, etc.
SCHEDULE_MAX_RUNS_PER_DAY=0  # 0 = unlimited

# Security
ENABLE_SSL_VERIFICATION=true
```

### Enhanced Features

#### 🎯 Advanced Salary Extraction

The scraper now supports comprehensive salary extraction:

```python
# Supported formats:
"$50k-$80k USD"           # Range with currency
"£45,000 per annum"       # Single amount with period
"от 100000 до 200000 рублей"  # Russian format
"€60k/year"               # European format
"$25/hour"                # Hourly rate
```

#### 📊 Structured Logging

Enhanced logging with structured output and error tracking:

```python
# JSON structured logs
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "telegram_scraper.filters",
  "message": "Job filtered successfully",
  "extra_fields": {
    "job_id": "12345",
    "keywords_matched": ["python", "remote"]
  }
}
```

#### 🔧 Configuration Validation

Comprehensive configuration validation with detailed error reporting:

```bash
# Validate configuration
python -c "from src.config import config; config.validate()"
```

## 🚀 Usage

### Basic Usage

```bash
# Single scraping session
python src/main.py --mode single --limit 100

# Continuous monitoring
python src/main.py --mode continuous

# Scheduled scraping
python src/main.py --mode scheduled
```

### Docker Deployment

```bash
# Deploy to production
./scripts/deploy.sh deploy production

# Deploy for development
./scripts/deploy.sh deploy development

# Check status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs telegram-scraper

# Stop services
./scripts/deploy.sh stop
```

### Development

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Lint code
flake8 src/ tests/

# Run all quality checks
pre-commit run --all-files
```

### Web UI

```bash
# Start web interface
python web/app.py

# Access at http://localhost:5000
```

## 🔍 Advanced Filtering

### Enhanced Keyword Filtering

- **Case-insensitive matching** with exclusion keywords
- **Multi-language support** (English, Russian, etc.)
- **Smart keyword detection** with context awareness
- **Configurable via environment variables**

### Advanced Salary Extraction

- **Multi-currency support**: USD, EUR, GBP, RUB, UAH, KZT, etc.
- **Range detection**: "$50k-$80k", "от 100000 до 200000 рублей"
- **Period recognition**: hourly, daily, weekly, monthly, yearly
- **Text-based currencies**: "dollars", "euros", "рублей"

### Smart Date Filtering

- **Timezone-aware filtering** with configurable windows
- **Business hours scheduling** with day-of-week support
- **Flexible time formats** and relative time expressions

### Experience Level Filtering

- **Junior position detection** with multiple languages
- **Experience requirement parsing** (years, levels)
- **Senior position exclusion** with customizable keywords

## 🐳 Deployment

### Docker Deployment

The application is containerized for easy deployment:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.yml --profile production up -d

# Development deployment
docker-compose -f docker-compose.yml --profile development up -d
```

### Production Considerations

- **Resource limits**: Configured memory and CPU limits
- **Health checks**: Automatic health monitoring
- **Log rotation**: Automatic log file management
- **Backup strategies**: Database and configuration backups
- **Security**: Non-root user, SSL verification, secure secrets

### Monitoring and Observability

- **Structured logging** with JSON format support
- **Error tracking** with context and stack traces
- **Performance metrics** with timing information
- **Health endpoints** for monitoring systems
- **Prometheus metrics** (optional)

## 🧪 Testing

### Test Coverage

- **Unit tests**: Core functionality testing
- **Integration tests**: End-to-end workflow testing
- **Performance tests**: Load and stress testing
- **Security tests**: Vulnerability scanning

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_filters.py
pytest tests/test_salary_extractor.py

# Run performance tests
pytest tests/test_performance.py
```

## 🔧 Development

### Code Quality

- **Pre-commit hooks**: Automatic code formatting and linting
- **Type checking**: Full type annotation support
- **Documentation**: Comprehensive docstrings and examples
- **Code review**: Automated quality checks

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Development Workflow

1. **Fork and clone** the repository
2. **Set up development environment** with pre-commit hooks
3. **Create feature branch** and make changes
4. **Run tests** and ensure coverage
5. **Submit pull request** with detailed description

## 📈 Performance

### Optimization Features

- **Async processing** for I/O operations
- **Batch processing** for message handling
- **Connection pooling** for database operations
- **Caching strategies** for repeated operations
- **Rate limiting** to respect API limits

### Scalability

- **Modular architecture** for easy scaling
- **Plugin system** for extensibility
- **Database indexing** for query optimization
- **Horizontal scaling** support with Docker

## Output Methods

### 1. Telegram (Send to Self or Target Account)

- Sends filtered job posts to your own Telegram chat or a target account
- Real-time notifications
- Easy to read on mobile
- **New**: Can send to a different personal account (see [SETUP_TARGET_ACCOUNT.md](SETUP_TARGET_ACCOUNT.md))

### 2. File Output

- Saves to JSON or CSV format
- Structured data for analysis
- Easy to import into other tools

### 3. Database Storage

- SQLite database for local storage
- Structured queries and filtering
- Data persistence across runs

## Web UI Features (Optional)

- View stored job postings
- Manage filter keywords
- Mark favorites
- Export data
- Real-time statistics

## Error Handling

- Rate limiting protection
- Connection error recovery
- Graceful degradation
- Comprehensive logging

## 🔒 Security

### Security Features

- **Secure credential handling** with environment variables
- **SSL verification** for all external connections
- **Non-root Docker containers** for production deployment
- **Input validation** and sanitization
- **Rate limiting** to prevent abuse
- **Session file protection** with proper permissions

### Best Practices

- **Never commit `.env` files** or sensitive credentials
- **Keep session files secure** and restrict access
- **Respect Telegram's terms of service** and rate limits
- **Don't scrape private groups** without explicit permission
- **Use HTTPS** for all web communications
- **Regular security updates** for dependencies

### Privacy and Compliance

- **Data minimization**: Only collect necessary information
- **Local storage**: All data stored locally by default
- **No external tracking**: No analytics or tracking code
- **User control**: Full control over data and configuration

## 🚀 Future Enhancements

### Planned Features

- **Machine learning** job classification and ranking
- **Company information** enrichment and verification
- **Advanced analytics** and job market insights
- **Email notifications** and alerting system
- **Slack/Discord integration** for team collaboration
- **API endpoints** for external integrations
- **Mobile application** for job monitoring
- **Advanced search** with filters and sorting
- **Job application tracking** and management
- **Salary benchmarking** and market analysis

### Plugin System

The modular architecture supports future plugins:

- **ML-based classification** plugins
- **Output integration** plugins (Slack, Discord, etc.)
- **Data enrichment** plugins (company info, etc.)
- **Custom filter** plugins for specific requirements

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors

1. **Fork and clone** the repository
2. **Set up development environment**:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```
3. **Create feature branch** and make changes
4. **Run tests** and ensure coverage
5. **Submit pull request** with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please respect:

- **Telegram's terms of service** and API usage guidelines
- **Privacy of group members** and their personal information
- **Rate limits** and fair use policies
- **Local laws** regarding data collection and privacy

Only scrape public groups/channels that you have permission to access.

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline documentation
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Ask questions and share ideas
- **Wiki**: Additional documentation and guides

### Community

- **Contributors**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: Track changes in [CHANGELOG.md](CHANGELOG.md)
- **Releases**: Check GitHub releases for updates

---

**Made with ❤️ by the open source community**

## Getting Started Examples

### Example 1: Basic Setup

1. **Set up your environment**:

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit with your credentials
   nano .env
   ```

2. **Run a single scrape**:

   ```bash
   python src/main.py --mode single --limit 50
   ```

3. **Check results**:
   - If using Telegram output: Check your saved messages
   - If using file output: Check `jobs_YYYYMMDD_HHMMSS.json`
   - If using database: Check `jobs.db`

### Example 2: Continuous Monitoring

```bash
python src/main.py --mode continuous
```

This will continuously monitor your configured channels and send new matching jobs to your Telegram chat.

### Example 3: Web Interface

```bash
# Start the web UI
python web/app.py

# Open in browser
open http://localhost:5000
```

## Troubleshooting

### Common Issues

1. **Authentication Error**

   - Ensure your API credentials are correct
   - Check that your phone number is in international format
   - Disable 2FA temporarily if needed

2. **No Messages Found**

   - Verify channel IDs are correct
   - Check that you have access to the channels
   - Adjust keyword filters if too restrictive

3. **Rate Limiting**
   - The scraper includes built-in delays
   - Reduce the number of channels if needed
   - Use longer intervals between scrapes

### Getting Channel IDs

1. Forward a message from the target channel to @userinfobot
2. The bot will reply with the channel ID
3. Add this ID to your `TARGET_CHANNELS` environment variable

### Logs

Check the log file `telegram_scraper.log` for detailed information about:

- Connection status
- Message processing
- Filtering results
- Error messages

## Advanced Configuration

### Custom Filters

You can extend the filtering logic by modifying `src/filters.py`:

```python
from src.filters import AdvancedFilter

# Create custom filter with salary range
filter = AdvancedFilter(
    keywords=['python', 'react'],
    exclude_keywords=['senior', 'lead'],
    min_salary=30000,
    max_salary=80000
)
```

### Database Queries

If using database output, you can query the data directly:

```python
import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

# Get all jobs with 'python' keyword
cursor.execute("""
    SELECT * FROM jobs
    WHERE message LIKE '%python%'
    ORDER BY created_at DESC
""")

jobs = cursor.fetchall()
```

## Performance Tips

1. **Optimize Keywords**: Use specific, relevant keywords
2. **Limit Date Range**: Use shorter time windows for faster processing
3. **Batch Processing**: Process messages in batches for better performance
4. **Database Indexing**: Add indexes for frequently queried columns

## Future Enhancements

- [ ] Machine learning-based job classification
- [ ] Salary extraction and analysis
- [ ] Company information enrichment
- [ ] Email notifications
- [ ] Slack/Discord integration
- [ ] Advanced web dashboard
- [ ] Mobile app
- [ ] API endpoints for external integrations
