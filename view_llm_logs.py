"""View LLM request/response logs for debugging."""

import argparse
import json
from datetime import datetime
from typing import Optional

from storage.llm_log_store import LLMLogStore


def format_timestamp(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def print_log(log: dict, show_full: bool = False):
    """Print a single log entry in a readable format."""
    print("\n" + "=" * 80)
    print(f"Log ID: {log['id']}")
    print(f"Time: {format_timestamp(log['created_at'])}")
    print(f"Conversation ID: {log.get('conversation_id', 'N/A')}")
    print(f"Iteration: {log['iteration']}")
    print(f"Provider: {log['provider']} | Model: {log['model']}")
    
    if log.get('error'):
        print(f"\n❌ ERROR: {log['error']}")
    
    print("\n" + "-" * 80)
    print("SYSTEM PROMPT:")
    print("-" * 80)
    system_prompt = log['system_prompt']
    if show_full or len(system_prompt) < 500:
        print(system_prompt)
    else:
        print(system_prompt[:500] + "... [truncated, use --full to see complete]")
    
    print("\n" + "-" * 80)
    print("MESSAGES SENT TO LLM:")
    print("-" * 80)
    messages = log['messages']
    for i, msg in enumerate(messages):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        print(f"\n[{i+1}] Role: {role.upper()}")
        if show_full or len(content) < 500:
            print(content)
        else:
            print(content[:500] + "... [truncated, use --full to see complete]")
    
    print("\n" + "-" * 80)
    print("RESPONSE FROM LLM:")
    print("-" * 80)
    response = log['response']
    if show_full or len(response) < 1000:
        print(response)
    else:
        print(response[:1000] + "... [truncated, use --full to see complete]")
    
    if log.get('response_metadata'):
        print("\n" + "-" * 80)
        print("RESPONSE METADATA:")
        print("-" * 80)
        metadata = log['response_metadata']
        if metadata:
            print(json.dumps(metadata, indent=2))
    
    print("\n" + "=" * 80)


def view_conversation(conversation_id: str, show_full: bool = False):
    """View all logs for a specific conversation."""
    store = LLMLogStore()
    logs = store.get_logs_by_conversation(conversation_id)
    
    if not logs:
        print(f"No logs found for conversation: {conversation_id}")
        return
    
    print(f"\nFound {len(logs)} LLM call(s) for conversation: {conversation_id}\n")
    
    for log in logs:
        # Convert LLMLog dataclass to dict for printing
        log_dict = {
            'id': log.id,
            'conversation_id': log.conversation_id,
            'iteration': log.iteration,
            'provider': log.provider,
            'model': log.model,
            'system_prompt': log.system_prompt,
            'messages': log.messages,
            'response': log.response,
            'response_metadata': log.response_metadata,
            'error': log.error,
            'created_at': log.created_at
        }
        print_log(log_dict, show_full)


def view_recent(limit: int = 10, show_full: bool = False):
    """View recent logs across all conversations."""
    store = LLMLogStore()
    logs = store.get_recent_logs(limit)
    
    if not logs:
        print("No logs found.")
        return
    
    print(f"\nShowing {len(logs)} most recent LLM call(s)\n")
    
    for log in logs:
        log_dict = {
            'id': log.id,
            'conversation_id': log.conversation_id,
            'iteration': log.iteration,
            'provider': log.provider,
            'model': log.model,
            'system_prompt': log.system_prompt,
            'messages': log.messages,
            'response': log.response,
            'response_metadata': log.response_metadata,
            'error': log.error,
            'created_at': log.created_at
        }
        print_log(log_dict, show_full)


def view_single(log_id: int, show_full: bool = False):
    """View a single log by ID."""
    store = LLMLogStore()
    log = store.get_log(log_id)
    
    if not log:
        print(f"Log with ID {log_id} not found.")
        return
    
    log_dict = {
        'id': log.id,
        'conversation_id': log.conversation_id,
        'iteration': log.iteration,
        'provider': log.provider,
        'model': log.model,
        'system_prompt': log.system_prompt,
        'messages': log.messages,
        'response': log.response,
        'response_metadata': log.response_metadata,
        'error': log.error,
        'created_at': log.created_at
    }
    print_log(log_dict, show_full)


def main():
    parser = argparse.ArgumentParser(
        description="View LLM request/response logs for debugging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View recent logs
  python view_llm_logs.py --recent 5
  
  # View logs for a specific conversation
  python view_llm_logs.py --conversation abc-123-def
  
  # View a specific log by ID
  python view_llm_logs.py --id 42
  
  # View with full content (no truncation)
  python view_llm_logs.py --recent 3 --full
        """
    )
    
    parser.add_argument(
        '--recent',
        type=int,
        metavar='N',
        help='Show N most recent logs (default: 10)'
    )
    parser.add_argument(
        '--conversation',
        type=str,
        metavar='ID',
        help='Show all logs for a specific conversation ID'
    )
    parser.add_argument(
        '--id',
        type=int,
        metavar='ID',
        help='Show a specific log by ID'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Show full content without truncation'
    )
    
    args = parser.parse_args()
    
    if args.id:
        view_single(args.id, show_full=args.full)
    elif args.conversation:
        view_conversation(args.conversation, show_full=args.full)
    elif args.recent:
        view_recent(args.recent, show_full=args.full)
    else:
        # Default: show 10 most recent
        view_recent(10, show_full=args.full)


if __name__ == "__main__":
    main()

