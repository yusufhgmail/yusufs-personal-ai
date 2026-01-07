# Starting Your Personal AI Assistant Bot

## ✅ Everything is Configured!

- ✅ OpenAI API key
- ✅ Supabase database (tables created)
- ✅ Discord bot token (verified)
- ✅ Message Content Intent enabled

## Start the Bot

Run this command:

```bash
python main.py run
```

The bot will:
- Connect to Discord
- Load your guidelines from Supabase
- Start listening for messages

## How to Use

### Option 1: Direct Messages (DMs)
1. Open Discord
2. Find "Yusuf Personal AI" in your DMs or friends list
3. Send a message to the bot
4. The bot will respond!

### Option 2: Server Channel
If you set `DISCORD_CHANNEL_ID` in `.env`, the bot will only respond in that channel.

## Test Commands

Try these:
- "What can you help me with?"
- "Reply to the email from [someone] about [topic]"
- "Help me draft an email"

## Troubleshooting

If the bot doesn't respond:
1. Check the bot is online in Discord (should show as online)
2. Make sure you've invited the bot to your server (if using a channel)
3. Check the console for error messages

## Stop the Bot

Press `Ctrl+C` in the terminal to stop the bot.

