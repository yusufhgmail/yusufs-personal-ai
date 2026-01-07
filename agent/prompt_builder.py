"""Builds prompts with guidelines for the agent."""

from storage.guidelines_store import GuidelinesStore


SYSTEM_PROMPT_TEMPLATE = """You are Yusuf's personal AI assistant. Your job is to help him with tasks, especially email responses.

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

## Response Format

When you need to use a tool, respond with:
THOUGHT: [your reasoning about what to do next]
ACTION: [tool_name]
ACTION_INPUT: [the input to the tool as JSON]

When you have a final answer or draft to present:
THOUGHT: [your reasoning]
FINAL_ANSWER: [your response to present to Yusuf]

When you have a draft that needs approval:
THOUGHT: [your reasoning]
DRAFT_FOR_APPROVAL: [the draft content]
"""


class PromptBuilder:
    """Builds prompts with current guidelines."""
    
    def __init__(self, guidelines_store: GuidelinesStore):
        self.guidelines_store = guidelines_store
    
    def build_system_prompt(self, tool_descriptions: str) -> str:
        """
        Build the system prompt with current guidelines.
        
        Args:
            tool_descriptions: Description of available tools
            
        Returns:
            The complete system prompt
        """
        guidelines = self.guidelines_store.get_or_create_current()
        
        return SYSTEM_PROMPT_TEMPLATE.format(
            guidelines=guidelines.content,
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

