"""Single ReAct-style agent that plans and executes inline."""

import json
import re
from typing import Optional
from dataclasses import dataclass

from config.settings import get_settings
from storage.guidelines_store import GuidelinesStore
from storage.interactions_store import InteractionsStore
from agent.prompt_builder import PromptBuilder
from agent.tools import ToolRegistry, create_default_registry


@dataclass
class AgentResponse:
    """Response from the agent."""
    type: str  # 'thought', 'action', 'final_answer', 'draft_for_approval'
    content: str
    action_name: Optional[str] = None
    action_input: Optional[dict] = None


class Agent:
    """
    ReAct-style agent that reasons, plans, and executes inline.
    
    Uses a single agent loop:
    1. Receive task
    2. Think about what to do
    3. Take action (use tool) or provide answer
    4. Observe result
    5. Repeat until task is complete
    """
    
    def __init__(
        self,
        guidelines_store: Optional[GuidelinesStore] = None,
        interactions_store: Optional[InteractionsStore] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        self.settings = get_settings()
        self.guidelines_store = guidelines_store or GuidelinesStore()
        self.interactions_store = interactions_store or InteractionsStore()
        self.tool_registry = tool_registry or create_default_registry()
        self.prompt_builder = PromptBuilder(self.guidelines_store)
        
        # Initialize LLM client based on provider
        self.llm = self._create_llm_client()
    
    def _create_llm_client(self):
        """Create LLM client based on configuration."""
        if self.settings.llm_provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.settings.openai_api_key)
        elif self.settings.llm_provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.settings.anthropic_api_key)
        else:
            raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")
    
    def _call_llm(self, system_prompt: str, user_message: str, history: list[dict] = None) -> str:
        """Call the LLM with the given prompts."""
        messages = []
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_message})
        
        if self.settings.llm_provider == "openai":
            response = self.llm.chat.completions.create(
                model=self.settings.llm_model,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        elif self.settings.llm_provider == "anthropic":
            response = self.llm.messages.create(
                model=self.settings.llm_model,
                system=system_prompt,
                messages=messages,
                max_tokens=2000
            )
            return response.content[0].text
        
        raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")
    
    def _parse_response(self, response: str) -> AgentResponse:
        """Parse the LLM response to extract structured output."""
        response = response.strip()
        
        # Check for FINAL_ANSWER
        if "FINAL_ANSWER:" in response:
            parts = response.split("FINAL_ANSWER:", 1)
            thought = ""
            if "THOUGHT:" in parts[0]:
                thought = parts[0].split("THOUGHT:", 1)[1].strip()
            return AgentResponse(
                type="final_answer",
                content=parts[1].strip()
            )
        
        # Check for DRAFT_FOR_APPROVAL
        if "DRAFT_FOR_APPROVAL:" in response:
            parts = response.split("DRAFT_FOR_APPROVAL:", 1)
            return AgentResponse(
                type="draft_for_approval",
                content=parts[1].strip()
            )
        
        # Check for ACTION
        if "ACTION:" in response:
            # Parse thought
            thought = ""
            if "THOUGHT:" in response:
                thought_match = re.search(r"THOUGHT:\s*(.+?)(?=ACTION:|$)", response, re.DOTALL)
                if thought_match:
                    thought = thought_match.group(1).strip()
            
            # Parse action name
            action_match = re.search(r"ACTION:\s*(\w+)", response)
            if not action_match:
                return AgentResponse(type="thought", content=response)
            action_name = action_match.group(1)
            
            # Parse action input
            action_input = {}
            input_match = re.search(r"ACTION_INPUT:\s*(.+?)(?=THOUGHT:|ACTION:|$)", response, re.DOTALL)
            if input_match:
                input_str = input_match.group(1).strip()
                try:
                    action_input = json.loads(input_str)
                except json.JSONDecodeError:
                    # Try to parse as simple key=value pairs
                    action_input = {"raw_input": input_str}
            
            return AgentResponse(
                type="action",
                content=thought,
                action_name=action_name,
                action_input=action_input
            )
        
        # Default: treat as thought/observation
        if "THOUGHT:" in response:
            thought = response.split("THOUGHT:", 1)[1].strip()
            return AgentResponse(type="thought", content=thought)
        
        return AgentResponse(type="thought", content=response)
    
    def run(self, task: str, conversation_id: Optional[str] = None, max_iterations: int = 10) -> str:
        """
        Run the agent on a task.
        
        Args:
            task: The task description from the user
            conversation_id: Optional conversation ID for tracking
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            The final response from the agent
        """
        # Create conversation if needed
        if conversation_id is None:
            conversation_id = self.interactions_store.create_conversation_id()
        
        # Log the user message
        self.interactions_store.add_message(conversation_id, "user", task)
        
        # Build prompts
        tool_descriptions = self.tool_registry.get_descriptions()
        system_prompt = self.prompt_builder.build_system_prompt(tool_descriptions)
        task_prompt = self.prompt_builder.build_task_prompt(task)
        
        # Agent loop
        history = []
        current_prompt = task_prompt
        
        for i in range(max_iterations):
            # Get LLM response
            response_text = self._call_llm(system_prompt, current_prompt, history)
            
            # Parse response
            response = self._parse_response(response_text)
            
            if response.type == "final_answer":
                # Log and return final answer
                self.interactions_store.add_message(
                    conversation_id, "agent", response.content,
                    {"type": "final_answer"}
                )
                return response.content
            
            elif response.type == "draft_for_approval":
                # Log and return draft
                self.interactions_store.add_message(
                    conversation_id, "agent", response.content,
                    {"type": "draft", "needs_approval": True}
                )
                return f"**Draft for your approval:**\n\n{response.content}\n\n*Please review and let me know if you'd like any changes, or say 'send it' to proceed.*"
            
            elif response.type == "action":
                # Execute the action
                try:
                    result = self.tool_registry.execute(
                        response.action_name,
                        **response.action_input
                    )
                    observation = f"OBSERVATION: {result}"
                except Exception as e:
                    observation = f"OBSERVATION: Error executing {response.action_name}: {str(e)}"
                
                # Add to history and continue
                history.append({"role": "assistant", "content": response_text})
                history.append({"role": "user", "content": observation})
                current_prompt = observation
            
            else:
                # Thought without action - prompt for next step
                history.append({"role": "assistant", "content": response_text})
                # Be more explicit about what we need
                current_prompt = "You need to either:\n1. Use a tool (respond with ACTION: tool_name and ACTION_INPUT: {{...}})\n2. Provide a final answer (respond with FINAL_ANSWER: your answer)\n\nPlease choose one and respond in the correct format."
        
        # Max iterations reached - provide a helpful response
        final_message = "I apologize, but I'm having trouble processing that request. Could you please rephrase it or provide more specific details? For example:\n- 'Search for emails from [person]'\n- 'Help me draft an email to [person] about [topic]'\n- 'What can you help me with?'"
        self.interactions_store.add_message(
            conversation_id, "agent", final_message,
            {"type": "max_iterations_reached"}
        )
        return final_message
    
    def handle_feedback(self, conversation_id: str, feedback: str) -> str:
        """
        Handle user feedback on a draft or response.
        
        Args:
            conversation_id: The conversation ID
            feedback: User's feedback or edited version
            
        Returns:
            Agent's response to the feedback
        """
        # Log feedback
        self.interactions_store.add_message(
            conversation_id, "user", feedback,
            {"type": "feedback"}
        )
        
        # Check if it's an approval
        if feedback.lower().strip() in ["send it", "looks good", "approved", "yes", "ok", "okay"]:
            return "Got it! I'll proceed with sending/saving this."
        
        # Otherwise, it's an edit or correction - continue the conversation
        return self.run(
            f"The user provided this feedback on the previous draft: {feedback}. Please incorporate their feedback.",
            conversation_id=conversation_id
        )

