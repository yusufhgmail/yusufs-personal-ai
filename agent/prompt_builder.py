"""Builds prompts with guidelines and facts for the agent."""

from storage.guidelines_store import GuidelinesStore
from storage.facts_store import FactsStore


SYSTEM_PROMPT_TEMPLATE = """You are Yusuf's personal AI assistant. Your job is to help him with tasks, especially email responses.

## Facts About Yusuf

{facts}

## Guidelines for Working with Yusuf

{guidelines}

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
ACTION: [tool_name]
ACTION_INPUT: {{"param1": "value1", "param2": "value2"}}

**To provide a final answer:**
THOUGHT: [your reasoning]
FINAL_ANSWER: [your response to present to Yusuf]

**To present a draft for approval:**
THOUGHT: [your reasoning]
DRAFT_FOR_APPROVAL: [the draft content]

## Examples

Example 1 - Using a tool:
THOUGHT: The user wants to search for emails. I should use the search_emails tool.
ACTION: search_emails
ACTION_INPUT: {{"query": "from:me", "max_results": 5}}

Example 2 - Final answer:
THOUGHT: I've found the information the user needs.
FINAL_ANSWER: I can help you with email management, drafting emails, searching your Gmail, and working with Google Drive files. What would you like to do?

IMPORTANT: Always end with either ACTION: or FINAL_ANSWER: or DRAFT_FOR_APPROVAL:. Never just think without taking action or providing an answer.
"""


class PromptBuilder:
    """Builds prompts with current guidelines and facts."""
    
    def __init__(self, guidelines_store: GuidelinesStore, facts_store: FactsStore = None):
        self.guidelines_store = guidelines_store
        self.facts_store = facts_store or FactsStore()
    
    def build_system_prompt(self, tool_descriptions: str) -> str:
        """
        Build the system prompt with current guidelines and facts.
        
        Args:
            tool_descriptions: Description of available tools
            
        Returns:
            The complete system prompt
        """
        guidelines = self.guidelines_store.get_or_create_current()
        facts = self.facts_store.get_facts_as_text()
        
        return SYSTEM_PROMPT_TEMPLATE.format(
            guidelines=guidelines.content,
            facts=facts,
            tool_descriptions=tool_descriptions
        )
    
    def build_task_prompt(self, task: str, context: str = "") -> str:
        """
        Build a prompt for a specific task.
        
        Args:
            task: The task description from the user
            context: Optional additional context (e.g., email content)
            
        Returns:
            The task prompt
        """
        prompt = f"## Current Task\n\n{task}"
        
        if context:
            prompt += f"\n\n## Context\n\n{context}"
        
        return prompt

