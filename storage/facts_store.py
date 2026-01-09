"""Facts store for objective information about Yusuf."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from storage.supabase_client import get_supabase_client


@dataclass
class Fact:
    """A fact about Yusuf."""
    id: int
    content: str
    created_at: datetime
    updated_at: datetime


class FactsStore:
    """Manages facts about Yusuf - objective information like people, events, circumstances."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "facts"
    
    def add_fact(self, content: str) -> Fact:
        """
        Add a new fact about Yusuf.
        
        Args:
            content: The fact content (e.g., "Miguel is a friend who works at...")
            
        Returns:
            The created Fact
        """
        response = self.client.table(self.table).insert({
            "content": content
        }).execute()
        
        row = response.data[0]
        return Fact(
            id=row["id"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
        )
    
    def get_all_facts(self) -> list[Fact]:
        """
        Get all facts about Yusuf.
        
        Returns:
            List of all facts, ordered by creation date (newest first)
        """
        response = self.client.table(self.table)\
            .select("*")\
            .order("created_at", desc=True)\
            .execute()
        
        return [
            Fact(
                id=row["id"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
    
    def get_fact(self, fact_id: int) -> Optional[Fact]:
        """
        Get a specific fact by ID.
        
        Args:
            fact_id: The fact ID
            
        Returns:
            The Fact if found, None otherwise
        """
        response = self.client.table(self.table)\
            .select("*")\
            .eq("id", fact_id)\
            .execute()
        
        if not response.data:
            return None
        
        row = response.data[0]
        return Fact(
            id=row["id"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
        )
    
    def update_fact(self, fact_id: int, content: str) -> Optional[Fact]:
        """
        Update an existing fact.
        
        Args:
            fact_id: The fact ID to update
            content: The new content
            
        Returns:
            The updated Fact if found, None otherwise
        """
        response = self.client.table(self.table)\
            .update({"content": content})\
            .eq("id", fact_id)\
            .execute()
        
        if not response.data:
            return None
        
        row = response.data[0]
        return Fact(
            id=row["id"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
        )
    
    def delete_fact(self, fact_id: int) -> bool:
        """
        Delete a fact.
        
        Args:
            fact_id: The fact ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        response = self.client.table(self.table)\
            .delete()\
            .eq("id", fact_id)\
            .execute()
        
        return len(response.data) > 0
    
    def search_facts(self, query: str) -> list[Fact]:
        """
        Search facts by content (simple text search).
        
        Args:
            query: Search query
            
        Returns:
            List of matching facts
        """
        response = self.client.table(self.table)\
            .select("*")\
            .ilike("content", f"%{query}%")\
            .order("created_at", desc=True)\
            .execute()
        
        return [
            Fact(
                id=row["id"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
    
    def get_facts_as_text(self) -> str:
        """
        Get all facts formatted as text for inclusion in prompts.
        
        Returns:
            Formatted string of all facts
        """
        facts = self.get_all_facts()
        
        if not facts:
            return "(No facts stored yet)"
        
        lines = []
        for fact in facts:
            date_str = fact.created_at.strftime("%Y-%m-%d")
            lines.append(f"- [{date_str}] {fact.content}")
        
        return "\n".join(lines)


