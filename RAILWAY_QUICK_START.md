# Railway Quick Start Guide

This guide will get your Discord bot deployed to Railway in minutes.

## What You Need to Do (3 Steps)

### Step 1: Login to Railway

Run this command:

```bash
railway login --browserless
```

This will give you a token to paste in your browser for authentication.

### Step 2: Set Environment Variables

**Option A: Automatic (Recommended)**

If you have a `.env` file, run:

```bash
./setup_railway_env.sh
```

Or on Windows PowerShell:
```powershell
.\setup_railway_env.ps1
```

This script will:
- Read your `.env` file
- Encode Google credentials to base64 (if present)
- Set all variables in Railway

**Option B: Manual**

Set variables one by one:

```bash
railway variables set LLM_PROVIDER=openai
railway variables set OPENAI_API_KEY=your-key-here
railway variables set SUPABASE_URL=your-url
railway variables set SUPABASE_KEY=your-key
railway variables set DISCORD_BOT_TOKEN=your-token
# ... etc
```

Or use the Railway dashboard: https://railway.app/dashboard

### Step 3: Deploy

Run the deployment script:

```bash
./deploy_railway.sh
```

Or on Windows PowerShell:
```powershell
.\deploy_railway.ps1
```

Or manually:

```bash
railway init    # First time only
railway up      # Deploy
```

## That's It!

Your bot should now be running in the cloud. Check the logs:

```powershell
railway logs
```

You should see: `Discord bot logged in as [Bot Name]`

## Useful Commands

```bash
railway logs          # View live logs
railway open          # Open Railway dashboard
railway status        # Check deployment status
railway variables     # List all environment variables
```

## Troubleshooting

### "Not logged in"
```bash
railway login --browserless
```

### "No project linked"
```powershell
railway init
```

### Bot not responding
1. Check logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Make sure Discord bot token is correct
4. Check that "Message Content Intent" is enabled in Discord Developer Portal

### Google credentials not working
If you have `config/google_credentials.json`, the setup script will automatically encode it to base64. If you need to do it manually:

**On Linux/Mac:**
```bash
base64 -i config/google_credentials.json
```

**On Windows PowerShell:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("config/google_credentials.json"))
```

Then set it:
```bash
railway variables set GOOGLE_CREDENTIALS_BASE64=<the-base64-string>
```

**Note:** You'll also need to upload your OAuth tokens (`gmail_token.json` and `drive_token.json`) if you've already authenticated locally. You can encode and upload them the same way.

## What I Did For You

✅ Installed Railway CLI  
✅ Created deployment scripts  
✅ Created environment variable setup script  
✅ Configured Railway project files  

## What You Must Do

1. **Login**: `railway login --browserless` (gives you a token to paste)
2. **Set variables**: Run `./setup_railway_env.sh` (or `.\setup_railway_env.ps1` on Windows) or set manually
3. **Deploy**: Run `./deploy_railway.sh` (or `.\deploy_railway.ps1` on Windows) or `railway up`

That's it! The scripts handle everything else.

