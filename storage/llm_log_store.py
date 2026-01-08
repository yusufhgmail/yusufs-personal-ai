"""LLM request/response logging store."""

import json
import uuid
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

from storage.supabase_client import get_supabase_client


@dataclass
class LLMLog:
    """A single LLM API call log entry."""
    id: int
    conversation_id: Optional[str]
    iteration: int  # Which iteration in the agent loop (0-indexed)
    provider: str  # 'openai' or 'anthropic'
    model: str
    system_prompt: str
    messages: List[dict]  # Full message history sent to LLM
    response: str
    response_metadata: dict = field(default_factory=dict)  # tokens, finish_reason, etc.
    error: Optional[str] = None
    original_user_message: Optional[str] = None  # The actual user request that started this agent run
    created_at: datetime = field(default_factory=datetime.now)


class LLMLogStore:
    """Manages LLM API call logs for debugging and analysis."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "llm_logs"
    
    def log_request(
        self,
        conversation_id: Optional[str],
        iteration: int,
        provider: str,
        model: str,
        system_prompt: str,
        messages: List[dict],
        response: str,
        response_metadata: Optional[dict] = None,
        error: Optional[str] = None,
        original_user_message: Optional[str] = None
    ) -> LLMLog:
        """
        Log an LLM API call.
        
        Args:
            conversation_id: The conversation this call belongs to
            iteration: Which iteration in the agent loop (0-indexed)
            provider: LLM provider ('openai' or 'anthropic')
            model: Model name used
            system_prompt: System prompt sent
            messages: Full message history sent to LLM
            response: Response received from LLM
            response_metadata: Optional metadata from response (tokens, finish_reason, etc.)
            error: Optional error message if call failed
            original_user_message: The actual user request that started this agent run
            
        Returns:
            The created LLMLog
        """
        db_response = self.client.table(self.table).insert({
            "conversation_id": conversation_id,
            "iteration": iteration,
            "provider": provider,
            "model": model,
            "system_prompt": system_prompt,
            "messages": messages,
            "response": response,
            "response_metadata": response_metadata or {},
            "error": error,
            "original_user_message": original_user_message
        }).execute()
        
        row = db_response.data[0]
        return LLMLog(
            id=row["id"],
            conversation_id=row.get("conversation_id"),
            iteration=row["iteration"],
            provider=row["provider"],
            model=row["model"],
            system_prompt=row["system_prompt"],
            messages=row["messages"],
            response=row["response"],
            response_metadata=row.get("response_metadata", {}),
            error=row.get("error"),
            original_user_message=row.get("original_user_message"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def get_logs_by_conversation(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[LLMLog]:
        """Get all LLM logs for a conversation, ordered by iteration."""
        query = self.client.table(self.table)\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("iteration")\
            .order("created_at")
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        return [
            LLMLog(
                id=row["id"],
                conversation_id=row.get("conversation_id"),
                iteration=row["iteration"],
                provider=row["provider"],
                model=row["model"],
                system_prompt=row["system_prompt"],
                messages=row["messages"],
                response=row["response"],
                response_metadata=row.get("response_metadata", {}),
                error=row.get("error"),
                original_user_message=row.get("original_user_message"),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
    
    def get_recent_logs(self, limit: int = 50) -> List[LLMLog]:
        """Get recent LLM logs across all conversations."""
        response = self.client.table(self.table)\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return [
            LLMLog(
                id=row["id"],
                conversation_id=row.get("conversation_id"),
                iteration=row["iteration"],
                provider=row["provider"],
                model=row["model"],
                system_prompt=row["system_prompt"],
                messages=row["messages"],
                response=row["response"],
                response_metadata=row.get("response_metadata", {}),
                error=row.get("error"),
                original_user_message=row.get("original_user_message"),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
    
    def get_log(self, log_id: int) -> Optional[LLMLog]:
        """Get a specific log by ID."""
        response = self.client.table(self.table)\
            .select("*")\
            .eq("id", log_id)\
            .execute()
        
        if not response.data:
            return None
        
        row = response.data[0]
        return LLMLog(
            id=row["id"],
            conversation_id=row.get("conversation_id"),
            iteration=row["iteration"],
            provider=row["provider"],
            model=row["model"],
            system_prompt=row["system_prompt"],
            messages=row["messages"],
            response=row["response"],
            response_metadata=row.get("response_metadata", {}),
            error=row.get("error"),
            original_user_message=row.get("original_user_message"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )

