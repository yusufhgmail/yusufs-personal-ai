"""Learning Observer - monitors interactions and updates guidelines."""

from typing import Optional
from dataclasses import dataclass

from storage.guidelines_store import GuidelinesStore
from storage.interactions_store import InteractionsStore, Interaction
from learning.diff_analyzer import DiffAnalyzer, DiffAnalysis
from learning.guideline_updater import GuidelineUpdater


@dataclass
class LearningResult:
    """Result of learning from an interaction."""
    learned: bool
    patterns: list[str]
    guidelines_updated: bool
    message: str


class LearningObserver:
    """
    Observes interactions and learns from user feedback/edits.
    
    The observer:
    1. Monitors conversations between user and agent
    2. Detects when user edits agent drafts
    3. Analyzes diffs to extract patterns
    4. Updates guidelines based on learned patterns
    """
    
    def __init__(
        self,
        guidelines_store: Optional[GuidelinesStore] = None,
        interactions_store: Optional[InteractionsStore] = None
    ):
        self.guidelines_store = guidelines_store or GuidelinesStore()
        self.interactions_store = interactions_store or InteractionsStore()
        self.diff_analyzer = DiffAnalyzer()
        self.guideline_updater = GuidelineUpdater(self.guidelines_store)
    
    def observe_edit(self, original: str, edited: str, context: str = "") -> LearningResult:
        """
        Observe an edit from the user and learn from it.
        
        Args:
            original: The original text (agent's draft)
            edited: The edited text (user's version)
            context: Optional context about what this was for
            
        Returns:
            LearningResult with what was learned
        """
        # Analyze the diff
        analysis = self.diff_analyzer.analyze(original, edited)
        
        if not analysis.significant:
            return LearningResult(
                learned=False,
                patterns=[],
                guidelines_updated=False,
                message="Changes were minor, nothing significant to learn."
            )
        
        # Extract patterns from the changes
        patterns = self.diff_analyzer.extract_patterns(analysis.changes)
        
        if not patterns:
            # No specific patterns detected, but we can still learn from the raw diff
            patterns = [f"User edited draft: {analysis.summary}"]
        
        # Update guidelines with learned patterns
        updated_count = 0
        for pattern in patterns:
            if self.guideline_updater.add_pattern(pattern):
                updated_count += 1
        
        return LearningResult(
            learned=True,
            patterns=patterns,
            guidelines_updated=updated_count > 0,
            message=f"Learned {len(patterns)} pattern(s), updated guidelines with {updated_count} new pattern(s)."
        )
    
    def observe_feedback(self, conversation_id: str, feedback: str) -> LearningResult:
        """
        Observe direct feedback from the user and learn from it.
        
        Args:
            conversation_id: The conversation this feedback is part of
            feedback: The user's feedback message
            
        Returns:
            LearningResult with what was learned
        """
        # Get conversation history to understand context
        history = self.interactions_store.get_conversation(conversation_id)
        
        # Look for the previous agent draft
        agent_draft = None
        for interaction in reversed(history):
            if interaction.role == 'agent' and interaction.metadata.get('type') == 'draft':
                agent_draft = interaction.content
                break
        
        if agent_draft is None:
            return LearningResult(
                learned=False,
                patterns=[],
                guidelines_updated=False,
                message="No previous draft found to learn from."
            )
        
        # Check if feedback is an edit (longer text that could be a replacement)
        if len(feedback) > 50 and not feedback.lower().startswith(('yes', 'no', 'ok', 'send', 'approve')):
            # This might be an edited version - analyze as diff
            return self.observe_edit(agent_draft, feedback)
        
        # Otherwise, try to extract learning from the feedback text
        patterns = self._extract_patterns_from_feedback(feedback)
        
        if not patterns:
            return LearningResult(
                learned=False,
                patterns=[],
                guidelines_updated=False,
                message="Could not extract specific patterns from feedback."
            )
        
        # Update guidelines
        updated_count = 0
        for pattern in patterns:
            if self.guideline_updater.add_pattern(pattern):
                updated_count += 1
        
        return LearningResult(
            learned=True,
            patterns=patterns,
            guidelines_updated=updated_count > 0,
            message=f"Learned {len(patterns)} pattern(s) from feedback."
        )
    
    def _extract_patterns_from_feedback(self, feedback: str) -> list[str]:
        """Extract learnable patterns from feedback text."""
        patterns = []
        feedback_lower = feedback.lower()
        
        # Common feedback patterns
        feedback_patterns = [
            ("too formal", "User prefers less formal language"),
            ("too casual", "User prefers more formal language"),
            ("too long", "User prefers shorter, more concise responses"),
            ("too short", "User prefers more detailed responses"),
            ("too wordy", "User prefers concise language"),
            ("not enough detail", "User prefers more thorough explanations"),
            ("wrong tone", "Pay attention to tone matching the context"),
            ("don't use", "Avoid using specific words/phrases the user mentions"),
            ("prefer", "Note the user's stated preference"),
            ("always", "Note the user's stated rule"),
            ("never", "Note what the user wants to avoid"),
        ]
        
        for trigger, pattern in feedback_patterns:
            if trigger in feedback_lower:
                # Try to extract more specific info
                if trigger in ["don't use", "prefer", "always", "never"]:
                    # Include the full feedback as context
                    patterns.append(f"User feedback: {feedback[:100]}")
                else:
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_conversation(self, conversation_id: str) -> dict:
        """
        Analyze a full conversation for learning opportunities.
        
        Args:
            conversation_id: The conversation to analyze
            
        Returns:
            Dict with analysis results
        """
        history = self.interactions_store.get_conversation(conversation_id)
        
        analysis = {
            "total_messages": len(history),
            "user_messages": sum(1 for m in history if m.role == 'user'),
            "agent_messages": sum(1 for m in history if m.role == 'agent'),
            "drafts": sum(1 for m in history if m.metadata.get('type') == 'draft'),
            "feedback_given": sum(1 for m in history if m.metadata.get('type') == 'feedback'),
            "potential_learnings": []
        }
        
        # Look for learning opportunities
        for i, msg in enumerate(history):
            if msg.role == 'agent' and msg.metadata.get('type') == 'draft':
                # Look for user response after draft
                for j in range(i + 1, len(history)):
                    if history[j].role == 'user':
                        user_response = history[j].content
                        # Check if it's an edit or feedback
                        if len(user_response) > 50:
                            analysis['potential_learnings'].append({
                                'type': 'possible_edit',
                                'draft': msg.content[:100],
                                'response': user_response[:100]
                            })
                        break
        
        return analysis

