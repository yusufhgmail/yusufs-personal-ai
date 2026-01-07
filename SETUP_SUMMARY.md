# Setup Summary - What Can Be Automated vs Manual

## ✅ What I Can Do (Automated)

### 1. OpenAI API Key
- ✅ **DONE**: Your OpenAI key is already configured in the `.env` template
- ✅ Created `create_env_template.py` to generate `.env` file

### 2. Environment File Creation
- ✅ Created `.env` template with your OpenAI key pre-filled
- ✅ Just need to fill in Supabase and Discord credentials

### 3. Helper Scripts
- ✅ `setup_supabase.py` - Extracts SQL and provides setup instructions
- ✅ `setup_discord.py` - Can verify Discord bot tokens via API
- ✅ `create_env_template.py` - Creates .env file with OpenAI key

## ❌ What Requires Manual Steps

### 1. Supabase Setup
**Why manual?**
- Need to create account/project on Supabase website
- Need to run SQL in their SQL Editor (web interface)
- CLI exists but requires separate installation and linking

**What you need to do:**
1. Go to https://supabase.com → Create account → New project
2. Go to SQL Editor → Run the SQL from `storage/supabase_client.py`
3. Go to Settings → API → Copy URL and anon key
4. Add to `.env` file

**Time:** ~5 minutes

### 2. Discord Bot Setup
**Why manual?**
- Discord doesn't provide CLI for creating bots
- Must use web interface at discord.com/developers
- Bot creation requires OAuth flow (web-based)

**What you need to do:**
1. Go to https://discord.com/developers/applications
2. Create new application → Add Bot
3. Enable "Message Content Intent"
4. Copy bot token → Add to `.env`
5. Generate OAuth URL → Invite bot to server

**Time:** ~5 minutes

**What I can help with:**
- ✅ Verify token is valid (via `setup_discord.py`)
- ✅ Test bot connection

### 3. Google APIs Setup
**Why manual?**
- OAuth 2.0 requires browser-based authentication
- Must download credentials JSON from Google Cloud Console
- First-time OAuth flow opens browser (by design)

**What you need to do:**
1. Go to https://console.cloud.google.com
2. Create project → Enable Gmail API + Drive API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download JSON → Save as `config/google_credentials.json`
5. On first run, app will open browser for OAuth

**Time:** ~10 minutes

**What I can help with:**
- ✅ Verify credentials file exists
- ✅ Test API connections after setup

## 🚀 Quick Start

### Step 1: Create .env File
```bash
python create_env_template.py
```
This creates `.env` with your OpenAI key already filled in.

### Step 2: Fill in Credentials
Edit `.env` and add:
- `SUPABASE_URL` and `SUPABASE_KEY` (from Supabase dashboard)
- `DISCORD_BOT_TOKEN` (from Discord Developer Portal)

### Step 3: Set Up Supabase
```bash
python setup_supabase.py
```
This will show you the SQL to run in Supabase SQL Editor.

### Step 4: Verify Discord Bot
```bash
python setup_discord.py
```
This will verify your Discord bot token is valid.

### Step 5: Test
```bash
python main.py test
```

### Step 6: Run
```bash
python main.py run
```

## Summary

**Automated:**
- ✅ .env file creation with OpenAI key
- ✅ SQL extraction for Supabase
- ✅ Token verification for Discord
- ✅ Setup instructions and helper scripts

**Manual (but quick):**
- ⚠️ Supabase: Create project + run SQL (5 min)
- ⚠️ Discord: Create bot + get token (5 min)
- ⚠️ Google: Create project + download credentials (10 min, optional)

**Total manual setup time: ~10-20 minutes**

All manual steps are straightforward web-based setups. The scripts guide you through each one!

