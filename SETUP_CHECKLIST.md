# Setup Checklist - What's Needed to Run the System

## ✅ Code Implementation
- [x] All Python modules implemented
- [x] Dependencies listed in requirements.txt
- [x] Main entry point (main.py)

## 🔴 Required Configuration (Must Have)

### 1. Environment Variables (`.env` file)
Create a `.env` file in the project root with:

```bash
# LLM Configuration (REQUIRED)
LLM_PROVIDER=openai                    # or "anthropic"
LLM_MODEL=gpt-4-turbo-preview          # or claude-3-opus-20240229
OPENAI_API_KEY=sk-your-actual-key      # if using OpenAI
# OR
ANTHROPIC_API_KEY=sk-ant-your-key      # if using Anthropic

# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Discord Configuration (REQUIRED)
DISCORD_BOT_TOKEN=your-discord-bot-token
DISCORD_CHANNEL_ID=                    # optional, leave empty for DMs only
```

**Status**: ❌ `.env` file does not exist

### 2. Supabase Database Setup (REQUIRED)
1. Create a Supabase account at https://supabase.com
2. Create a new project
3. Go to SQL Editor
4. Run this SQL to create the tables:

```sql
-- Guidelines table with version history
CREATE TABLE guidelines (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    diff_from_previous TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for version lookups
CREATE INDEX idx_guidelines_version ON guidelines(version DESC);

-- Interactions table for conversation history
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for conversation lookups
CREATE INDEX idx_interactions_conversation ON interactions(conversation_id, created_at);
```

5. Get your Supabase URL and anon key from Project Settings > API

**Status**: ❓ Need to verify if Supabase project exists and tables are created

### 3. Discord Bot Setup (REQUIRED)
1. Go to https://discord.com/developers/applications
2. Click "New Application" → name it (e.g., "Personal AI Assistant")
3. Go to "Bot" section → Click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - ✅ **Message Content Intent** (REQUIRED)
5. Click "Reset Token" and copy the token → add to `.env` as `DISCORD_BOT_TOKEN`
6. Go to "OAuth2" → "URL Generator"
   - Select scope: `bot`
   - Select permissions: `Send Messages`, `Read Message History`, `View Channels`
   - Copy the generated URL and open it in browser to invite bot to your server
   - OR: The bot will work in DMs if you have it as a friend

**Status**: ❓ Need to verify if Discord bot is created and token is available

## 🟡 Optional Configuration (For Full Features)

### 4. Google APIs Setup (Optional - for Gmail/Drive features)
If you want email and Drive features:

1. Go to https://console.cloud.google.com
2. Create a new project (or select existing)
3. Enable APIs:
   - Gmail API
   - Google Drive API
4. Go to "APIs & Services" → "Credentials"
5. Click "Create Credentials" → "OAuth 2.0 Client ID"
6. Application type: "Desktop app"
7. Download the JSON file
8. Save it as `config/google_credentials.json`
9. On first run, the app will open a browser for OAuth authentication

**Status**: ❓ Optional - only needed for Gmail/Drive features

## 🧪 Testing the Setup

### Quick Test (Without Discord)
```bash
# Test that imports work
python -c "from agent import Agent; print('OK')"

# Test guidelines view (will fail if Supabase not configured)
python main.py guidelines
```

### Full Test (With Discord)
```bash
# Start the bot
python main.py run
```

## Common Issues

### "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`

### "SUPABASE_URL is required"
- Create `.env` file with Supabase credentials

### "DISCORD_BOT_TOKEN is required"
- Create Discord bot and add token to `.env`

### "Message Content Intent" error
- Enable "Message Content Intent" in Discord Developer Portal

### Bot doesn't respond
- Check bot is online in Discord
- Check bot has permissions in the channel
- Check `DISCORD_CHANNEL_ID` is correct (or leave empty for DMs)

### Database connection errors
- Verify Supabase URL and key are correct
- Check tables were created (run the SQL)
- Check internet connection

## Next Steps

1. **Create `.env` file** with all required variables
2. **Set up Supabase** and run the SQL to create tables
3. **Create Discord bot** and get the token
4. **Test**: Run `python main.py test` to verify basic functionality
5. **Start**: Run `python main.py run` to start the Discord bot

Once these are done, the system should be fully functional!

