# Telegram Job Scraper

A robust, production-ready Python-based Telegram job scraper that monitors groups/channels for job postings matching specific keywords and filters. Built with scalability, maintainability, and extensibility in mind.

## 🚀 Features

- 🔍 **Smart Job Filtering**: Advanced keyword matching specifically for developer/engineer roles
- 🚫 **Resume Detection**: Automatically excludes CVs and resumes with comprehensive keyword detection
- 👨‍💻 **Junior Developer Focus**: Targets only "junior developer/engineer" positions (excludes general "junior" roles)
- 🌐 **Web3 Support**: Includes web3/blockchain developer roles when combined with developer keywords
- 📱 **Telegram UserBot**: Full access to public channels using Telethon
- 🤖 **Auto-Authentication**: Automatic login code handling for deployment
- ☁️ **DigitalOcean Ready**: Optimized for App Platform deployment with health checks
- 💾 **Database Storage**: SQLite database with message deduplication
- 📊 **Comprehensive Logging**: Detailed debug logs for filtering decisions
- 🔒 **Secure Session Handling**: Development/production branch workflow for session files
- ⚡ **Real-time Monitoring**: Continuous mode for live job notifications
- 🧪 **Tested Filters**: Extensively tested filtering logic with fallback imports

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
│   ├── config.py            # Configuration management with fallbacks
│   ├── filters.py           # Advanced job filtering logic
│   ├── salary_extractor.py  # Salary extraction utilities
│   ├── logging_config.py    # Centralized logging configuration
│   ├── telegram_client.py   # Telegram API client with auto-auth
│   ├── output.py            # Output delivery methods
│   ├── scheduler.py         # Job scheduling
│   └── utils.py             # Utility functions
├── tests/                   # Test suite
│   ├── test_filters.py      # Filter logic tests
│   └── test_salary_extractor.py  # Salary extraction tests
├── web/                     # Web interface for health checks
│   └── app.py               # Flask application with health endpoint
├── .do/                     # DigitalOcean App Platform configuration
│   └── app.yaml             # App platform specification
├── logs/                    # Application logs
├── config_template.txt      # Environment variables template
├── requirements.txt         # Python dependencies
├── Dockerfile.do           # DigitalOcean-optimized Dockerfile
├── DEPLOYMENT.md           # DigitalOcean deployment guide
├── DEVELOPMENT_WORKFLOW.md # Git workflow with session file handling
├── .python-version         # Python version specification
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Telegram account
- Telegram API credentials (API ID and API Hash)
- DigitalOcean account (for cloud deployment) or local environment

### Option 1: DigitalOcean App Platform (Recommended for Production)

1. **Fork and configure**:

   ```bash
   # Fork this repository on GitHub
   # Clone your fork
   git clone https://github.com/your-username/telegram-job-scraper.git
   cd telegram-job-scraper
   ```

2. **Follow deployment guide**:
   
   See [DEPLOYMENT.md](DEPLOYMENT.md) for complete DigitalOcean setup instructions.

3. **Key benefits**:
   - ✅ Automatic deployments from GitHub
   - ✅ Built-in health checks and monitoring  
   - ✅ Secure environment variable management
   - ✅ Auto-scaling and reliability

### Option 2: Local Development

**Use the `development` branch for local work (includes session file):**

1. **Clone and setup**:

   ```bash
   git clone https://github.com/maxbmaapc/telegram-job-scraper.git
   cd telegram-job-scraper
   git checkout development  # Important: Use development branch
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
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

5. **Run single scrape test**:
   ```bash
   python -m src.main --mode single
   ```

6. **Run continuous monitoring**:
   ```bash
   python -m src.main --mode continuous
   ```

See [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) for the complete development workflow.

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. See [config_template.txt](config_template.txt) for a complete list of all available options with detailed explanations.

**Quick setup:**
```bash
cp config_template.txt .env
# Edit .env with your specific values
```

**Essential variables:**
- `API_ID` & `API_HASH`: From https://my.telegram.org/apps
- `PHONE_NUMBER`: Your Telegram phone number
- `TARGET_CHANNELS`: Comma-separated channel IDs to monitor
- `TARGET_USER_ID`: Where to send filtered job notifications
- `FILTER_KEYWORDS`: Keywords to match in job posts

**For DigitalOcean deployment:**
- `TELEGRAM_PHONE_CODE`: Login code for automatic authentication
- `TELEGRAM_2FA_PASSWORD`: Two-factor auth password (if enabled)

See [config_template.txt](config_template.txt) for detailed descriptions and examples.

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
# Single scraping session (test mode)
python -m src.main --mode single

# Continuous monitoring (production mode)
python -m src.main --mode continuous
```

### DigitalOcean Deployment

1. **Follow [DEPLOYMENT.md](DEPLOYMENT.md)** for complete setup
2. **Monitor via DigitalOcean dashboard** - logs, metrics, health checks
3. **Auto-deploys** from GitHub main branch (when enabled)

### Local Development

```bash
# Switch to development branch (has session file)
git checkout development

# Test the filters and scraping
python -m src.main --mode single

# Run continuous monitoring locally  
python -m src.main --mode continuous
```

See [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) for Git workflow with session files.

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

### Health Check Endpoint

The Flask web server provides a health check endpoint for monitoring:

```bash
# Start web interface (for health checks)
python -m web.app

# Health check endpoint
curl http://localhost:8080/health
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

## 🚀 Deployment

### DigitalOcean App Platform (Recommended)

This application is optimized for DigitalOcean App Platform deployment:

**Key Features:**
- ✅ **Automatic deployments** from GitHub
- ✅ **Built-in health checks** and monitoring
- ✅ **Secure environment variable** management
- ✅ **Auto-scaling** and high availability
- ✅ **Integrated logging** and metrics

**Setup:** Follow the complete guide in [DEPLOYMENT.md](DEPLOYMENT.md)

### Production Considerations

- **Health monitoring**: `/health` endpoint for uptime checks
- **Automatic restarts**: App Platform handles failures gracefully
- **Environment variables**: Secure credential management
- **Git-based deployment**: Clean separation of dev/prod branches
- **Session file security**: Development branch workflow

### Monitoring and Observability

- **Detailed logging**: All filtering decisions and errors logged
- **Health endpoint**: HTTP health checks for monitoring
- **DigitalOcean metrics**: Built-in performance monitoring
- **Real-time alerts**: Via DigitalOcean dashboard

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
