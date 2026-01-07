"""Analyzes diffs between agent drafts and user edits."""

import difflib
from dataclasses import dataclass
from typing import Optional


@dataclass
class DiffAnalysis:
    """Result of analyzing a diff between two texts."""
    original: str
    edited: str
    changes: list[dict]  # List of changes with type, original, edited
    summary: str  # Human-readable summary of changes
    significant: bool  # Whether the changes are significant enough to learn from


class DiffAnalyzer:
    """Analyzes differences between agent output and user edits."""
    
    def analyze(self, original: str, edited: str) -> DiffAnalysis:
        """
        Analyze the differences between original and edited text.
        
        Args:
            original: The original text (agent's draft)
            edited: The edited text (user's version)
            
        Returns:
            DiffAnalysis with details about the changes
        """
        # Quick check for no changes
        if original.strip() == edited.strip():
            return DiffAnalysis(
                original=original,
                edited=edited,
                changes=[],
                summary="No changes made",
                significant=False
            )
        
        # Get line-by-line diff
        original_lines = original.splitlines(keepends=True)
        edited_lines = edited.splitlines(keepends=True)
        
        differ = difflib.Differ()
        diff = list(differ.compare(original_lines, edited_lines))
        
        # Parse diff into structured changes
        changes = self._parse_diff(diff)
        
        # Generate summary
        summary = self._generate_summary(changes)
        
        # Determine if significant
        significant = self._is_significant(changes, original, edited)
        
        return DiffAnalysis(
            original=original,
            edited=edited,
            changes=changes,
            summary=summary,
            significant=significant
        )
    
    def _parse_diff(self, diff: list[str]) -> list[dict]:
        """Parse diff output into structured changes."""
        changes = []
        i = 0
        
        while i < len(diff):
            line = diff[i]
            
            if line.startswith('- '):
                # Removal or modification
                removed = line[2:]
                
                # Check if next line is an addition (modification)
                if i + 1 < len(diff) and diff[i + 1].startswith('+ '):
                    added = diff[i + 1][2:]
                    changes.append({
                        'type': 'modification',
                        'original': removed.strip(),
                        'edited': added.strip()
                    })
                    i += 2
                    continue
                else:
                    changes.append({
                        'type': 'deletion',
                        'original': removed.strip(),
                        'edited': None
                    })
            elif line.startswith('+ '):
                # Addition
                added = line[2:]
                changes.append({
                    'type': 'addition',
                    'original': None,
                    'edited': added.strip()
                })
            
            i += 1
        
        return changes
    
    def _generate_summary(self, changes: list[dict]) -> str:
        """Generate a human-readable summary of changes."""
        if not changes:
            return "No changes detected"
        
        additions = sum(1 for c in changes if c['type'] == 'addition')
        deletions = sum(1 for c in changes if c['type'] == 'deletion')
        modifications = sum(1 for c in changes if c['type'] == 'modification')
        
        parts = []
        if additions:
            parts.append(f"{additions} addition(s)")
        if deletions:
            parts.append(f"{deletions} deletion(s)")
        if modifications:
            parts.append(f"{modifications} modification(s)")
        
        summary = f"Changes: {', '.join(parts)}.\n\n"
        
        # Add details for modifications (most instructive)
        if modifications > 0:
            summary += "Key modifications:\n"
            for c in changes:
                if c['type'] == 'modification':
                    summary += f"  - Changed \"{c['original'][:50]}...\" to \"{c['edited'][:50]}...\"\n"
        
        return summary
    
    def _is_significant(self, changes: list[dict], original: str, edited: str) -> bool:
        """Determine if the changes are significant enough to learn from."""
        if not changes:
            return False
        
        # Calculate change ratio
        original_len = len(original)
        edited_len = len(edited)
        
        # Very small texts - any change is significant
        if original_len < 50:
            return True
        
        # Calculate how much changed
        total_change = sum(
            len(c.get('original', '') or '') + len(c.get('edited', '') or '')
            for c in changes
        )
        
        change_ratio = total_change / max(original_len, edited_len)
        
        # Changes are significant if:
        # 1. More than 5% of the content changed
        # 2. There are more than 2 modifications
        # 3. There are substantial additions/deletions
        return (
            change_ratio > 0.05 or
            sum(1 for c in changes if c['type'] == 'modification') > 2 or
            total_change > 100
        )
    
    def extract_patterns(self, changes: list[dict]) -> list[str]:
        """
        Extract learnable patterns from the changes.
        
        Returns a list of potential guideline updates.
        """
        patterns = []
        
        for change in changes:
            if change['type'] == 'modification':
                original = change['original']
                edited = change['edited']
                
                # Detect common patterns
                
                # Tone changes
                if self._is_more_formal(original, edited):
                    patterns.append("User prefers more formal language")
                elif self._is_less_formal(original, edited):
                    patterns.append("User prefers less formal/more casual language")
                
                # Length changes
                if len(edited) < len(original) * 0.7:
                    patterns.append("User prefers shorter, more concise text")
                elif len(edited) > len(original) * 1.3:
                    patterns.append("User prefers more detailed/expanded text")
                
                # Specific word replacements
                word_patterns = self._detect_word_preferences(original, edited)
                patterns.extend(word_patterns)
        
        return list(set(patterns))  # Remove duplicates
    
    def _is_more_formal(self, original: str, edited: str) -> bool:
        """Check if edit made text more formal."""
        informal_words = ['hey', 'hi', 'thanks', 'gonna', 'wanna', 'yeah']
        formal_words = ['hello', 'dear', 'thank you', 'going to', 'want to', 'yes']
        
        original_lower = original.lower()
        edited_lower = edited.lower()
        
        informal_removed = any(w in original_lower and w not in edited_lower for w in informal_words)
        formal_added = any(w not in original_lower and w in edited_lower for w in formal_words)
        
        return informal_removed or formal_added
    
    def _is_less_formal(self, original: str, edited: str) -> bool:
        """Check if edit made text less formal."""
        return self._is_more_formal(edited, original)  # Reverse check
    
    def _detect_word_preferences(self, original: str, edited: str) -> list[str]:
        """Detect specific word replacements that indicate preferences."""
        patterns = []
        
        # Common replacements to detect
        replacements = [
            ('utilize', 'use', "User prefers 'use' over 'utilize'"),
            ('assist', 'help', "User prefers 'help' over 'assist'"),
            ('regarding', 'about', "User prefers 'about' over 'regarding'"),
            ('commence', 'start', "User prefers 'start' over 'commence'"),
            ('terminate', 'end', "User prefers 'end' over 'terminate'"),
        ]
        
        original_lower = original.lower()
        edited_lower = edited.lower()
        
        for formal, casual, pattern in replacements:
            if formal in original_lower and casual in edited_lower:
                patterns.append(pattern)
            elif casual in original_lower and formal in edited_lower:
                patterns.append(pattern.replace("prefers", "prefers not").replace("over", "and instead wants"))
        
        return patterns

