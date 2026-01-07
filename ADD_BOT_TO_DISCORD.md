# How to Add the Bot to Discord

## The Issue

Discord bots don't automatically appear in your friends list. You need to either:
1. Invite it to a server (recommended)
2. Have it in a mutual server to DM it

## Solution: Invite Bot to a Server

### Step 1: Get the Invite URL

Run this command to get your invite URL:
```bash
python get_discord_invite.py
```

Or use this URL directly:
```
https://discord.com/api/oauth2/authorize?client_id=1458283360538464266&permissions=68608&scope=bot
```

### Step 2: Invite the Bot

1. **Copy the URL above**
2. **Open it in your browser**
3. **Select your Discord server** (or create a test server)
4. **Click "Authorize"**
5. **The bot will join your server!**

### Step 3: Make Sure Bot is Running

In your terminal, run:
```bash
python main.py run
```

You should see:
```
Discord bot logged in as Yusuf Personal AI
Bot is ready to receive messages
```

### Step 4: Use the Bot

**Option A: In the Server**
- Go to any channel in your server
- Send a message: "What can you help me with?"
- The bot will respond!

**Option B: In DMs (After Inviting to Server)**
- Once the bot is in your server, you can DM it
- Find "Yusuf Personal AI" in your DMs
- Or right-click the bot in your server > "Message"

## Alternative: Create a Test Server

If you don't have a server:

1. Open Discord
2. Click the "+" icon on the left sidebar
3. Click "Create My Own" > "For me and my friends"
4. Name it (e.g., "Test Server")
5. Create it
6. Then use the invite URL above to add the bot to this server

## Verify Bot is Online

After inviting and starting the bot:
- Check your server member list
- You should see "Yusuf Personal AI" with a green "online" indicator
- If it's offline, make sure `python main.py run` is still running

## Troubleshooting

**Bot doesn't appear after inviting:**
- Make sure the bot is running (`python main.py run`)
- Check the terminal for any error messages
- Try refreshing Discord (Ctrl+R)

**Can't DM the bot:**
- Make sure the bot is in at least one server with you
- Try right-clicking the bot in your server > "Message"
- Or just use it in the server channel

**Bot doesn't respond:**
- Check that "Message Content Intent" is enabled (you did this earlier)
- Make sure the bot is online (green indicator)
- Check the terminal for errors

