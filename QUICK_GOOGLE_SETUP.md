# Quick Google APIs Setup

## The Reality: OAuth2 Requires Manual Step

Unfortunately, **OAuth2 credentials for desktop apps cannot be fully automated via CLI** because:
- Google requires you to download the credentials JSON file from the web console
- This is a security measure to prevent credential theft

## What CAN Be Automated

✅ Opening the right pages in your browser  
✅ Guiding you through each step  
✅ Handling OAuth authentication flow (after you have credentials)  
✅ Auto-saving tokens  

## What REQUIRES Manual Step

❌ Creating the OAuth credentials in Google Cloud Console  
❌ Downloading the JSON file  
❌ Saving it to `config/google_credentials.json`  

## Fastest Path

1. **Run the automated guide:**
   ```bash
   python setup_google_auto.py
   ```
   This will open all the right pages for you.

2. **Or do it manually (5 minutes):**
   - Go to https://console.cloud.google.com/apis/credentials
   - Create OAuth client ID (Desktop app)
   - Download JSON
   - Save as `config/google_credentials.json`

3. **Verify:**
   ```bash
   python setup_google_quick.py
   ```

4. **Start bot:**
   ```bash
   python main.py run
   ```
   The bot will handle OAuth authentication automatically!

## Why This Limitation?

Google's security model requires that OAuth credentials be:
- Created in the web console (so you can see what you're creating)
- Downloaded as a file (so you control where it's stored)
- Not accessible via API (to prevent credential theft)

This is by design for security. Once you have the credentials file, everything else is automated!

