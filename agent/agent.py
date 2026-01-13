"""Single ReAct-style agent that plans and executes inline."""

import json
import re
from typing import Optional, Tuple
from dataclasses import dataclass

from config.settings import get_settings
from storage.guidelines_store import GuidelinesStore
from storage.interactions_store import InteractionsStore
from storage.llm_log_store import LLMLogStore
from storage.facts_store import FactsStore
from storage.memory_store import MemoryStore
from storage.focus_store import FocusStore
from agent.prompt_builder import PromptBuilder
from agent.embeddings import get_embedding
from agent.tools import ToolRegistry, create_default_registry


@dataclass
class AgentResponse:
    """Response from the agent."""
    type: str  # 'thought', 'action', 'final_answer', 'draft_for_approval'
    content: str
    action_name: Optional[str] = None
    action_input: Optional[dict] = None
    focus: Optional[str] = None  # Extracted focus line


class Agent:
    """
    ReAct-style agent that reasons, plans, and executes inline.
    
    Uses a single agent loop:
    1. Receive task
    2. Think about what to do
    3. Take action (use tool) or provide answer
    4. Observe result
    5. Repeat until task is complete
    
    Memory system:
    - Stores all messages with embeddings for semantic search
    - Retrieves relevant past context via vector similarity
    - Maintains a focus line for ambiguous message interpretation
    """
    
    def __init__(
        self,
        guidelines_store: Optional[GuidelinesStore] = None,
        interactions_store: Optional[InteractionsStore] = None,
        tool_registry: Optional[ToolRegistry] = None,
        llm_log_store: Optional[LLMLogStore] = None,
        facts_store: Optional[FactsStore] = None,
        memory_store: Optional[MemoryStore] = None,
        focus_store: Optional[FocusStore] = None
    ):
        self.settings = get_settings()
        self.guidelines_store = guidelines_store or GuidelinesStore()
        self.interactions_store = interactions_store or InteractionsStore()
        self.facts_store = facts_store or FactsStore()
        self.memory_store = memory_store or MemoryStore()
        self.focus_store = focus_store or FocusStore()
        self.tool_registry = tool_registry or create_default_registry(
            facts_store=self.facts_store
        )
        self.llm_log_store = llm_log_store or LLMLogStore()
        self.prompt_builder = PromptBuilder(
            self.guidelines_store, 
            self.facts_store
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
        current_focus: Optional[str] = None,
        tool_observations: list[dict] = None
    ) -> Tuple[str, Optional['LLMLog']]:
        """
        Call the LLM with the given prompts.
        
        Args:
            system_prompt: System prompt to send
            user_message: Current user message
            history: Previous conversation history
            conversation_id: Optional conversation ID for logging
            iteration: Current iteration number in agent loop (for logging)
            original_user_message: The original user request (for logging/debugging)
            current_focus: The current focus line (for logging)
            tool_observations: Tool observations collected during this agent run (for logging)
        """
        messages = []
        
        if history:
            # Ensure all roles are valid (map "agent" to "assistant" if any slipped through)
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
            system_msg = {"role": "system", "content": system_prompt}
            safe_messages = [system_msg]
            for msg in messages:
                role = msg.get("role", "user")
                if role == "agent":
                    role = "assistant"
                safe_messages.append({"role": role, "content": msg.get("content", "")})
            
            full_messages_for_log = safe_messages.copy()
            
            try:
                response = self.llm.chat.completions.create(
                    model=self.settings.llm_model,
                    messages=safe_messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                response_text = response.choices[0].message.content
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
                log_entry = None
                try:
                    log_entry = self.llm_log_store.log_request(
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
                        current_task_brief=current_focus,
                        tool_observations=tool_observations
                    )
                except Exception as log_error:
                    print(f"Warning: Failed to log LLM error: {log_error}")
                return "", log_entry
        elif self.settings.llm_provider == "anthropic":
            full_messages_for_log = [{"role": "system", "content": system_prompt}] + messages.copy()
            
            try:
                response = self.llm.messages.create(
                    model=self.settings.llm_model,
                    system=system_prompt,
                    messages=messages,
                    max_tokens=2000
                )
                response_text = response.content[0].text
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
                log_entry = None
                try:
                    log_entry = self.llm_log_store.log_request(
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
                        current_task_brief=current_focus,
                        tool_observations=tool_observations
                    )
                except Exception as log_error:
                    print(f"Warning: Failed to log LLM error: {log_error}")
                return "", log_entry
        else:
            raise ValueError(f"Unknown LLM provider: {self.settings.llm_provider}")
        
        # Log successful request
        log_entry = None
        try:
            log_entry = self.llm_log_store.log_request(
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
                current_task_brief=current_focus,
                tool_observations=tool_observations
            )
        except Exception as log_error:
            import traceback
            print(f"Warning: Failed to log LLM request: {log_error}")
            print(f"Logging error details: {traceback.format_exc()}")
        
        return response_text, log_entry
    
    def _extract_focus(self, response_text: str) -> Optional[str]:
        """
        Extract the FOCUS line from a response.
        
        Args:
            response_text: The full response from the LLM
            
        Returns:
            The focus line content, or None if not found
        """
        # Look for FOCUS: line
        focus_match = re.search(r"FOCUS:\s*(.+?)(?=\n|ACTION:|FINAL_ANSWER:|DRAFT_FOR_APPROVAL:|$)", response_text, re.IGNORECASE)
        if focus_match:
            focus = focus_match.group(1).strip()
            # Clean up any trailing punctuation or formatting
            focus = focus.rstrip(".")
            return focus if focus else None
        return None
    
    def _parse_response(self, response: str) -> AgentResponse:
        """Parse the LLM response to extract structured output."""
        response = response.strip()
        
        # Extract focus from response
        focus = self._extract_focus(response)
        
        # Check for FINAL_ANSWER
        if "FINAL_ANSWER:" in response:
            parts = response.split("FINAL_ANSWER:", 1)
            return AgentResponse(
                type="final_answer",
                content=parts[1].strip(),
                focus=focus
            )
        
        # Check for DRAFT_FOR_APPROVAL
        if "DRAFT_FOR_APPROVAL:" in response:
            parts = response.split("DRAFT_FOR_APPROVAL:", 1)
            return AgentResponse(
                type="draft_for_approval",
                content=parts[1].strip(),
                focus=focus
            )
        
        # Check for ACTION
        if "ACTION:" in response:
            # Parse thought
            thought = ""
            if "THOUGHT:" in response:
                thought_match = re.search(r"THOUGHT:\s*(.+?)(?=FOCUS:|ACTION:|$)", response, re.DOTALL)
                if thought_match:
                    thought = thought_match.group(1).strip()
            
            # Parse action name
            action_match = re.search(r"ACTION:\s*(\w+)", response)
            if not action_match:
                return AgentResponse(type="thought", content=response, focus=focus)
            action_name = action_match.group(1)
            
            # Parse action input
            action_input = {}
            input_match = re.search(r"ACTION_INPUT:\s*(.+?)(?=THOUGHT:|ACTION:|FOCUS:|$)", response, re.DOTALL)
            if input_match:
                input_str = input_match.group(1).strip()
                try:
                    action_input = json.loads(input_str)
                except json.JSONDecodeError:
                    action_input = {"raw_input": input_str}
            
            return AgentResponse(
                type="action",
                content=thought,
                action_name=action_name,
                action_input=action_input,
                focus=focus
            )
        
        # Default: treat as thought/observation
        if "THOUGHT:" in response:
            thought = response.split("THOUGHT:", 1)[1].strip()
            return AgentResponse(type="thought", content=thought, focus=focus)
        
        return AgentResponse(type="thought", content=response, focus=focus)
    
    def _get_memory_context(self, user_id: str, task: str) -> tuple[str, str, str, list[float]]:
        """
        Get memory context for a user's message.
        
        Args:
            user_id: The user ID
            task: The user's current message
            
        Returns:
            Tuple of (current_focus, recent_messages_text, similar_memories_text, embedding)
        """
        # Get current focus
        current_focus = self.focus_store.get_focus(user_id)
        
        # Generate embedding for the user's message
        embedding = get_embedding(task)
        
        # Search for similar past messages
        similar_memories = self.memory_store.search_similar(user_id, embedding, limit=10)
        similar_text = self.memory_store.format_memories_for_prompt(similar_memories)
        
        # Get recent messages
        recent_memories = self.memory_store.get_recent(user_id, limit=5)
        recent_text = self.memory_store.format_memories_for_prompt(recent_memories)
        
        return current_focus, recent_text, similar_text, embedding
    
    def run(self, task: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None, max_iterations: int = 10) -> str:
        """
        Run the agent on a task.
        
        Args:
            task: The task description from the user
            conversation_id: Optional conversation ID for tracking
            user_id: Optional user ID (Discord user ID) for memory persistence
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
        history = []
        for interaction in prev_interactions:
            role = interaction.role
            if role == "agent":
                role = "assistant"
            elif role == "tool":
                # Tool observations are presented as user messages to the LLM
                role = "user"
            history.append({"role": role, "content": interaction.content})
        
        # Log the current user message (this will be included in next run's history)
        self.interactions_store.add_message(conversation_id, "user", task)
        
        # Get memory context if user_id is provided
        current_focus = None
        recent_text = None
        similar_text = None
        user_embedding = None
        
        if user_id:
            try:
                current_focus, recent_text, similar_text, user_embedding = self._get_memory_context(user_id, task)
            except Exception as e:
                print(f"Warning: Could not get memory context: {e}")
        
        # Build prompts with memory context
        tool_descriptions = self.tool_registry.get_descriptions()
        system_prompt = self.prompt_builder.build_system_prompt(
            tool_descriptions,
            current_focus=current_focus,
            recent_messages=recent_text,
            similar_memories=similar_text
        )
        task_prompt = self.prompt_builder.build_task_prompt(task)
        
        # Agent loop
        original_user_task = task_prompt
        current_prompt = task_prompt
        final_response = None
        extracted_focus = None
        collected_tool_observations = []  # Track all tool observations during this run
        
        for i in range(max_iterations):
            # Get LLM response
            response_text, log_entry = self._call_llm(
                system_prompt,
                current_prompt,
                history,
                conversation_id=conversation_id,
                iteration=i,
                original_user_message=task,
                current_focus=current_focus,
                tool_observations=collected_tool_observations.copy()
            )
            
            # Parse response
            response = self._parse_response(response_text)
            
            # Track the focus from the response
            if response.focus:
                extracted_focus = response.focus
            
            if response.type == "final_answer":
                # Log and return final answer
                self.interactions_store.add_message(
                    conversation_id, "agent", response.content,
                    {"type": "final_answer"}
                )
                final_response = response.content
                break
            
            elif response.type == "draft_for_approval":
                # Log and return draft
                self.interactions_store.add_message(
                    conversation_id, "agent", response.content,
                    {"type": "draft", "needs_approval": True}
                )
                final_response = f"**Draft for your approval:**\n\n{response.content}\n\n*Please review and let me know if you'd like any changes, or say 'send it' to proceed.*"
                break
            
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
                
                # Store the agent's action (thought + action) to interactions
                self.interactions_store.add_message(
                    conversation_id, "agent", response_text,
                    {"type": "action", "tool_name": response.action_name, "action_input": response.action_input}
                )
                
                # Store the tool observation to interactions (persists IDs for future context)
                self.interactions_store.add_message(
                    conversation_id, "tool", observation,
                    {"tool_name": response.action_name}
                )
                
                # Collect tool observation for logging
                tool_observation = {
                    "iteration": i,
                    "tool_name": response.action_name,
                    "action_input": response.action_input,
                    "observation": observation
                }
                collected_tool_observations.append(tool_observation)
                
                # Update the log entry for this iteration with the tool observation
                if log_entry:
                    try:
                        # Get current tool observations and append the new one
                        current_observations = log_entry.tool_observations.copy() if log_entry.tool_observations else []
                        current_observations.append(tool_observation)
                        self.llm_log_store.update_tool_observations(log_entry.id, current_observations)
                    except Exception as update_error:
                        print(f"Warning: Failed to update tool observations in log: {update_error}")
                
                # Preserve the original user message in history
                if i == 0:
                    history.append({"role": "user", "content": original_user_task})
                
                # Add action and observation to history
                history.append({"role": "assistant", "content": response_text})
                history.append({"role": "user", "content": observation})
                
                current_prompt = f"The tool returned the above observation. Continue with your original task. Remember to include THOUGHT:, FOCUS:, and FINAL_ANSWER: when you have enough information."
            
            else:
                # Thought without action - prompt for next step
                if i == 0:
                    history.append({"role": "user", "content": original_user_task})
                history.append({"role": "assistant", "content": response_text})
                current_prompt = "You need to either:\n1. Use a tool (respond with THOUGHT:, FOCUS:, ACTION:, and ACTION_INPUT:)\n2. Provide a final answer (respond with THOUGHT:, FOCUS:, and FINAL_ANSWER:)\n\nPlease choose one and respond in the correct format."
        
        # If we didn't get a final response, provide a fallback
        if final_response is None:
            final_response = "I apologize, but I'm having trouble processing that request. Could you please rephrase it or provide more specific details?"
            self.interactions_store.add_message(
                conversation_id, "agent", final_response,
                {"type": "max_iterations_reached"}
            )
        
        # Store messages in memory and update focus (only if user_id is provided)
        if user_id:
            try:
                # Store user message with embedding
                if user_embedding:
                    self.memory_store.store_message(user_id, "user", task, user_embedding)
                
                # Store assistant response with embedding
                response_embedding = get_embedding(final_response)
                self.memory_store.store_message(user_id, "assistant", final_response, response_embedding)
                
                # Update focus if we extracted one
                if extracted_focus:
                    self.focus_store.set_focus(user_id, extracted_focus)
            except Exception as e:
                print(f"Warning: Could not store memory: {e}")
        
        return final_response
    
    def handle_feedback(self, conversation_id: str, feedback: str, user_id: Optional[str] = None) -> str:
        """
        Handle user feedback on a draft or response.
        
        Args:
            conversation_id: The conversation ID
            feedback: User's feedback or edited version
            user_id: Optional user ID for memory persistence
            
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
