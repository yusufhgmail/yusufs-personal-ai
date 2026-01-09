"""Single ReAct-style agent that plans and executes inline."""

import json
import re
from typing import Optional
from dataclasses import dataclass

from config.settings import get_settings
from storage.guidelines_store import GuidelinesStore
from storage.interactions_store import InteractionsStore
from storage.llm_log_store import LLMLogStore
from storage.facts_store import FactsStore
from storage.active_task_store import ActiveTaskStore
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
        tool_registry: Optional[ToolRegistry] = None,
        llm_log_store: Optional[LLMLogStore] = None,
        facts_store: Optional[FactsStore] = None,
        active_task_store: Optional[ActiveTaskStore] = None
    ):
        self.settings = get_settings()
        self.guidelines_store = guidelines_store or GuidelinesStore()
        self.interactions_store = interactions_store or InteractionsStore()
        self.facts_store = facts_store or FactsStore()
        self.active_task_store = active_task_store or ActiveTaskStore()
        self.tool_registry = tool_registry or create_default_registry(
            facts_store=self.facts_store,
            active_task_store=self.active_task_store
        )
        self.llm_log_store = llm_log_store or LLMLogStore()
        self.prompt_builder = PromptBuilder(
            self.guidelines_store, 
            self.facts_store,
            self.active_task_store
        )
        
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
    
    def _call_llm(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict] = None,
        conversation_id: Optional[str] = None,
        iteration: int = 0,
        original_user_message: Optional[str] = None,
        current_task_brief: Optional[str] = None
    ) -> str:
        """
        Call the LLM with the given prompts.
        
        Args:
            system_prompt: System prompt to send
            user_message: Current user message
            history: Previous conversation history
            conversation_id: Optional conversation ID for logging
            iteration: Current iteration number in agent loop (for logging)
            original_user_message: The original user request (for logging/debugging)
            current_task_brief: The active task brief (for logging)
        """
        messages = []
        
        if history:
            # Ensure all roles are valid (map "agent" to "assistant" if any slipped through)
            # Create new dicts to avoid any reference issues
            for msg in history:
                role = msg.get("role", "user")
                if role == "agent":
                    role = "assistant"
                messages.append({"role": role, "content": msg.get("content", "")})
        
        messages.append({"role": "user", "content": user_message})
        
        # Prepare full message list for logging (includes system prompt)
        full_messages_for_log = []
        response_text = ""
        response_metadata = {}
        error = None
        
        if self.settings.llm_provider == "openai":
            # Final safety check: ensure no "agent" roles before API call
            # Create a completely new list with all roles properly mapped
            system_msg = {"role": "system", "content": system_prompt}
            safe_messages = [system_msg]
            for msg in messages:
                role = msg.get("role", "user")
                # Map "agent" to "assistant" - this is the critical fix
                if role == "agent":
                    role = "assistant"
                safe_messages.append({"role": role, "content": msg.get("content", "")})
            
            # Store full message list for logging
            full_messages_for_log = safe_messages.copy()
            
            try:
                response = self.llm.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=safe_messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                response_text = response.choices[0].message.content
                # Extract metadata
                response_metadata = {
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                        "completion_tokens": response.usage.completion_tokens if response.usage else None,
                        "total_tokens": response.usage.total_tokens if response.usage else None
                    }
                }
            except Exception as e:
                error = str(e)
                print(f"ERROR in OpenAI API call: {e}")
                print(f"Messages that caused error: {[(i, m.get('role')) for i, m in enumerate(safe_messages)]}")
                # Log the error before raising
                try:
                    self.llm_log_store.log_request(
                        conversation_id=conversation_id,
                        iteration=iteration,
                        provider="openai",
                        model=self.settings.llm_model,
                        system_prompt=system_prompt,
                        messages=full_messages_for_log,
                        response="",
                        response_metadata={},
                        error=error,
                        original_user_message=original_user_message,
                        current_task_brief=current_task_brief
                    )
                except Exception as log_error:
                    print(f"Warning: Failed to log LLM error: {log_error}")
                raise
        elif self.settings.llm_provider == "anthropic":
            # For Anthropic, system prompt is separate
            # Include system prompt in messages for logging consistency
            full_messages_for_log = [{"role": "system", "content": system_prompt}] + messages.copy()
            
            try:
                response = self.llm.messages.create(
                    model=self.settings.llm_model,
                    system=system_prompt,
                    messages=messages,
                    max_tokens=2000
                )
                response_text = response.content[0].text
                # Extract metadata
                response_metadata = {
                    "stop_reason": response.stop_reason,
                    "usage": {
                        "input_tokens": response.usage.input_tokens if response.usage else None,
                        "output_tokens": response.usage.output_tokens if response.usage else None
                    }
                }
            except Exception as e:
                error = str(e)
                print(f"ERROR in Anthropic API call: {e}")
                # Log the error before raising
                try:
                    self.llm_log_store.log_request(
                        conversation_id=conversation_id,
                        iteration=iteration,
                        provider="anthropic",
                        model=self.settings.llm_model,
                        system_prompt=system_prompt,
                        messages=full_messages_for_log,
                        response="",
                        response_metadata={},
                        error=error,
                        original_user_message=original_user_message,
                        current_task_brief=current_task_brief
                    )
                except Exception as log_error:
                    print(f"Warning: Failed to log LLM error: {log_error}")
                raise
        else:
            raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")
        
        # Log successful request (non-blocking - don't fail if logging fails)
        try:
            self.llm_log_store.log_request(
                conversation_id=conversation_id,
                iteration=iteration,
                provider=self.settings.llm_provider,
                model=self.settings.llm_model,
                system_prompt=system_prompt,
                messages=full_messages_for_log,
                response=response_text,
                response_metadata=response_metadata,
                error=error,
                original_user_message=original_user_message,
                current_task_brief=current_task_brief
            )
        except Exception as log_error:
            # Don't fail the request if logging fails - just log the error
            import traceback
            print(f"Warning: Failed to log LLM request: {log_error}")
            print(f"Logging error details: {traceback.format_exc()}")
        
        return response_text
    
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
    
    def run(self, task: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None, max_iterations: int = 10) -> str:
        """
        Run the agent on a task.
        
        Args:
            task: The task description from the user
            conversation_id: Optional conversation ID for tracking
            user_id: Optional user ID (Discord user ID) for task brief persistence
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            The final response from the agent
        """
        # Create conversation if needed
        if conversation_id is None:
            conversation_id = self.interactions_store.create_conversation_id()
        
        # Set current user ID on tool registry so tools can access it
        if user_id:
            self.tool_registry.set_current_user_id(user_id)
        
        # Load previous conversation history (before adding current message)
        prev_interactions = self.interactions_store.get_conversation(conversation_id)
        
        # Convert previous interactions to history format
        # Note: Observations from tool executions are not stored, only user/agent messages
        # Map "agent" role to "assistant" for LLM API compatibility
        history = []
        for interaction in prev_interactions:
            role = interaction.role
            # Map "agent" to "assistant" for LLM API (which expects "assistant" not "agent")
            if role == "agent":
                role = "assistant"
            history.append({"role": role, "content": interaction.content})
        
        # Log the current user message (this will be included in next run's history)
        self.interactions_store.add_message(conversation_id, "user", task)
        
        # Get current task brief for logging (before building prompts)
        current_task_brief = None
        if user_id:
            task_obj = self.active_task_store.get_active_task(user_id)
            if task_obj:
                current_task_brief = f"{task_obj.title}: {task_obj.brief}"
        
        # Build prompts
        tool_descriptions = self.tool_registry.get_descriptions()
        system_prompt = self.prompt_builder.build_system_prompt(tool_descriptions, user_id=user_id)
        task_prompt = self.prompt_builder.build_task_prompt(task)
        
        # Agent loop
        # Track the original user task to preserve it across iterations
        original_user_task = task_prompt
        current_prompt = task_prompt
        
        for i in range(max_iterations):
            # Refresh task brief for each iteration (it might change during tool calls)
            if user_id:
                task_obj = self.active_task_store.get_active_task(user_id)
                if task_obj:
                    current_task_brief = f"{task_obj.title}: {task_obj.brief}"
            
            # Get LLM response
            response_text = self._call_llm(
                system_prompt,
                current_prompt,
                history,
                conversation_id=conversation_id,
                iteration=i,
                original_user_message=task,
                current_task_brief=current_task_brief
            )
            
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
                
                # CRITICAL FIX: Preserve the original user message in history
                # After the first iteration, add the original user message so it's not lost
                if i == 0:
                    history.append({"role": "user", "content": original_user_task})
                
                # Add action and observation to history
                history.append({"role": "assistant", "content": response_text})
                history.append({"role": "user", "content": observation})
                
                # Use a continuation prompt that references the observation
                # instead of just the observation (which would cause it to be duplicated)
                current_prompt = f"The tool returned the above observation. Continue with your original task. Remember to provide a FINAL_ANSWER when you have enough information."
            
            else:
                # Thought without action - prompt for next step
                # Also preserve user message if this is the first iteration
                if i == 0:
                    history.append({"role": "user", "content": original_user_task})
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
    
    def handle_feedback(self, conversation_id: str, feedback: str, user_id: Optional[str] = None) -> str:
        """
        Handle user feedback on a draft or response.
        
        Args:
            conversation_id: The conversation ID
            feedback: User's feedback or edited version
            user_id: Optional user ID for task brief persistence
            
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
            conversation_id=conversation_id,
            user_id=user_id
        )

