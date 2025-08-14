# DigitalOcean App Platform Deployment Guide

## Prerequisites

1. **DigitalOcean Account** - Sign up at [digitalocean.com](https://digitalocean.com)
2. **GitHub Repository** - Your code must be in a GitHub repo
3. **Telegram API Credentials** - Get from [my.telegram.org/apps](https://my.telegram.org/apps)

## Step 1: Prepare Your Repository

1. **Update the app.yaml file:**

   - Replace `your-username/telegram-job-scraper` with your actual GitHub username and repo name
   - Update any environment variables as needed

2. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "Add DigitalOcean deployment configuration"
   git push origin main
   ```

## Step 2: Deploy to DigitalOcean

1. **Go to DigitalOcean App Platform:**

   - Login to [cloud.digitalocean.com](https://cloud.digitalocean.com)
   - Click "Apps" in the left sidebar
   - Click "Create App"

2. **Connect GitHub:**

   - Choose "GitHub" as source
   - Select your repository: `telegram-job-scraper`
   - Select branch: `main`

3. **Configure App:**

   - **App Name**: `telegram-job-scraper`
   - **Region**: Choose closest to your target audience
   - **Plan**: Start with `Basic` ($12/month)

4. **Environment Variables:**
   Set these required variables:

   ```
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   PHONE_NUMBER=+1234567890
   TARGET_CHANNELS=-1001234567890,-1009876543210
   TARGET_USER_ID=123456789
   TELEGRAM_PHONE_CODE=123456
   TELEGRAM_2FA_PASSWORD=your_2fa_password_if_enabled
   ```

5. **Deploy:**
   - Click "Create Resources"
   - Wait for build and deployment (5-10 minutes)

## Step 3: Get Your Phone Code

### **How to Get the Phone Code:**

1. **Start the deployment** on DigitalOcean
2. **Check the logs** - you'll see "Please enter the code you received"
3. **Go to Telegram** on your phone
4. **Look for the SMS/Telegram message** with the 6-digit code
5. **Copy the code** (e.g., `123456`)
6. **Go back to DigitalOcean** and add the environment variable:
   ```
   TELEGRAM_PHONE_CODE=123456
   ```
7. **Redeploy** the app

### **Important Notes:**

- **Phone codes expire** after a few minutes
- **You need to be quick** to get the code and set it
- **Codes are one-time use** - you'll need a new one for each fresh deployment
- **If you have 2FA enabled**, also set `TELEGRAM_2FA_PASSWORD`

## Step 4: Verify Deployment

1. **Check App Status:**

   - Go to your app dashboard
   - Verify status is "Running"
   - Check logs for any errors

2. **Test Health Endpoint:**

   - Visit: `https://your-app-name.ondigitalocean.app/health`
   - Should return: `{"status": "healthy", "service": "Telegram Job Scraper"}`

3. **Check Telegram:**
   - Verify you receive job postings
   - Check that filtering is working correctly

## Step 5: Monitor and Maintain

1. **View Logs:**

   - In your app dashboard, click "Runtime Logs"
   - Monitor for errors or issues

2. **Scale if Needed:**

   - Increase instance count for better performance
   - Upgrade to larger instance size if needed

3. **Update App:**
   - Push changes to GitHub
   - DigitalOcean automatically redeploys

## Configuration Options

### **Instance Sizes:**

- `basic-xxs`: $12/month (1 vCPU, 512MB RAM) - **Recommended to start**
- `basic-xs`: $18/month (1 vCPU, 1GB RAM)
- `basic-s`: $24/month (1 vCPU, 2GB RAM)

### **Environment Variables:**

```yaml
# Required
API_ID: Your Telegram API ID
API_HASH: Your Telegram API Hash
PHONE_NUMBER: Your phone number (+1234567890)
TARGET_CHANNELS: Comma-separated channel IDs
TARGET_USER_ID: Your Telegram user ID

# New: Automatic Authentication
TELEGRAM_PHONE_CODE: The 6-digit code Telegram sends you
TELEGRAM_2FA_PASSWORD: Your 2FA password (if enabled)

# Optional (with defaults)
FILTER_KEYWORDS: "python,javascript,js,react,developer,software engineer,job,hire,remote"
DATE_FILTER_HOURS: "24"
OUTPUT_METHOD: "telegram"
LOG_LEVEL: "INFO"
SCHEDULE_INTERVAL_MINUTES: "30"
```

## Troubleshooting

### **Common Issues:**

1. **Build Fails:**

   - Check requirements.txt has all dependencies
   - Verify Dockerfile syntax
   - Check runtime logs

2. **App Won't Start:**

   - Verify all environment variables are set
   - Check if Telegram credentials are correct
   - Look for authentication errors in logs

3. **Authentication Fails:**

   - **Phone Code Issues**: Make sure `TELEGRAM_PHONE_CODE` is set and valid
   - **2FA Issues**: Set `TELEGRAM_2FA_PASSWORD` if you have 2FA enabled
   - **Code Expired**: Get a fresh code and update the environment variable

4. **No Messages Received:**
   - Verify TARGET_USER_ID is correct
   - Check if bot account is authenticated
   - Verify target channels are accessible

### **Useful Commands:**

```bash
# Check app status
doctl apps get your-app-id

# View logs
doctl apps logs your-app-id

# Update environment variables
doctl apps update your-app-id --set-env-vars KEY=value
```

## Cost Estimation

- **Basic Plan**: $12/month
- **Data Transfer**: Included (1TB)
- **Storage**: Included (1GB)
- **Total**: ~$12/month

## Security Notes

1. **Environment Variables**: Never commit sensitive data to GitHub
2. **Phone Codes**: Temporary and expire quickly
3. **2FA Passwords**: Store securely, consider disabling 2FA temporarily
4. **Telegram Sessions**: Stored securely in DigitalOcean's environment
5. **Network**: App runs in DigitalOcean's secure network
6. **Updates**: Automatic security updates applied

## Support

- **DigitalOcean Docs**: [docs.digitalocean.com](https://docs.digitalocean.com)
- **Community**: [digitalocean.com/community](https://digitalocean.com/community)
- **Support Tickets**: Available in your DigitalOcean dashboard
