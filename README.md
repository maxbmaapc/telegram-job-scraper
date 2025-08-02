# Telegram Job Scraper

A Python-based Telegram job scraper that monitors groups/channels for job postings matching specific keywords and filters.

## Features

- 🔍 **Keyword Filtering**: Case-insensitive matching for job-related keywords
- 📅 **Date Filtering**: Filter messages by timestamp (last X days/hours)
- 📱 **Telegram Integration**: Uses Telethon for full user access to Telegram
- 💾 **Multiple Output Options**: Send to self, save to file, or store in database
- 🏗️ **Modular Architecture**: Easy to extend with new filters and output methods
- 🌐 **Web UI** (Optional): Flask-based web interface for management

## Project Structure

```
telegram-job-scraper/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration and settings
│   ├── filters.py           # Filtering logic
│   ├── telegram_client.py   # Telegram API client
│   ├── output.py            # Output delivery methods
│   └── utils.py             # Utility functions
├── tests/
│   └── test_filters.py      # Unit tests
├── web/                     # Optional web UI
│   ├── app.py
│   ├── templates/
│   └── static/
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Telegram account
- Telegram API credentials (API ID and API Hash)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/maxbmaapc/telegram-job-scraper.git
   cd telegram-job-scraper
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Get Telegram API credentials**

   - Go to https://my.telegram.org/apps
   - Create a new application
   - Note your API ID and API Hash

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials and settings
   ```

5. **Configure target groups/channels**
   - Add group/channel IDs to your `.env` file
   - Or modify `src/config.py` to include your target channels

### Configuration

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

# Logging
LOG_LEVEL=INFO

# Web UI Settings (optional)
WEB_HOST=localhost
WEB_PORT=5000
```

## Usage

### Basic Usage

```bash
python src/main.py
```

### With Custom Configuration

```bash
python src/main.py --config custom_config.json
```

### Run Tests

```bash
pytest tests/
```

### Start Web UI (Optional)

```bash
python web/app.py
```

## Filtering Logic

The scraper uses the following filtering criteria:

### Keywords

- Case-insensitive matching
- Supports multiple keywords
- Configurable via environment variables

### Date Filtering

- Filters messages by timestamp
- Configurable time window (hours/days)
- Default: last 24 hours

### Future Extensions

- Location-based filtering
- Salary range filtering
- Tech stack matching
- Company filtering

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

## Security Considerations

- Never commit `.env` files
- Keep session files secure
- Respect Telegram's terms of service
- Don't scrape private groups without permission

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect Telegram's terms of service and the privacy of group members. Only scrape public groups/channels that you have permission to access.

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
