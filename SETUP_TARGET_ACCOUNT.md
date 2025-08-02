# Setting Up Bot to Send Messages to Personal Account

This guide explains how to configure your Telegram job scraper bot to send messages to your personal account instead of sending them to itself.

## Configuration Changes

### 1. Environment Variables

Add these new environment variables to your `.env` file:

```bash
# Target Personal Account (where to send messages)
TARGET_USER_ID=123456789  # Your personal Telegram user ID
# OR
TARGET_USERNAME=your_username  # Your personal Telegram username (without @)
# OR
TARGET_PHONE_NUMBER=+1234567890  # Your personal phone number

# Output Settings
SEND_TO_SELF=false  # Set to false to send to target account instead of bot itself
```

### 2. Choose Your Target Method

You can specify your personal account in one of three ways:

#### Option A: User ID (Recommended)

```bash
TARGET_USER_ID=123456789
```

To find your user ID:

1. Send a message to @userinfobot on Telegram
2. It will reply with your user ID

#### Option B: Username

```bash
TARGET_USERNAME=your_username
```

- Use your username without the @ symbol
- Make sure your account is public or the bot account is in your contacts

#### Option C: Phone Number

```bash
TARGET_PHONE_NUMBER=+1234567890
```

- Use the same format as your phone number
- The bot account must have your number in its contacts

### 3. Complete Example Configuration

```bash
# Bot Account Credentials
API_ID=your_bot_api_id
API_HASH=your_bot_api_hash
PHONE_NUMBER=+bot_phone_number

# Target Channels
TARGET_CHANNELS=-1001234567890,-1009876543210

# Your Personal Account (where to receive messages)
TARGET_USER_ID=123456789

# Output Settings
OUTPUT_METHOD=telegram
SEND_TO_SELF=false

# Filter Keywords
FILTER_KEYWORDS=python,developer,software engineer,job,hire,remote
```

## How It Works

1. **Bot Account**: The account specified by `API_ID`, `API_HASH`, and `PHONE_NUMBER` will:

   - Monitor the target channels
   - Filter messages based on keywords
   - Send matching job postings to your personal account

2. **Personal Account**: The account specified by `TARGET_USER_ID`, `TARGET_USERNAME`, or `TARGET_PHONE_NUMBER` will:
   - Receive all filtered job postings
   - Get formatted messages with job details

## Important Notes

1. **Privacy Settings**: Make sure your personal account can receive messages from the bot account:

   - Add the bot account to your contacts, or
   - Make your account public, or
   - Use your user ID (most reliable method)

2. **Rate Limiting**: The bot includes delays between messages to avoid Telegram's rate limits

3. **Fallback**: If `SEND_TO_SELF=true`, messages will be sent to the bot account itself (original behavior)

4. **Validation**: The bot will validate that a target entity is configured when `SEND_TO_SELF=false`

## Troubleshooting

### "Could not resolve target entity" Error

- Check that your user ID, username, or phone number is correct
- Ensure the bot account can access your personal account
- Try using user ID instead of username for better reliability

### "No target entity configured" Error

- Make sure you've set one of: `TARGET_USER_ID`, `TARGET_USERNAME`, or `TARGET_PHONE_NUMBER`
- Ensure `SEND_TO_SELF=false` is set

### Messages not being received

- Check your Telegram privacy settings
- Verify the bot account is in your contacts
- Try using user ID instead of username/phone number
