#!/usr/bin/env python3
"""
Generate Discord bot invite URL
"""

APPLICATION_ID = "1458283360538464266"  # From your Discord Developer Portal

# Permissions needed:
# - Send Messages (2048)
# - Read Message History (65536)
# - View Channels (1024)
PERMISSIONS = 2048 + 65536 + 1024  # = 68608

# Scopes
SCOPES = "bot"

# Generate invite URL
INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={APPLICATION_ID}&permissions={PERMISSIONS}&scope={SCOPES}"

print("=" * 60)
print("Discord Bot Invite URL")
print("=" * 60)
print()
print("Copy this URL and open it in your browser:")
print()
print(INVITE_URL)
print()
print("This will let you:")
print("  - Invite the bot to your Discord server")
print("  - Grant it the necessary permissions")
print()
print("Or use DMs (no invitation needed):")
print("  - Just find 'Yusuf Personal AI' in your Discord")
print("  - Send it a message directly")
print()

