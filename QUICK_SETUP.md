# Quick Setup Guide

## What I Can Do For You

I've created helper scripts to automate what's possible. Here's what we can do:

### ✅ Already Done
- OpenAI API key is ready to use

### 🔧 Setup Scripts Created

1. **`setup_env.py`** - Interactive script to create .env file
2. **`setup_supabase.py`** - Helps set up Supabase database
3. **`setup_discord.py`** - Helps verify Discord bot token

## Step-by-Step Setup

### 1. Create .env File

Since .env is in .gitignore, run:

```bash
python setup_env.py
```

This will:
- Use your OpenAI key (already provided)
- Prompt for Supabase credentials
- Prompt for Discord bot token
- Create the .env file

### 2. Set Up Supabase

**Option A: Via Web (Easiest)**
1. Go to https://supabase.com/dashboard
2. Create a new project (or use existing)
3. Go to SQL Editor
4. Run the SQL from `storage/supabase_client.py` (or use `supabase_setup.sql`)

**Option B: Via Supabase CLI (if installed)**
```bash
# Install Supabase CLI (Windows with Scoop)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# Or download from: https://github.com/supabase/cli/releases
```

Then run:
```bash
python setup_supabase.py
```

### 3. Set Up Discord Bot

**Via Web (Required - no CLI alternative)**
1. Go to https://discord.com/developers/applications
2. Create new application → Add Bot
3. Enable "Message Content Intent"
4. Copy the bot token

Then verify it:
```bash
python setup_discord.py
```

This will verify your token is valid.

### 4. Set Up Google APIs (Optional)

**Via Web (Required - OAuth needs browser)**
1. Go to https://console.cloud.google.com
2. Create project → Enable Gmail API + Drive API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download JSON → save as `config/google_credentials.json`

On first run, the app will open a browser for OAuth.

## Quick Start Commands

```bash
# 1. Create .env file
python setup_env.py

# 2. Set up Supabase (manual SQL or CLI)
python setup_supabase.py

# 3. Verify Discord bot
python setup_discord.py

# 4. Test the system
python main.py test

# 5. Run the bot
python main.py run
```

## What Each Service Needs

### Supabase
- ✅ Can be done via web interface (SQL Editor)
- ⚠️ CLI available but requires separate installation
- **Status**: Manual setup required (5 minutes)

### Discord
- ❌ No official CLI for creating bots
- ✅ Must use web interface
- ✅ Can verify token via API (script does this)
- **Status**: Manual setup required (5 minutes)

### Google
- ❌ OAuth requires browser interaction
- ⚠️ gcloud CLI exists but doesn't help with OAuth
- ✅ Can download credentials via web
- **Status**: Manual setup required (10 minutes)

## Summary

**What I automated:**
- ✅ .env file creation (interactive script)
- ✅ Token verification (Discord)
- ✅ SQL extraction and instructions (Supabase)

**What requires manual steps:**
- Supabase: Create project + run SQL (web interface)
- Discord: Create bot + get token (web interface)  
- Google: Create project + download credentials (web interface)

All of these are quick web-based setups. The scripts guide you through each step!

