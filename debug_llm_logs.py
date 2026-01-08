#!/usr/bin/env python3
"""
Debug viewer for LLM logs.
Shows what's being sent to and received from the LLM API.

Usage:
    python debug_llm_logs.py                 # Show last 10 logs
    python debug_llm_logs.py --id 44         # Show specific log by ID
    python debug_llm_logs.py --conv <conv_id> # Show all logs for a conversation
    python debug_llm_logs.py --last 20       # Show last 20 logs
    python debug_llm_logs.py --detailed      # Show full message content
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional

from storage.llm_log_store import LLMLogStore, LLMLog


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


def format_messages_summary(messages: list) -> str:
    """Format messages into a readable summary."""
    lines = []
    for i, msg in enumerate(messages):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        
        # Skip system prompt in summary (it's shown separately)
        if role == "system":
            continue
            
        # Format based on content type
        if content.startswith("THOUGHT:") or content.startswith("ACTION:"):
            content_preview = truncate(content, 80)
        elif content.startswith("OBSERVATION:"):
            content_preview = "OBSERVATION: " + truncate(content[12:], 60)
        elif content.startswith("## Current Task"):
            # Extract just the task
            task = content.replace("## Current Task\n\n", "").strip()
            content_preview = f"[USER TASK] {truncate(task, 70)}"
        else:
            content_preview = truncate(content, 80)
        
        lines.append(f"  [{i}] {role}: {content_preview}")
    
    return "\n".join(lines)


def format_log_brief(log: LLMLog) -> str:
    """Format a log entry for brief display."""
    timestamp = log.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    # Get original user message or extract from messages
    original_msg = log.original_user_message
    if not original_msg:
        # Try to find user task in messages
        for msg in log.messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if content.startswith("## Current Task"):
                    original_msg = content.replace("## Current Task\n\n", "").strip()
                    break
                elif not content.startswith("OBSERVATION:"):
                    original_msg = content
                    break
    
    # Extract response type from LLM response
    response_type = "?"
    response_preview = ""
    if log.response:
        if "FINAL_ANSWER:" in log.response:
            response_type = "FINAL"
            response_preview = truncate(log.response.split("FINAL_ANSWER:", 1)[1], 50)
        elif "ACTION:" in log.response:
            response_type = "ACTION"
            import re
            action_match = re.search(r"ACTION:\s*(\w+)", log.response)
            if action_match:
                response_preview = action_match.group(1)
        elif "DRAFT_FOR_APPROVAL:" in log.response:
            response_type = "DRAFT"
            response_preview = truncate(log.response.split("DRAFT_FOR_APPROVAL:", 1)[1], 50)
        else:
            response_type = "OTHER"
            response_preview = truncate(log.response, 50)
    
    # Token usage
    tokens = ""
    if log.response_metadata:
        usage = log.response_metadata.get("usage", {})
        total = usage.get("total_tokens") or (
            (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)
        )
        if total:
            tokens = f"[{total} tokens]"
    
    error_marker = " [ERROR]" if log.error else ""
    
    return f"""
{'='*80}
ID: {log.id} | Conv: {log.conversation_id[:8] if log.conversation_id else 'N/A'}... | Iter: {log.iteration} | {timestamp} {tokens}{error_marker}
ORIGINAL USER MESSAGE: {truncate(original_msg, 70) if original_msg else '(not recorded)'}
RESPONSE: [{response_type}] {response_preview}
Messages sent ({len(log.messages)}):
{format_messages_summary(log.messages)}
"""


def format_log_detailed(log: LLMLog) -> str:
    """Format a log entry for detailed display."""
    timestamp = log.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "=" * 80,
        f"LOG ID: {log.id}",
        f"Conversation: {log.conversation_id}",
        f"Iteration: {log.iteration}",
        f"Timestamp: {timestamp}",
        f"Provider: {log.provider}",
        f"Model: {log.model}",
        "",
        "-" * 40,
        "ORIGINAL USER MESSAGE (what the user actually sent):",
        "-" * 40,
        log.original_user_message or "(not recorded - older log entry)",
        "",
        "-" * 40,
        "SYSTEM PROMPT:",
        "-" * 40,
    ]
    
    # Show system prompt (truncated for brevity)
    if len(log.system_prompt) > 500:
        lines.append(log.system_prompt[:500] + "\n... (truncated)")
    else:
        lines.append(log.system_prompt)
    
    lines.extend([
        "",
        "-" * 40,
        f"MESSAGES SENT TO LLM ({len(log.messages)} messages):",
        "-" * 40,
    ])
    
    for i, msg in enumerate(log.messages):
        role = msg.get("role", "?")
        content = msg.get("content", "")
        
        # Skip system in detailed view (shown above)
        if role == "system":
            continue
        
        lines.append(f"\n[{i}] ROLE: {role}")
        lines.append("-" * 20)
        
        # Show full content for detailed view
        if len(content) > 1000:
            lines.append(content[:1000] + "\n... (truncated, full length: " + str(len(content)) + ")")
        else:
            lines.append(content)
    
    lines.extend([
        "",
        "-" * 40,
        "LLM RESPONSE:",
        "-" * 40,
        log.response if log.response else "(empty)",
        "",
        "-" * 40,
        "METADATA:",
        "-" * 40,
        json.dumps(log.response_metadata, indent=2) if log.response_metadata else "{}",
    ])
    
    if log.error:
        lines.extend([
            "",
            "-" * 40,
            "ERROR:",
            "-" * 40,
            log.error,
        ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Debug viewer for LLM logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_llm_logs.py                    # Show last 10 logs (brief)
  python debug_llm_logs.py --last 5           # Show last 5 logs (brief)
  python debug_llm_logs.py --id 44            # Show detailed log #44
  python debug_llm_logs.py --id 44 --brief    # Show brief log #44
  python debug_llm_logs.py --conv abc123      # Show all logs for conversation
  python debug_llm_logs.py --detailed         # Show last 10 logs in detail
        """
    )
    parser.add_argument("--id", type=int, help="Show specific log by ID")
    parser.add_argument("--conv", type=str, help="Show all logs for conversation ID")
    parser.add_argument("--last", type=int, default=10, help="Number of recent logs to show (default: 10)")
    parser.add_argument("--detailed", action="store_true", help="Show detailed output")
    parser.add_argument("--brief", action="store_true", help="Force brief output (even for --id)")
    
    args = parser.parse_args()
    
    try:
        store = LLMLogStore()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("\nMake sure your Supabase environment variables are set:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")
        sys.exit(1)
    
    logs = []
    
    if args.id:
        log = store.get_log(args.id)
        if not log:
            print(f"Log #{args.id} not found")
            sys.exit(1)
        logs = [log]
        # Default to detailed for single log lookup
        if not args.brief:
            args.detailed = True
    elif args.conv:
        logs = store.get_logs_by_conversation(args.conv)
        if not logs:
            print(f"No logs found for conversation: {args.conv}")
            sys.exit(1)
    else:
        logs = store.get_recent_logs(args.last)
        # Reverse to show oldest first (chronological order)
        logs = list(reversed(logs))
    
    if not logs:
        print("No logs found")
        sys.exit(0)
    
    print(f"\n{'DETAILED' if args.detailed else 'BRIEF'} LLM LOG VIEWER")
    print(f"Found {len(logs)} log(s)")
    
    for log in logs:
        if args.detailed:
            print(format_log_detailed(log))
        else:
            print(format_log_brief(log))
    
    print("\n" + "=" * 80)
    print("TIP: Use --id <ID> for detailed view of a specific log")
    print("TIP: Use --detailed for full message content")


if __name__ == "__main__":
    main()

