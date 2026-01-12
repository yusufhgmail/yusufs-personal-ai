"""Focus store for the one-line current focus tracker."""

from datetime import datetime
from typing import Optional

from storage.supabase_client import get_supabase_client


class FocusStore:
    """
    Manages the current focus line for each user.
    
    The focus line is a single sentence describing what the user
    is currently working on, used to provide context for ambiguous
    messages like "continue" or "let's resume".
    """
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "current_focus"
    
    def get_focus(self, user_id: str) -> Optional[str]:
        """
        Get the current focus line for a user.
        
        Args:
            user_id: The user ID (Discord user ID)
            
        Returns:
            The focus line, or None if not set
        """
        response = self.client.table(self.table)\
            .select("focus")\
            .eq("user_id", user_id)\
            .execute()
        
        if not response.data:
            return None
        
        return response.data[0]["focus"]
    
    def set_focus(self, user_id: str, focus: str) -> None:
        """
        Set or update the current focus line for a user.
        
        Args:
            user_id: The user ID (Discord user ID)
            focus: The new focus line (one sentence)
        """
        # Use upsert to create or update
        self.client.table(self.table).upsert(
            {
                "user_id": user_id,
                "focus": focus
            },
            on_conflict="user_id"
        ).execute()
    
    def clear_focus(self, user_id: str) -> None:
        """
        Clear the current focus for a user.
        
        Args:
            user_id: The user ID (Discord user ID)
        """
        self.client.table(self.table)\
            .delete()\
            .eq("user_id", user_id)\
            .execute()

