# Yusuf's Personal AI Assistant

A personal AI assistant that can perform real work and continuously learns from your feedback to improve over time.

## Overview

This assistant:
- **Performs real work** - Executes tasks end-to-end (starting with email responses)
- **Connects to your assets** - Access Google Drive, Gmail via APIs
- **Learns continuously** - Improves from your edits and feedback
- **Adapts over time** - Becomes better at working with you specifically

## Architecture

The system uses a simple, learning-centered architecture:

```
Discord Interface
       │
       ▼
  Single Agent (ReAct-style)
       │
   ┌───┴───┐
   ▼       ▼
Tools   Learning Observer
   │           │
   │           ▼
   │    Guidelines Document
   │           │
   └─────┬─────┘
         ▼
      Supabase
```

### Core Components

1. **Single Agent** - ReAct-style agent that reasons, plans, and executes inline
2. **Learning Observer** - Monitors interactions and updates guidelines based on your feedback
3. **Guidelines Document** - The single source of truth for how the assistant should work with you
4. **Tools** - Gmail, Google Drive, Discord integrations

## Setup

### 1. Prerequisites

- Python 3.11+
- A Supabase account
- A Discord bot
- Google Cloud project with Gmail and Drive APIs enabled

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root with the following variables:

```bash
# LLM Configuration
LLM_PROVIDER=openai                    # or "anthropic"
LLM_MODEL=gpt-4o                      # or claude-3-opus-20240229
OPENAI_API_KEY=sk-your-key-here        # if using OpenAI
ANTHROPIC_API_KEY=sk-ant-your-key-here # if using Anthropic

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Discord Configuration
DISCORD_BOT_TOKEN=your-discord-bot-token
DISCORD_CHANNEL_ID=                    # optional, for channel-specific responses

# Google API Configuration
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
```

Required:
- `LLM_PROVIDER` and corresponding API key
- `SUPABASE_URL` and `SUPABASE_KEY`
- `DISCORD_BOT_TOKEN`

Optional:
- `GOOGLE_CREDENTIALS_PATH` (for Gmail/Drive features)

### 4. Set Up Supabase

Run the following SQL in your Supabase SQL editor to create the required tables:

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

### 5. Set Up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Enable "Message Content Intent" under Privileged Gateway Intents
5. Copy the bot token to your `.env` file
6. Go to OAuth2 > URL Generator
7. Select "bot" scope and "Send Messages", "Read Message History" permissions
8. Use the generated URL to invite the bot to your server

### 6. Set Up Google APIs (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API and Google Drive API
4. Go to APIs & Services > Credentials
5. Create OAuth 2.0 Client ID (Desktop application)
6. Download the credentials JSON file
7. Save it as `config/google_credentials.json`

On first run, the app will open a browser for OAuth authentication.

## Usage

### Start the Discord Bot

```bash
python main.py run
```

Or simply:

```bash
python main.py
```

### Other Commands

```bash
# Test the agent
python main.py test

# View current guidelines
python main.py guidelines

# View guidelines version history
python main.py history
```

### Talking to the Bot

Once running, you can message the bot directly in Discord:

- **DM the bot** - Send any message in a direct message
- **In a channel** - If `DISCORD_CHANNEL_ID` is set, message in that channel

Example interactions:

```
You: Reply to the email from John about the project update
Bot: [Searches for email, drafts response, asks for approval]

You: Make it shorter and more casual
Bot: [Revises draft based on feedback]

You: send it
Bot: [Sends the email]
```

## How Learning Works

The assistant learns from:

1. **Your edits** - When you modify a draft, the Learning Observer analyzes the diff
2. **Your feedback** - When you say things like "make it shorter" or "too formal"
3. **Your corrections** - When you point out mistakes

Learned patterns are added to the Guidelines document, which is injected into every prompt.

### View What's Been Learned

```bash
python main.py guidelines
```

### Guidelines Structure

```markdown
# Guidelines for Working with Yusuf

## Communication Style
- Use direct, concise language
- Avoid excessive formality

## Email Preferences
- Keep emails under 200 words
- Always include a clear subject line

## Patterns Learned
- [2024-01-05] User prefers shorter responses
- [2024-01-06] Use "Hi" instead of "Dear" for casual emails
```

## Project Structure

```
yusufsPersonalAIAssistant/
├── agent/
│   ├── agent.py              # Single ReAct-style agent
│   ├── prompt_builder.py     # Builds prompts with guidelines
│   └── tools.py              # Tool definitions and registry
├── learning/
│   ├── observer.py           # Learning Observer
│   ├── diff_analyzer.py      # Analyzes edits/diffs
│   └── guideline_updater.py  # Updates guidelines
├── storage/
│   ├── supabase_client.py    # Database connection
│   ├── guidelines_store.py   # Guidelines CRUD with versioning
│   └── interactions_store.py # Conversation history
├── integrations/
│   ├── gmail.py              # Gmail API integration
│   ├── google_drive.py       # Google Drive API integration
│   └── discord_bot.py        # Discord bot
├── config/
│   └── settings.py           # Configuration
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── .env.example              # Environment template
```

## Success Criteria

The system is working when:

1. **Learning happens** - After editing a draft, a guideline is added/updated
2. **Learning is used** - The next similar task produces better results
3. **Less editing over time** - Repeated task types require fewer corrections
4. **Guidelines are readable** - You can read and understand what the system learned
5. **Guidelines can be edited** - You can manually update guidelines

## Troubleshooting

### Bot not responding

- Check that the bot token is correct in `.env`
- Ensure "Message Content Intent" is enabled in Discord Developer Portal
- Verify the bot is in your server with correct permissions

### Gmail/Drive not working

- Ensure OAuth credentials are in the correct path
- Delete `config/gmail_token.json` or `config/drive_token.json` to re-authenticate
- Check that APIs are enabled in Google Cloud Console

### Database errors

- Verify Supabase URL and key are correct
- Ensure tables are created (run the SQL from setup step 4)

