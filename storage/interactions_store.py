"""Interactions store for conversation history."""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from storage.supabase_client import get_supabase_client


@dataclass
class Interaction:
    """A single interaction (message) in a conversation."""
    id: int
    conversation_id: str
    role: str  # 'user' or 'agent'
    content: str
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class InteractionsStore:
    """Manages conversation history."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "interactions"
    
    def create_conversation_id(self) -> str:
        """Generate a new conversation ID."""
        return str(uuid.uuid4())
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str,
        metadata: Optional[dict] = None
    ) -> Interaction:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The conversation this message belongs to
            role: 'user' or 'agent'
            content: The message content
            metadata: Optional metadata (task type, edits made, etc.)
            
        Returns:
            The created Interaction
        """
        response = self.client.table(self.table).insert({
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }).execute()
        
        row = response.data[0]
        return Interaction(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            metadata=row.get("metadata", {}),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def get_conversation(self, conversation_id: str) -> list[Interaction]:
        """Get the last 20 messages in a conversation, ordered by time."""
        response = self.client.table(self.table)\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        
        # Convert to Interaction objects
        interactions = [
            Interaction(
                id=row["id"],
                conversation_id=row["conversation_id"],
                role=row["role"],
                content=row["content"],
                metadata=row.get("metadata", {}),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
        
        # Reverse to maintain chronological order (oldest to newest)
        interactions.reverse()
        
        return interactions
    
    def get_recent_conversations(self, limit: int = 10) -> list[str]:
        """Get IDs of recent conversations."""
        response = self.client.table(self.table)\
            .select("conversation_id")\
            .order("created_at", desc=True)\
            .limit(limit * 10)\
            .execute()
        
        # Get unique conversation IDs while preserving order
        seen = set()
        conversation_ids = []
        for row in response.data:
            cid = row["conversation_id"]
            if cid not in seen:
                seen.add(cid)
                conversation_ids.append(cid)
                if len(conversation_ids) >= limit:
                    break
        
        return conversation_ids
    
    def update_metadata(self, interaction_id: int, metadata: dict) -> Interaction:
        """Update metadata for an interaction."""
        response = self.client.table(self.table)\
            .update({"metadata": metadata})\
            .eq("id", interaction_id)\
            .execute()
        
        row = response.data[0]
        return Interaction(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            metadata=row.get("metadata", {}),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )

