"""Updates guidelines based on learned patterns."""

from datetime import datetime
from typing import Optional

from storage.guidelines_store import GuidelinesStore


class GuidelineUpdater:
    """Updates the guidelines document based on learning."""
    
    def __init__(self, guidelines_store: Optional[GuidelinesStore] = None):
        self.guidelines_store = guidelines_store or GuidelinesStore()
    
    def add_pattern(self, pattern: str) -> bool:
        """
        Add a learned pattern to the guidelines.
        
        Args:
            pattern: The pattern to add (e.g., "User prefers formal language")
            
        Returns:
            True if the pattern was added, False if it already exists
        """
        current = self.guidelines_store.get_or_create_current()
        
        # Check if similar pattern already exists
        if self._pattern_exists(current.content, pattern):
            return False
        
        # Add the pattern
        self.guidelines_store.add_learned_pattern(pattern)
        return True
    
    def _pattern_exists(self, content: str, pattern: str) -> bool:
        """Check if a similar pattern already exists in the guidelines."""
        # Simple check - look for key words from the pattern
        content_lower = content.lower()
        pattern_lower = pattern.lower()
        
        # Extract key words (ignore common words)
        common_words = {'user', 'prefers', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'for', 'in', 'on', 'at'}
        pattern_words = set(pattern_lower.split()) - common_words
        
        # If most key words are already in the content, pattern likely exists
        matches = sum(1 for word in pattern_words if word in content_lower)
        return matches >= len(pattern_words) * 0.7
    
    def update_section(self, section_name: str, new_content: str) -> bool:
        """
        Update a specific section of the guidelines.
        
        Args:
            section_name: The section to update (e.g., "Communication Style")
            new_content: The new content for the section
            
        Returns:
            True if updated, False if section not found
        """
        current = self.guidelines_store.get_or_create_current()
        content = current.content
        
        # Find the section
        section_header = f"## {section_name}"
        if section_header not in content:
            return False
        
        # Find section boundaries
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if line.strip() == section_header:
                start_idx = i
            elif start_idx is not None and line.startswith('## '):
                end_idx = i
                break
        
        if start_idx is None:
            return False
        
        if end_idx is None:
            end_idx = len(lines)
        
        # Replace section content
        new_lines = lines[:start_idx + 1] + [new_content] + lines[end_idx:]
        new_full_content = '\n'.join(new_lines)
        
        self.guidelines_store.update(
            new_full_content,
            f"Updated section: {section_name}"
        )
        
        return True
    
    def add_to_section(self, section_name: str, item: str) -> bool:
        """
        Add an item to a specific section.
        
        Args:
            section_name: The section to add to
            item: The item to add (will be formatted as a bullet point)
            
        Returns:
            True if added, False if section not found
        """
        current = self.guidelines_store.get_or_create_current()
        content = current.content
        
        section_header = f"## {section_name}"
        if section_header not in content:
            return False
        
        # Format the item
        if not item.startswith('- '):
            item = f"- {item}"
        
        # Find where to insert
        lines = content.split('\n')
        insert_idx = None
        
        for i, line in enumerate(lines):
            if line.strip() == section_header:
                # Find the last bullet point in this section
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('## '):
                        insert_idx = j
                        break
                    if lines[j].strip().startswith('- '):
                        insert_idx = j + 1
                if insert_idx is None:
                    insert_idx = i + 1
                break
        
        if insert_idx is None:
            return False
        
        # Insert the item
        lines.insert(insert_idx, item)
        new_content = '\n'.join(lines)
        
        self.guidelines_store.update(new_content, f"Added to {section_name}: {item[:50]}...")
        
        return True
    
    def suggest_improvement(self, suggestion: str, context: str = "") -> dict:
        """
        Record a suggestion for system improvement (for later review).
        
        Args:
            suggestion: The improvement suggestion
            context: Optional context about why this was suggested
            
        Returns:
            Dict with suggestion details
        """
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return {
            "timestamp": today,
            "suggestion": suggestion,
            "context": context,
            "status": "pending_review"
        }

