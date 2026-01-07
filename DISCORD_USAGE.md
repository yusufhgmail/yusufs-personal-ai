# How to Use Your Discord Bot

## Two Ways to Use the Bot

### Option 1: Direct Messages (DMs) - Easiest!

**No invitation needed!** The bot works in DMs automatically.

1. **Find the bot in Discord:**
   - Open Discord
   - Look for "Yusuf Personal AI" in your friends/DMs list
   - If you don't see it, you may need to add it as a friend first

2. **Start a conversation:**
   - Click on "Yusuf Personal AI" to open a DM
   - Send a message like: "What can you help me with?"
   - The bot will respond!

### Option 2: Server Channel

If you want to use the bot in a Discord server:

1. **Invite the bot to your server:**
   - Go to https://discord.com/developers/applications
   - Select your application: "Yusuf Personal AI yai26"
   - Go to "OAuth2" > "URL Generator"
   - Under "Scopes", select: `bot`
   - Under "Bot Permissions", select:
     - ✅ Send Messages
     - ✅ Read Message History
     - ✅ View Channels
   - Copy the generated URL at the bottom
   - Open the URL in your browser
   - Select your Discord server
   - Click "Authorize"

2. **Set the channel (optional):**
   - If you want the bot to only respond in a specific channel:
   - Get the channel ID (right-click channel > Copy ID - need Developer Mode enabled)
   - Add to `.env`: `DISCORD_CHANNEL_ID=your-channel-id`
   - Or leave empty to respond in any channel

3. **Use it:**
   - Go to your Discord server
   - Send a message in the channel
   - The bot will respond!

## How to Send Messages

Once the bot is running and you've connected to it:

### In DMs:
- Just send a message directly to "Yusuf Personal AI"
- Example: "Help me draft an email"

### In a Server:
- Send a message in the channel where the bot is active
- The bot will respond in that channel

## Example Commands to Try

- "What can you help me with?"
- "Search for emails from [someone]"
- "Reply to the email from [X] about [Y]"
- "Help me draft an email"
- "Find files in my Drive"

## Troubleshooting

### Bot doesn't respond in DMs:
- Make sure the bot is online (check the bot's status in Discord)
- Make sure you've started the bot: `python main.py run`
- Try restarting the bot

### Bot doesn't respond in server:
- Make sure you've invited the bot to the server
- Check that the bot has permissions in that channel
- If you set `DISCORD_CHANNEL_ID`, make sure you're messaging in that channel

### Can't find the bot:
- The bot name is "Yusuf Personal AI" (from your Discord Developer Portal)
- If you can't see it, you may need to add it as a friend or invite it to a server first

