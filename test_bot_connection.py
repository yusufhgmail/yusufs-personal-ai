#!/usr/bin/env python3
"""
Test if the Discord bot can connect
"""

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

async def test_connection():
    """Test Discord bot connection."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in .env")
        return False
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"Bot connected as: {bot.user}")
        print(f"Bot ID: {bot.user.id}")
        print(f"Bot is ready!")
        await bot.close()
    
    try:
        await bot.start(token)
        return True
    except discord.LoginFailure:
        print("Error: Invalid bot token")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    print("Testing Discord bot connection...")
    print()
    success = asyncio.run(test_connection())
    
    if success:
        print()
        print("[OK] Bot can connect to Discord!")
        print("Now start it with: python main.py run")
    else:
        print()
        print("[ERROR] Bot connection failed. Check your token.")

