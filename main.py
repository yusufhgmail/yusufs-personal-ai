#!/usr/bin/env python3
"""
Yusuf's Personal AI Assistant

Main entry point for the personal AI assistant system.
Runs the Discord bot and integrates all components.
"""

import asyncio
import argparse
import sys

from config.settings import get_settings
from storage.guidelines_store import GuidelinesStore
from storage.interactions_store import InteractionsStore
from agent.agent import Agent
from agent.tools import create_default_registry
from integrations.discord_bot import DiscordBot, ConversationManager
from integrations.gmail import GmailClient
from integrations.google_drive import GoogleDriveClient
from integrations.google_docs import GoogleDocsClient


def create_agent(gmail_client=None, drive_client=None, docs_client=None) -> Agent:
    """Create and configure the AI agent."""
    # Create stores
    guidelines_store = GuidelinesStore()
    interactions_store = InteractionsStore()
    
    # Create tool registry with clients
    tool_registry = create_default_registry(
        gmail_client=gmail_client,
        drive_client=drive_client,
        docs_client=docs_client
    )
    
    # Create agent
    agent = Agent(
        guidelines_store=guidelines_store,
        interactions_store=interactions_store,
        tool_registry=tool_registry
    )
    
    return agent


def run_discord_bot():
    """Run the Discord bot interface."""
    settings = get_settings()
    
    # Validate required settings
    if not settings.discord_bot_token:
        print("Error: DISCORD_BOT_TOKEN is required")
        print("Please set it in your .env file")
        sys.exit(1)
    
    if not settings.supabase_url or not settings.supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY are required")
        print("Please set them in your .env file")
        sys.exit(1)
    
    # Initialize clients (optional - will work without them)
    gmail_client = None
    drive_client = None
    docs_client = None
    
    try:
        gmail_client = GmailClient()
        print("Gmail client initialized")
    except Exception as e:
        print(f"Gmail client not available: {e}")
        print("Email features will be simulated")
    
    try:
        drive_client = GoogleDriveClient()
        print("Google Drive client initialized")
    except Exception as e:
        print(f"Google Drive client not available: {e}")
        print("Drive features will be simulated")
    
    try:
        docs_client = GoogleDocsClient()
        print("Google Docs client initialized")
    except Exception as e:
        print(f"Google Docs client not available: {e}")
        print("Document editing features will be simulated")
    
    # Create agent
    agent = create_agent(gmail_client=gmail_client, drive_client=drive_client, docs_client=docs_client)
    print("Agent initialized")
    
    # Ensure initial guidelines exist
    guidelines = agent.guidelines_store.get_or_create_current()
    print(f"Guidelines loaded (version {guidelines.version})")
    
    # Create conversation manager
    conversation_manager = ConversationManager(agent)
    
    # Create and run Discord bot
    bot = DiscordBot(message_handler=conversation_manager.handle_message)
    
    print("Starting Discord bot...")
    print("The bot will respond to messages in DMs or the configured channel")
    print("Press Ctrl+C to stop")
    
    bot.run()


def show_guidelines():
    """Display current guidelines."""
    guidelines_store = GuidelinesStore()
    guidelines = guidelines_store.get_or_create_current()
    
    print(f"\n{'='*60}")
    print(f"GUIDELINES (Version {guidelines.version})")
    print(f"Last updated: {guidelines.created_at}")
    print(f"{'='*60}\n")
    print(guidelines.content)
    print(f"\n{'='*60}\n")


def show_guidelines_history():
    """Display guidelines version history."""
    guidelines_store = GuidelinesStore()
    history = guidelines_store.get_version_history(limit=10)
    
    print(f"\n{'='*60}")
    print("GUIDELINES VERSION HISTORY")
    print(f"{'='*60}\n")
    
    for version in history:
        print(f"Version {version.version} - {version.created_at}")
        if version.diff_from_previous:
            print(f"  Changes: {version.diff_from_previous}")
        print()


def test_agent():
    """Run a simple test of the agent."""
    print("Testing agent...")
    
    # Create agent without external clients
    agent = create_agent()
    
    # Test a simple task
    response = agent.run("What can you help me with?")
    print(f"\nAgent response:\n{response}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Yusuf's Personal AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  run       Start the Discord bot (default)
  test      Test the agent with a simple query
  guidelines  Show current guidelines
  history   Show guidelines version history
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='run',
        choices=['run', 'test', 'guidelines', 'history'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_discord_bot()
    elif args.command == 'test':
        test_agent()
    elif args.command == 'guidelines':
        show_guidelines()
    elif args.command == 'history':
        show_guidelines_history()


if __name__ == '__main__':
    main()

