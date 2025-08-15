# 🔄 Development Workflow

## 📋 Branch Strategy

### **Main Branch (`main`)**

- ✅ **Production-ready code**
- ❌ **NO session files** (secure)
- 🚀 **Connected to DigitalOcean auto-deploy**
- 🔒 **Safe for public viewing**

### **Development Branch (`development`)**

- 🛠️ **Local development code**
- 🔒 **No session files** (fully secure)
- 🧪 **Used for testing and development**
- ⚠️ **Never deployed to production**

## 🔄 Workflow Steps

### **For Local Development:**

```bash
# 1. Switch to development branch
git checkout development

# 2. Set up environment variables (first time only)
cp config_template.txt .env
# Edit .env with your credentials

# 3. Make your changes and test locally
python -m src.main --mode single
python -m src.main --mode continuous

# 4. Commit changes
git add .
git commit -m "Your development changes"
```

### **To Sync Main Changes to Development:**

```bash
# 1. Switch to development branch
git checkout development

# 2. Merge main branch into development
git merge main

# 3. If any conflicts occur, resolve them
git add .
git commit -m "Merge main into development"

# 4. Push updated development branch
git push origin development
```

### **For Production Updates:**

```bash
# 1. Switch to main branch
git checkout main

# 2. Merge development branch
git merge development

# 3. Push to trigger deployment
git push origin main
```

### **Alternative Cherry-pick Merge:**

```bash
# 1. From development branch, note commit hashes you want
git checkout development
git log --oneline

# 2. Switch to main and cherry-pick specific commits
git checkout main
git cherry-pick <commit-hash-1> <commit-hash-2>

# 3. Push to production
git push origin main
```

## 🛡️ Security Benefits

- ✅ **No session files** in any branch (100% secure)
- ✅ **Local development** uses environment variables only
- ✅ **Production deployment** uses environment-based auth
- ✅ **GitHub repo is completely secure** for public viewing
- ✅ **Zero sensitive data** committed to repository

## ⚙️ Current Setup

- **Local development**: Use `development` branch with environment variables
- **Production deployment**: DigitalOcean uses `main` branch with environment variables
- **Auto-deploy**: Enable/disable as needed in DigitalOcean dashboard

## 🔧 Authentication Configuration

Both local and production environments use these environment variables:

- `API_ID` & `API_HASH`: From https://my.telegram.org/apps
- `PHONE_NUMBER`: Your Telegram phone number
- `TELEGRAM_PHONE_CODE`: Login code from Telegram (for deployment)
- `TELEGRAM_2FA_PASSWORD`: 2FA password if enabled
- `SESSION_NAME`: Name for session file (generated automatically)

## 📝 Notes

- Always test in `development` branch first
- Both branches are completely secure (no session files)
- All authentication uses environment variables
- Repository is safe for public viewing and collaboration
