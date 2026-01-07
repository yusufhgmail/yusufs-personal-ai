# Get Your Discord Bot Token

## Good News: Your Bot Already Exists! ✅

I can see from your screenshot that the bot "Yusuf Personal AI" (#8735) has already been created. That's why there's no "Add Bot" button - it's already there!

## Next Steps:

### 1. Get Your Bot Token

On the Bot page you're currently viewing:

1. **Find the "Token" section** (it's on the page, below the bot username)
2. **Click the blue "Reset Token" button**
3. **A popup will appear** asking you to confirm
4. **Click "Yes" or "Confirm"**
5. **The token will appear** in the grey text field below
6. **Copy the token immediately** - you can only see it once!

The token will look something like:
```
MTQ1ODI4MzM2MDUzODQ2NDI2Ni5HZXQuMTIzNDU2Nzg5MGFiY2RlZg
```

### 2. Enable Message Content Intent (REQUIRED)

While you're on the Bot page:

1. **Scroll down to "Privileged Gateway Intents"**
2. **Find "Message Content Intent"** (it's currently OFF/grey)
3. **Click the toggle to turn it ON** (it should turn blue)
4. **Click "Save Changes"** at the bottom

⚠️ **This is REQUIRED** - without this, your bot won't be able to read message content!

### 3. Add Token to .env File

Once you have the token:

1. Open your `.env` file
2. Add this line (or update if it exists):
   ```
   DISCORD_BOT_TOKEN=your-token-here
   ```
3. Save the file

### 4. Verify It Works

Run this command to verify your token:
```bash
python setup_discord.py
```

This will test if your token is valid and the bot is properly configured.

## Quick Summary:

✅ Bot exists: "Yusuf Personal AI"  
⬜ Get token: Click "Reset Token" → Copy it  
⬜ Enable Message Content Intent: Toggle it ON  
⬜ Add to .env: `DISCORD_BOT_TOKEN=your-token`  
⬜ Verify: `python setup_discord.py`

