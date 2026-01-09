"""Active task store for the AI's working memory during long-running tasks."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from storage.supabase_client import get_supabase_client


@dataclass
class ActiveTask:
    """An active task brief - the AI's working memory for a long-running task."""
    id: int
    user_id: str
    title: str
    brief: str
    created_at: datetime
    updated_at: datetime


class ActiveTaskStore:
    """Manages active task briefs - the AI's working memory for long-running tasks."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "active_tasks"
    
    def get_active_task(self, user_id: str) -> Optional[ActiveTask]:
        """
        Get the current active task for a user.
        
        Args:
            user_id: The user ID (Discord user ID)
            
        Returns:
            The ActiveTask if one exists, None otherwise
        """
        response = self.client.table(self.table)\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        if not response.data:
            return None
        
        row = response.data[0]
        return ActiveTask(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            brief=row["brief"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
        )
    
    def set_active_task(self, user_id: str, title: str, brief: str) -> ActiveTask:
        """
        Create or update the active task for a user (upsert).
        
        Args:
            user_id: The user ID (Discord user ID)
            title: Short title describing the task
            brief: Full context and instructions for the task
            
        Returns:
            The created or updated ActiveTask
        """
        # Use upsert to create or update
        response = self.client.table(self.table).upsert(
            {
                "user_id": user_id,
                "title": title,
                "brief": brief
            },
            on_conflict="user_id"
        ).execute()
        
        row = response.data[0]
        return ActiveTask(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            brief=row["brief"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
        )
    
    def get_task_as_text(self, user_id: str) -> Optional[str]:
        """
        Get the active task formatted as text for inclusion in prompts.
        
        Args:
            user_id: The user ID
            
        Returns:
            Formatted string of the active task, or None if no task exists
        """
        task = self.get_active_task(user_id)
        
        if not task:
            return None
        
        return f"""## Current Task (Working Memory)

**Task:** {task.title}

**Context and Instructions:**
{task.brief}
"""

