"""Builds prompts with guidelines, facts, and memory context for the agent."""

from typing import Optional

from storage.guidelines_store import GuidelinesStore
from storage.facts_store import FactsStore


SYSTEM_PROMPT_TEMPLATE = """You are Yusuf's personal AI assistant. Your job is to help him with tasks, especially email responses.

## Facts About Yusuf

{facts}

## Guidelines for Working with Yusuf

{guidelines}
{memory_context}
## Your Capabilities

You have access to the following tools:
{tool_descriptions}

## How to Work

1. Think step by step about what needs to be done
2. Use tools to gather information and take actions
3. When drafting content (emails, documents), follow the guidelines above
4. Always ask for approval before sending emails or making permanent changes
5. Learn from feedback - if Yusuf edits your work, that's valuable information
6. When Yusuf shares important factual information about himself, his life, people he knows, events, or circumstances, use the remember_fact tool to store it for future reference

## CRITICAL: Response Format

You MUST respond in one of these exact formats. Choose the appropriate one:

**To use a tool:**
THOUGHT: [your reasoning about what to do next]
FOCUS: [one-line description of what we're currently working on]
ACTION: [tool_name]
ACTION_INPUT: {{"param1": "value1", "param2": "value2"}}

**To provide a final answer:**
THOUGHT: [your reasoning]
FOCUS: [one-line description of what we're currently working on]
FINAL_ANSWER: [your response to present to Yusuf]

**To present a draft for approval:**
THOUGHT: [your reasoning]
FOCUS: [one-line description of what we're currently working on]
DRAFT_FOR_APPROVAL: [the draft content]

## About the FOCUS line

The FOCUS line is your working memory. It should be a single sentence describing what you and Yusuf are currently working on. Examples:
- "Answering Q&A document for Miguel, currently on question 12"
- "Drafting email response to Sarah about the project deadline"
- "Helping with vacation planning research"
- "General conversation, no specific task"

Update the FOCUS line when:
- Starting a new task
- Moving to a different question/section
- The topic clearly changes

Keep the same FOCUS when:
- Continuing the same task
- Answering a quick side question
- Providing clarification on the current topic

## Examples

Example 1 - Using a tool:
THOUGHT: The user wants to search for emails. I should use the search_emails tool.
FOCUS: Searching for emails from Miguel
ACTION: search_emails
ACTION_INPUT: {{"query": "from:miguel", "max_results": 5}}

Example 2 - Final answer:
THOUGHT: I've found the information the user needs.
FOCUS: General assistance
FINAL_ANSWER: I can help you with email management, drafting emails, searching your Gmail, and working with Google Drive files. What would you like to do?

IMPORTANT: Always include THOUGHT:, FOCUS:, and then either ACTION: or FINAL_ANSWER: or DRAFT_FOR_APPROVAL:. Never skip the FOCUS line.
"""


class PromptBuilder:
    """Builds prompts with current guidelines, facts, and memory context."""
    
    def __init__(
        self, 
        guidelines_store: GuidelinesStore, 
        facts_store: Optional[FactsStore] = None
    ):
        self.guidelines_store = guidelines_store
        self.facts_store = facts_store or FactsStore()
    
    def build_system_prompt(
        self,
        tool_descriptions: str,
        current_focus: Optional[str] = None,
        recent_messages: Optional[str] = None,
        similar_memories: Optional[str] = None
    ) -> str:
        """
        Build the system prompt with current guidelines, facts, and memory context.
        
        Args:
            tool_descriptions: Description of available tools
            current_focus: The current focus line (one sentence)
            recent_messages: Formatted recent conversation messages
            similar_memories: Formatted semantically similar past messages
            
        Returns:
            The complete system prompt
        """
        guidelines = self.guidelines_store.get_or_create_current()
        facts = self.facts_store.get_facts_as_text()
        
        # Build memory context section
        memory_context = self._build_memory_context(
            current_focus,
            recent_messages,
            similar_memories
        )
        
        return SYSTEM_PROMPT_TEMPLATE.format(
            guidelines=guidelines.content,
            facts=facts,
            memory_context=memory_context,
            tool_descriptions=tool_descriptions
        )
    
    def _build_memory_context(
        self,
        current_focus: Optional[str],
        recent_messages: Optional[str],
        similar_memories: Optional[str]
    ) -> str:
        """
        Build the memory context section of the prompt.
        
        Args:
            current_focus: The current focus line
            recent_messages: Formatted recent messages
            similar_memories: Formatted similar past messages
            
        Returns:
            Formatted memory context string
        """
        sections = []
        
        # Current focus
        if current_focus:
            sections.append(f"## Current Focus\n\n{current_focus}")
        
        # Recent conversation
        if recent_messages:
            sections.append(f"## Recent Conversation\n\n{recent_messages}")
        
        # Related past context
        if similar_memories:
            sections.append(f"## Related Past Context\n\n{similar_memories}")
        
        if sections:
            return "\n\n" + "\n\n".join(sections) + "\n"
        return ""
    
    def build_task_prompt(self, task: str, context: str = "") -> str:
        """
        Build a prompt for a specific task.
        
        Args:
            task: The task description from the user
            context: Optional additional context (e.g., email content)
            
        Returns:
            The task prompt
        """
        prompt = task
        
        if context:
            prompt += f"\n\n## Context\n\n{context}"
        
        return prompt
