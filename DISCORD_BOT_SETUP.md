# Discord Bot Setup - Step by Step

## You're Currently On: "General Information" Page

From the screenshot, I can see you're on the **General Information** page. To add a bot, you need to go to the **Bot** section.

## Steps to Add Bot:

1. **Look at the LEFT SIDEBAR** - You should see a list of options under "Settings"
2. **Click on "Bot"** - It's in the left sidebar, below "OAuth2" (it has a robot icon 🤖)
3. **On the Bot page**, you'll see:
   - A button that says **"Add Bot"** or **"Create Bot"**
   - Click that button
   - Confirm by clicking "Yes, do it!" or similar

4. **After creating the bot**, you'll see:
   - **Token** section - This is what you need!
   - Click **"Reset Token"** or **"Copy"** to get your bot token
   - **IMPORTANT**: Copy this token immediately - you can only see it once!

5. **Enable Required Intents**:
   - Scroll down to **"Privileged Gateway Intents"**
   - Enable: ✅ **"Message Content Intent"** (REQUIRED for the bot to read messages)
   - Save changes

6. **Invite Bot to Server**:
   - Go to **"OAuth2"** in the left sidebar
   - Click **"URL Generator"**
   - Under **Scopes**, select: `bot`
   - Under **Bot Permissions**, select:
     - ✅ Send Messages
     - ✅ Read Message History
     - ✅ View Channels
   - Copy the generated URL at the bottom
   - Open the URL in your browser
   - Select your Discord server
   - Authorize the bot

## Quick Navigation:

From "General Information" page:
- Look LEFT → Find "Bot" (with robot icon) → Click it
- OR use this direct URL (replace YOUR_APP_ID):
  `https://discord.com/developers/applications/YOUR_APP_ID/bot`

Your Application ID from the screenshot: `1458283360538464266`

So you can go directly to:
`https://discord.com/developers/applications/1458283360538464266/bot`

## After Getting the Token:

1. Add it to your `.env` file:
   ```
   DISCORD_BOT_TOKEN=your-token-here
   ```

2. Verify it works:
   ```bash
   python setup_discord.py
   ```

3. Test the bot:
   ```bash
   python main.py test
   ```

4. Run the bot:
   ```bash
   python main.py run
   ```

