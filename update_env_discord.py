#!/usr/bin/env python3
"""Update .env file with Discord bot token"""

from pathlib import Path

DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

# Read existing .env
env_path = Path(".env")
if env_path.exists():
    content = env_path.read_text()
    
    # Update or add Discord token
    lines = content.split('\n')
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("DISCORD_BOT_TOKEN="):
            new_lines.append(f"DISCORD_BOT_TOKEN={DISCORD_BOT_TOKEN}")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        # Add if missing
        new_lines.append(f"DISCORD_BOT_TOKEN={DISCORD_BOT_TOKEN}")
    
    env_path.write_text('\n'.join(new_lines))
    print(f"[OK] Updated .env with Discord bot token")
    print(f"  Token: {DISCORD_BOT_TOKEN[:20]}...")
else:
    print(".env file not found!")

if __name__ == "__main__":
    pass

