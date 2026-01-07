"""Guidelines store with version history."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from storage.supabase_client import get_supabase_client


@dataclass
class GuidelinesVersion:
    """A version of the guidelines document."""
    id: int
    content: str
    version: int
    diff_from_previous: Optional[str]
    created_at: datetime


# Default initial guidelines
DEFAULT_GUIDELINES = """# Guidelines for Working with Yusuf

## Communication Style
- Use direct, concise language
- Avoid excessive formality
- Never use em-dashes (-)

## Email Preferences
- Always include a clear subject line
- Keep emails under 200 words when possible
- Be professional but friendly

## Document Formatting
- Use headers for sections
- Bullet points over paragraphs
- Prefer active voice

## Patterns Learned
(New patterns will be added here as the system learns from your feedback)
"""


class GuidelinesStore:
    """Manages the guidelines document with version history."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "guidelines"
    
    def get_current(self) -> Optional[GuidelinesVersion]:
        """Get the current (latest) version of guidelines."""
        response = self.client.table(self.table)\
            .select("*")\
            .order("version", desc=True)\
            .limit(1)\
            .execute()
        
        if not response.data:
            return None
        
        row = response.data[0]
        return GuidelinesVersion(
            id=row["id"],
            content=row["content"],
            version=row["version"],
            diff_from_previous=row.get("diff_from_previous"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def get_or_create_current(self) -> GuidelinesVersion:
        """Get current guidelines or create with defaults if none exist."""
        current = self.get_current()
        if current is None:
            return self.create_initial()
        return current
    
    def create_initial(self) -> GuidelinesVersion:
        """Create initial guidelines with default content."""
        response = self.client.table(self.table).insert({
            "content": DEFAULT_GUIDELINES,
            "version": 1,
            "diff_from_previous": None
        }).execute()
        
        row = response.data[0]
        return GuidelinesVersion(
            id=row["id"],
            content=row["content"],
            version=row["version"],
            diff_from_previous=None,
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def update(self, new_content: str, diff_description: str) -> GuidelinesVersion:
        """
        Create a new version of the guidelines.
        
        Args:
            new_content: The updated guidelines content
            diff_description: Human-readable description of what changed
            
        Returns:
            The new GuidelinesVersion
        """
        current = self.get_current()
        new_version = (current.version + 1) if current else 1
        
        response = self.client.table(self.table).insert({
            "content": new_content,
            "version": new_version,
            "diff_from_previous": diff_description
        }).execute()
        
        row = response.data[0]
        return GuidelinesVersion(
            id=row["id"],
            content=row["content"],
            version=row["version"],
            diff_from_previous=row.get("diff_from_previous"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def get_version(self, version: int) -> Optional[GuidelinesVersion]:
        """Get a specific version of the guidelines."""
        response = self.client.table(self.table)\
            .select("*")\
            .eq("version", version)\
            .execute()
        
        if not response.data:
            return None
        
        row = response.data[0]
        return GuidelinesVersion(
            id=row["id"],
            content=row["content"],
            version=row["version"],
            diff_from_previous=row.get("diff_from_previous"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        )
    
    def get_version_history(self, limit: int = 10) -> list[GuidelinesVersion]:
        """Get recent version history."""
        response = self.client.table(self.table)\
            .select("*")\
            .order("version", desc=True)\
            .limit(limit)\
            .execute()
        
        return [
            GuidelinesVersion(
                id=row["id"],
                content=row["content"],
                version=row["version"],
                diff_from_previous=row.get("diff_from_previous"),
                created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            )
            for row in response.data
        ]
    
    def add_learned_pattern(self, pattern: str) -> GuidelinesVersion:
        """
        Add a new learned pattern to the guidelines.
        
        Args:
            pattern: The pattern to add (e.g., "Prefer formal tone for client emails")
            
        Returns:
            The new GuidelinesVersion
        """
        current = self.get_or_create_current()
        
        # Add pattern with timestamp to the Patterns Learned section
        today = datetime.now().strftime("%Y-%m-%d")
        new_pattern_line = f"- [{today}] {pattern}"
        
        # Find the Patterns Learned section and add the new pattern
        content_lines = current.content.split("\n")
        new_lines = []
        found_patterns_section = False
        
        for line in content_lines:
            new_lines.append(line)
            if "## Patterns Learned" in line:
                found_patterns_section = True
            elif found_patterns_section and line.strip() == "":
                # Insert before the next empty line after section header
                new_lines.insert(-1, new_pattern_line)
                found_patterns_section = False
        
        # If we didn't find a good insertion point, append at end
        if found_patterns_section:
            new_lines.append(new_pattern_line)
        
        new_content = "\n".join(new_lines)
        
        return self.update(new_content, f"Added learned pattern: {pattern}")

