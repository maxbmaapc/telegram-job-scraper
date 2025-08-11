# Telegram Bot Setup Guide

This guide will help you set up a Telegram bot to replace user authentication, making the job scraper fully containerizable.

## Why Use a Bot?

- **No authentication codes needed** - works perfectly in Docker containers
- **No rate limiting issues** - bots have different limits than user accounts
- **More reliable** - no session management problems
- **Production ready** - designed for automated systems

## Step 1: Create a Bot via @BotFather

1. **Open Telegram** and search for `@BotFather`
2. **Send the command**: `/newbot`
3. **Choose a name** for your bot (e.g., "Job Scraper Bot")
4. **Choose a username** ending with "bot" (e.g., "job_scraper_bot")
5. **Save the bot token** that BotFather gives you (starts with `5`)

## Step 2: Get Your API Credentials

1. **Go to**: https://my.telegram.org/apps
2. **Log in** with your phone number
3. **Create a new application** if you don't have one
4. **Note down** your `API_ID` and `API_HASH`

## Step 3: Update Your .env File

Replace your current `.env` file with the bot configuration:

```env
# Bot Authentication
AUTH_METHOD=bot
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Remove or comment out PHONE_NUMBER
# PHONE_NUMBER=+1234567890

# Keep your existing channel IDs and other settings
TARGET_CHANNELS=-1001786987818, -1001782596777, -1001193527943, ...
```

## Step 4: Test the Bot Locally

```bash
# Activate your virtual environment
source venv/bin/activate

# Test the bot configuration
python run.py --mode single
```

## Step 5: Deploy with Docker

```bash
# Build and start the containers
docker-compose up -d

# Check the logs
docker-compose logs -f telegram-scraper
```

## Bot Limitations

**What bots CAN do:**

- ✅ Read messages from public channels
- ✅ Send messages to users who have interacted with the bot
- ✅ Access bot-specific API methods

**What bots CANNOT do:**

- ❌ Read messages from private channels (unless added as admin)
- ❌ Send messages to users who haven't started the bot
- ❌ Access user-specific API methods

## Channel Access Requirements

For the bot to work, your target channels must be:

1. **Public channels** - bot can read these automatically
2. **Private channels** - bot must be added as a member/admin

## Troubleshooting

### Bot can't read channels

- Ensure channels are public, or
- Add the bot as a member to private channels

### Bot can't send messages

- Users must start the bot first by sending `/start`
- Or use `SEND_TO_SELF=true` to send to the bot itself

### Rate limiting

- Bots have higher rate limits than users
- Default delays should work fine

## Security Notes

- **Never share your bot token** - it gives full access to your bot
- **Bot tokens can be regenerated** if compromised
- **Bots are more secure** than user accounts for automation

## Migration from User Account

If you're switching from user authentication:

1. **Backup your current .env file**
2. **Create the bot** following Step 1
3. **Update .env** with bot credentials
4. **Test locally** before deploying
5. **Update Docker** and restart containers

## Next Steps

Once your bot is working:

1. **Monitor the logs** for any issues
2. **Adjust filter keywords** based on results
3. **Set up scheduling** for automated scraping
4. **Configure web UI** for monitoring
