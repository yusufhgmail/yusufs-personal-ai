# Deployment Guide

This guide will help you deploy your Discord bot to the cloud so it can run continuously.

## Why Not Vercel?

Vercel is designed for serverless functions and static sites. Discord bots require:
- **Persistent WebSocket connections** - Discord bots maintain a constant connection to Discord's servers
- **Long-running processes** - The bot needs to stay online 24/7
- **Stateful connections** - Can't work with serverless functions that timeout

## Recommended Platforms

### Option 1: Railway (Recommended)

**Pros:**
- Very easy to set up
- Free tier with $5 credit/month
- Automatic deployments from GitHub
- Great for Python apps
- Easy environment variable management

**Cons:**
- Free tier is limited (but usually enough for a Discord bot)

#### Railway Deployment Steps

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Create a New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   - In your Railway project, go to "Variables"
   - Add all your environment variables from `.env`:
     ```
     LLM_PROVIDER=openai
     LLM_MODEL=gpt-4o
     OPENAI_API_KEY=your-key-here
     SUPABASE_URL=your-url
     SUPABASE_KEY=your-key
     DISCORD_BOT_TOKEN=your-token
     DISCORD_CHANNEL_ID=your-channel-id (optional)
     GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
     ```

4. **Handle Google Credentials**
   - Railway doesn't support file uploads directly in the UI
   - You have two options:
     
     **Option A: Use Environment Variable (Recommended)**
     - Convert your `google_credentials.json` to a base64 string:
       ```bash
       # On Windows PowerShell:
       [Convert]::ToBase64String([IO.File]::ReadAllBytes("config/google_credentials.json"))
       
       # On Mac/Linux:
       base64 -i config/google_credentials.json
       ```
     - Add `GOOGLE_CREDENTIALS_BASE64` to Railway variables
     - Update your code to read from this (see below)
     
     **Option B: Use Railway Volumes**
     - Go to your service → Settings → Volumes
     - Create a volume and mount it to `/app/config`
     - Upload your credentials file there

5. **Deploy**
   - Railway will automatically detect Python and deploy
   - Check the "Deployments" tab to see logs
   - Your bot should start automatically!

6. **Monitor**
   - Check the "Logs" tab to see if your bot connected successfully
   - You should see: "Discord bot logged in as [Bot Name]"

---

### Option 2: Render

**Pros:**
- Free tier available
- Good for Python apps
- Simple configuration

**Cons:**
- Free tier spins down after 15 minutes of inactivity (not ideal for Discord bots)
- Need to upgrade to paid plan ($7/month) for always-on

#### Render Deployment Steps

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Service**
   - **Name:** `discord-bot` (or any name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py run`
   - **Plan:** Choose "Starter" ($7/month) for always-on, or "Free" for testing

4. **Add Environment Variables**
   - Scroll down to "Environment Variables"
   - Add all your variables (same as Railway above)

5. **Handle Google Credentials**
   - Similar to Railway, use base64 encoding or a secret file service

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your bot
   - Check logs to verify it's running

---

## Handling Google Credentials in the Cloud

Since cloud platforms don't easily support file uploads, here's how to handle Google credentials:

### Method 1: Base64 Environment Variable (Recommended)

1. **Encode your credentials:**
   ```bash
   # Windows PowerShell:
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("config/google_credentials.json"))
   
   # Mac/Linux:
   base64 -i config/google_credentials.json
   ```

2. **Add to your platform's environment variables:**
   - Variable name: `GOOGLE_CREDENTIALS_BASE64`
   - Value: (the base64 string)

3. **Update your code** to read from this variable (see `config/settings.py` update below)

### Method 2: Use a Secret Management Service

- Use services like AWS Secrets Manager, HashiCorp Vault, or similar
- More complex but more secure for production

---

## Required Code Updates for Cloud Deployment

### Update `config/settings.py` to Support Base64 Credentials

You'll need to update the settings to handle base64-encoded Google credentials. Here's what to add:

```python
import base64
import json
from pathlib import Path

# In Settings class, add:
google_credentials_base64: str = Field(default="", alias="GOOGLE_CREDENTIALS_BASE64")

# Add a method to get credentials:
def get_google_credentials_path(self) -> str:
    """Get Google credentials path, creating from base64 if needed."""
    if self.google_credentials_base64:
        # Decode and write to file
        creds_path = Path(self.google_credentials_path)
        creds_path.parent.mkdir(parents=True, exist_ok=True)
        creds_data = base64.b64decode(self.google_credentials_base64)
        creds_path.write_bytes(creds_data)
        return str(creds_path)
    return self.google_credentials_path
```

---

## Environment Variables Checklist

Make sure you have all these set in your cloud platform:

**Required:**
- `LLM_PROVIDER` (openai or anthropic)
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (depending on provider)
- `LLM_MODEL` (e.g., gpt-4o, claude-3-opus-20240229)
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `DISCORD_BOT_TOKEN`

**Optional:**
- `DISCORD_CHANNEL_ID` (if you want channel-specific responses)
- `GOOGLE_CREDENTIALS_PATH` (or `GOOGLE_CREDENTIALS_BASE64` for cloud)
- `GOOGLE_CREDENTIALS_BASE64` (base64-encoded credentials)

---

## Testing Your Deployment

1. **Check Logs**
   - Look for: "Discord bot logged in as [Bot Name]"
   - Look for: "Bot is ready to receive messages"
   - Check for any error messages

2. **Test the Bot**
   - Send a DM to your bot in Discord
   - It should respond within a few seconds

3. **Monitor**
   - Keep an eye on logs for the first few hours
   - Check that the bot stays online

---

## Troubleshooting

### Bot Not Responding
- Check that `DISCORD_BOT_TOKEN` is correct
- Verify "Message Content Intent" is enabled in Discord Developer Portal
- Check logs for connection errors

### Google APIs Not Working
- Verify credentials are properly encoded/uploaded
- Check that OAuth tokens are generated (may need to run locally first to generate tokens)
- Consider uploading `gmail_token.json` and `drive_token.json` as well

### Bot Keeps Restarting
- Check logs for errors
- Verify all required environment variables are set
- Check that Supabase connection is working

### Free Tier Limitations
- Railway: $5 credit/month (usually enough for a Discord bot)
- Render Free: Spins down after 15 min (upgrade to Starter for $7/month)

---

## Cost Comparison

- **Railway:** Free tier with $5 credit/month (usually sufficient)
- **Render Free:** Free but spins down (not suitable for Discord bots)
- **Render Starter:** $7/month (always-on)
- **Fly.io:** Free tier available, pay-as-you-go after
- **DigitalOcean:** $5-12/month depending on plan

**Recommendation:** Start with Railway's free tier. If you exceed the credit, consider Render Starter ($7/month) or Railway's paid plans.

---

## Next Steps

1. Choose a platform (Railway recommended)
2. Set up your account and connect GitHub
3. Configure environment variables
4. Handle Google credentials (base64 method)
5. Deploy and test
6. Monitor logs to ensure everything works

Good luck with your deployment! 🚀

