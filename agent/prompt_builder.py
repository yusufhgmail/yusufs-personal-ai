"""Builds prompts with guidelines and facts for the agent."""

from typing import Optional

from storage.guidelines_store import GuidelinesStore
from storage.facts_store import FactsStore
from storage.active_task_store import ActiveTaskStore


SYSTEM_PROMPT_TEMPLATE = """You are Yusuf's personal AI assistant. Your job is to help him with tasks, especially email responses.

## Facts About Yusuf

{facts}

## Guidelines for Working with Yusuf

{guidelines}
{active_task}
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

## Working Memory (Task Brief) - IMPORTANT

You have TWO tools to manage your working memory:

**`set_task_brief(title, brief)`** - Use ONLY when:
- Starting a brand NEW multi-step task
- Switching to a COMPLETELY DIFFERENT task
- This REPLACES the entire brief

**`add_to_task_brief(instruction)`** - Use when:
- Yusuf gives new preferences or feedback (e.g., "list each question", "be more formal")
- You need to note progress or additional context
- This safely APPENDS without erasing existing context

**When NOT to use either tool:**
- Quick one-off questions
- Continuing the same work without new instructions
- Just answering a question about the current task

CRITICAL: When Yusuf gives feedback or new instructions during an ongoing task, use `add_to_task_brief`, NOT `set_task_brief`. This prevents accidentally erasing important context.

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
    
    def __init__(
        self, 
        guidelines_store: GuidelinesStore, 
        facts_store: FactsStore = None,
        active_task_store: ActiveTaskStore = None
    ):
        self.guidelines_store = guidelines_store
        self.facts_store = facts_store or FactsStore()
        self.active_task_store = active_task_store or ActiveTaskStore()
    
    def build_system_prompt(self, tool_descriptions: str, user_id: Optional[str] = None) -> str:
        """
        Build the system prompt with current guidelines, facts, and active task.
        
        Args:
            tool_descriptions: Description of available tools
            user_id: Optional user ID to fetch active task for
            
        Returns:
            The complete system prompt
        """
        guidelines = self.guidelines_store.get_or_create_current()
        facts = self.facts_store.get_facts_as_text()
        
        # Get active task if user_id is provided
        active_task = ""
        if user_id:
            task_text = self.active_task_store.get_task_as_text(user_id)
            if task_text:
                active_task = f"\n{task_text}\n"
        
        return SYSTEM_PROMPT_TEMPLATE.format(
            guidelines=guidelines.content,
            facts=facts,
            active_task=active_task,
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
        # Just pass the user's message as-is (no "## Current Task" wrapper)
        # The persistent task brief is already in the system prompt
        prompt = task
        
        if context:
            prompt += f"\n\n## Context\n\n{context}"
        
        return prompt

