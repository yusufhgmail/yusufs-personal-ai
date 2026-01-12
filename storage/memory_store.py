"""Memory store for vector-based context retrieval."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from storage.supabase_client import get_supabase_client


@dataclass
class Memory:
    """A memory entry (stored message with embedding)."""
    id: int
    user_id: str
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
    similarity: Optional[float] = None  # Only set when returned from search


class MemoryStore:
    """
    Manages memory storage and retrieval using vector embeddings.
    
    Stores all messages with their embeddings for semantic search,
    enabling retrieval of contextually relevant past conversations.
    """
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "memory"
    
    def store_message(
        self,
        user_id: str,
        role: str,
        content: str,
        embedding: list[float]
    ) -> Memory:
        """
        Store a message with its embedding for future retrieval.
        
        Args:
            user_id: The user ID (Discord user ID)
            role: 'user' or 'assistant'
            content: The message content
            embedding: The embedding vector (1536 dimensions)
            
        Returns:
            The created Memory entry
        """
        response = self.client.table(self.table).insert({
            "user_id": user_id,
            "role": role,
            "content": content,
            "embedding": embedding
        }).execute()
        
        row = response.data[0]
        return Memory(
            id=row["id"],
            user_id=row["user_id"],
            role=row["role"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def search_similar(
        self,
        user_id: str,
        embedding: list[float],
        limit: int = 10
    ) -> list[Memory]:
        """
        Search for semantically similar messages using vector similarity.
        
        Args:
            user_id: The user ID to search within
            embedding: The query embedding vector
            limit: Maximum number of results to return
            
        Returns:
            List of Memory entries, ordered by similarity (most similar first)
        """
        # Use the RPC function we created in the SQL migration
        response = self.client.rpc(
            "search_memory",
            {
                "p_user_id": user_id,
                "p_embedding": embedding,
                "p_limit": limit
            }
        ).execute()
        
        return [
            Memory(
                id=row["id"],
                user_id=row["user_id"],
                role=row["role"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                similarity=row.get("similarity")
            )
            for row in response.data
        ]
    
    def get_recent(self, user_id: str, limit: int = 5) -> list[Memory]:
        """
        Get the most recent messages for a user.
        
        Args:
            user_id: The user ID
            limit: Maximum number of messages to return
            
        Returns:
            List of Memory entries, ordered chronologically (oldest first)
        """
        response = self.client.table(self.table)\
            .select("id, user_id, role, content, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        memories = [
            Memory(
                id=row["id"],
                user_id=row["user_id"],
                role=row["role"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
        
        # Reverse to get chronological order (oldest first)
        memories.reverse()
        return memories
    
    def format_memories_for_prompt(self, memories: list[Memory]) -> str:
        """
        Format a list of memories for inclusion in a prompt.
        
        Args:
            memories: List of Memory entries
            
        Returns:
            Formatted string suitable for prompt injection
        """
        if not memories:
            return "(No relevant past context)"
        
        lines = []
        for memory in memories:
            role_label = "You" if memory.role == "assistant" else "Yusuf"
            date_str = memory.created_at.strftime("%Y-%m-%d %H:%M")
            # Truncate very long messages for context efficiency
            content = memory.content
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(f"[{date_str}] {role_label}: {content}")
        
        return "\n".join(lines)

