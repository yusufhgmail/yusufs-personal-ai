# Quick Guide: Set Environment Variables in Railway

Since the CLI is having issues with service linking, let's use the Railway dashboard (much easier!)

## Steps:

1. Go to your Railway project:
   https://railway.app/project/4bcfe608-0884-4157-98b5-c48807d0902c

2. Click on your service (or create one if needed)

3. Go to the "Variables" tab

4. Add these variables from your `.env` file:
   - `LLM_PROVIDER`
   - `OPENAI_API_KEY`
   - `LLM_MODEL`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_CHANNEL_ID` (if you have it)

5. For Google credentials (if you have them):
   - Encode `config/google_credentials.json` to base64
   - Add as `GOOGLE_CREDENTIALS_BASE64`

## To encode Google credentials:

**In PowerShell:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("config/google_credentials.json"))
```

**In Bash:**
```bash
base64 -i config/google_credentials.json
```

Copy the output and paste it as the value for `GOOGLE_CREDENTIALS_BASE64` in Railway.

## After setting variables:

The deployment should automatically redeploy with the new variables. Check logs:
```bash
railway logs
```

You should see your bot connect to Discord!

