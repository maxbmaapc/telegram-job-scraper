# 🔄 Development Workflow

## 📋 Branch Strategy

### **Main Branch (`main`)**

- ✅ **Production-ready code**
- ❌ **NO session files** (secure)
- 🚀 **Connected to DigitalOcean auto-deploy**
- 🔒 **Safe for public viewing**

### **Development Branch (`development`)**

- 🛠️ **Local development code**
- ✅ **Contains session files** for local testing
- 🧪 **Used for testing and development**
- ⚠️ **Never deployed to production**

## 🔄 Workflow Steps

### **For Local Development:**

```bash
# 1. Switch to development branch
git checkout development

# 2. Make your changes and test locally
python -m src.main --mode single
python -m src.main --mode continuous

# 3. Commit changes (including session file if needed)
git add .
git commit -m "Your development changes"
```

### **For Production Updates:**

```bash
# 1. Switch to main branch
git checkout main

# 2. Merge development branch (but exclude session file)
git merge development

# 3. If session file got merged, remove it
git rm --cached telegram_job_scraper.session
git commit -m "Remove session file from main"

# 4. Push to trigger deployment
git push origin main
```

### **Alternative Secure Merge:**

```bash
# 1. From development branch, create patch without session file
git checkout development
git diff main..development -- . ':!telegram_job_scraper.session' > changes.patch

# 2. Switch to main and apply patch
git checkout main
git apply changes.patch
git add .
git commit -m "Apply development changes"
rm changes.patch

# 3. Push to production
git push origin main
```

## 🛡️ Security Benefits

- ✅ **Session file never exposed** in public main branch
- ✅ **Local development works** with session file
- ✅ **Production deployment** uses environment-based auth
- ✅ **GitHub repo is secure** for public viewing

## ⚙️ Current Setup

- **Local development**: Use `development` branch with session file
- **Production deployment**: DigitalOcean uses `main` branch with environment variables
- **Auto-deploy**: Currently **DISABLED** for safety

## 🔧 DigitalOcean Configuration

The production app uses these environment variables instead of session file:

- `TELEGRAM_PHONE_CODE`: Login code from Telegram
- `TELEGRAM_2FA_PASSWORD`: 2FA password if enabled
- `SESSION_NAME`: Name for session file (generated automatically)

## 📝 Notes

- Always test in `development` branch first
- Keep `main` branch clean and secure
- Session file is automatically ignored in `main` via `.gitignore`
- Production relies on environment variables for authentication
