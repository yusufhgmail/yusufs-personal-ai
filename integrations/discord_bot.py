"""Discord bot integration for the personal AI assistant."""

import asyncio
from typing import Callable, Optional

import discord
from discord.ext import commands

from config.settings import get_settings


class DiscordBot:
    """Discord bot for interacting with the AI assistant."""
    
    def __init__(self, message_handler: Optional[Callable] = None):
        """
        Initialize the Discord bot.
        
        Args:
            message_handler: Async function to handle incoming messages.
                            Signature: async def handler(user_id: str, message: str) -> str
        """
        self.settings = get_settings()
        self.message_handler = message_handler
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        # Create bot
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        
        # Track conversations per user
        self.user_conversations: dict[str, str] = {}
        
        # Set up event handlers
        self._setup_events()
    
    def _setup_events(self):
        """Set up Discord event handlers."""
        
        @self.bot.event
        async def on_ready():
            print(f"Discord bot logged in as {self.bot.user}")
            print(f"Bot is ready to receive messages")
        
        @self.bot.event
        async def on_message(message: discord.Message):
            # Ignore messages from the bot itself
            if message.author == self.bot.user:
                return
            
            # Check if this is in the configured channel or a DM
            is_dm = isinstance(message.channel, discord.DMChannel)
            is_configured_channel = str(message.channel.id) == self.settings.discord_channel_id
            
            if not (is_dm or is_configured_channel):
                return
            
            # Get user ID
            user_id = str(message.author.id)
            user_message = message.content.strip()
            
            if not user_message:
                return
            
            # Show typing indicator while processing
            async with message.channel.typing():
                if self.message_handler:
                    try:
                        response = await self.message_handler(user_id, user_message)
                        await self._send_response(message.channel, response)
                    except Exception as e:
                        await message.channel.send(f"Sorry, I encountered an error: {str(e)}")
                else:
                    await message.channel.send("Bot is running but no message handler is configured.")
    
    async def _send_response(self, channel, response: str):
        """Send a response, splitting if necessary for Discord's character limit."""
        max_length = 2000
        
        if len(response) <= max_length:
            await channel.send(response)
        else:
            # Split into chunks
            chunks = []
            current_chunk = ""
            
            for line in response.split("\n"):
                if len(current_chunk) + len(line) + 1 > max_length:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = line
                else:
                    current_chunk += ("\n" if current_chunk else "") + line
            
            if current_chunk:
                chunks.append(current_chunk)
            
            for chunk in chunks:
                await channel.send(chunk)
    
    async def send_message(self, channel_id: str, message: str):
        """Send a message to a specific channel."""
        channel = self.bot.get_channel(int(channel_id))
        if channel:
            await self._send_response(channel, message)
    
    def run(self):
        """Run the Discord bot (blocking)."""
        self.bot.run(self.settings.discord_bot_token)
    
    async def start(self):
        """Start the Discord bot (non-blocking, for use with asyncio)."""
        await self.bot.start(self.settings.discord_bot_token)
    
    async def close(self):
        """Close the Discord bot connection."""
        await self.bot.close()


class ConversationManager:
    """Manages conversations between users and the AI agent."""
    
    def __init__(self, agent):
        """
        Initialize the conversation manager.
        
        Args:
            agent: The Agent instance to use for processing messages
        """
        self.agent = agent
        self.user_conversations: dict[str, str] = {}
        self.pending_drafts: dict[str, str] = {}  # user_id -> last draft content
    
    async def handle_message(self, user_id: str, message: str) -> str:
        """
        Handle an incoming message from a user.
        
        Args:
            user_id: The Discord user ID
            message: The user's message
            
        Returns:
            The agent's response
        """
        # Get or create conversation ID for this user
        conversation_id = self.user_conversations.get(user_id)
        
        # Check for conversation reset commands
        if message.lower().strip() in ["new conversation", "reset", "start over"]:
            conversation_id = self.agent.interactions_store.create_conversation_id()
            self.user_conversations[user_id] = conversation_id
            self.pending_drafts.pop(user_id, None)
            return "Started a new conversation. How can I help you?"
        
        # Check if this looks like approval of a previous draft
        if conversation_id and message.lower().strip() in ["send it", "looks good", "approved", "yes", "ok", "okay"]:
            self.pending_drafts.pop(user_id, None)  # Clear pending draft
            response = self.agent.handle_feedback(conversation_id, message, user_id=user_id)
            return response
        
        # Run the agent
        # Note: agent.run is synchronous, so we run it in an executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.agent.run(message, conversation_id=conversation_id, user_id=user_id)
        )
        
        # Track if this response contains a draft for approval
        if "**Draft for your approval:**" in response or "DRAFT_FOR_APPROVAL" in response:
            # Extract the draft content and store it
            if "**Draft for your approval:**" in response:
                draft_content = response.split("**Draft for your approval:**", 1)[1]
                draft_content = draft_content.split("*Please review")[0].strip()
                self.pending_drafts[user_id] = draft_content
        
        # Update conversation tracking
        if conversation_id is None:
            # Get the new conversation ID from the agent's interactions
            recent = self.agent.interactions_store.get_recent_conversations(1)
            if recent:
                self.user_conversations[user_id] = recent[0]
        
        return response

