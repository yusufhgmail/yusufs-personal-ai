# Setting Up Google APIs (Gmail & Drive)

## Step-by-Step Guide

### 1. Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Click the project dropdown at the top
3. Click "New Project"
4. Name it (e.g., "Personal AI Assistant")
5. Click "Create"

### 2. Enable Required APIs

1. In your project, go to "APIs & Services" > "Library"
2. Search for and enable:
   - **Gmail API** - Click "Enable"
   - **Google Drive API** - Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User Type: "External" (or "Internal" if you have Google Workspace)
   - App name: "Personal AI Assistant"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Click "Add or Remove Scopes"
     - Add: `https://www.googleapis.com/auth/gmail.readonly`
     - Add: `https://www.googleapis.com/auth/gmail.send`
     - Add: `https://www.googleapis.com/auth/gmail.compose`
     - Add: `https://www.googleapis.com/auth/gmail.modify`
     - Add: `https://www.googleapis.com/auth/drive.file`
     - Add: `https://www.googleapis.com/auth/drive.readonly`
   - Click "Update" then "Save and Continue"
   - Test users: Add your email address
   - Click "Save and Continue" > "Back to Dashboard"
4. Back at Credentials page, click "Create Credentials" > "OAuth client ID"
5. Application type: **"Desktop app"**
6. Name: "Personal AI Assistant" (or any name)
7. Click "Create"
8. **Download the JSON file** - Click the download icon
9. Save it as `config/google_credentials.json` in your project folder

### 4. First-Time Authentication

When you first run the bot, it will:
1. Open a browser window
2. Ask you to sign in with your Google account
3. Ask for permissions (Gmail and Drive access)
4. Click "Allow"
5. Save the token automatically to `config/gmail_token.json` and `config/drive_token.json`

### 5. Verify Setup

After setup, the bot will automatically use these credentials for Gmail and Drive operations.

## File Structure

After setup, you should have:
```
config/
  ├── google_credentials.json  (OAuth2 credentials - downloaded from Google)
  ├── gmail_token.json         (Auto-generated on first run)
  └── drive_token.json         (Auto-generated on first run)
```

## Troubleshooting

- **"Credentials file not found"**: Make sure `google_credentials.json` is in the `config/` folder
- **"Access denied"**: Make sure you added your email as a test user in OAuth consent screen
- **"Invalid credentials"**: Re-download the credentials JSON from Google Cloud Console

