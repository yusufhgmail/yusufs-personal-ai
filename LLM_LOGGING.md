# LLM Request/Response Logging

This system logs all LLM API calls to help you debug and understand what's being sent to the LLM and what responses are received.

## Setup

1. **Create the database table**: Run the SQL in `supabase_setup.sql` in your Supabase SQL editor. The new table is `llm_logs`.

   If you haven't set up the tables yet, you can run:
   ```bash
   python setup_supabase_tables.py
   ```
   Then copy the SQL from `supabase_setup.sql` into your Supabase SQL editor.

2. **The logging is automatic**: Once the table exists, all LLM calls are automatically logged. No code changes needed in your application.

## What Gets Logged

For each LLM API call, the system logs:
- **Conversation ID**: Links the log to a specific conversation
- **Iteration**: Which iteration in the agent loop (0-indexed)
- **Provider & Model**: Which LLM provider and model was used
- **System Prompt**: The full system prompt sent
- **Messages**: Complete message history sent to the LLM (including system, user, and assistant messages)
- **Response**: The full response received from the LLM
- **Response Metadata**: Token usage, finish reason, etc.
- **Error**: Any errors that occurred (if the call failed)
- **Timestamp**: When the call was made

## Viewing Logs

Use the `view_llm_logs.py` script to view logs:

### View Recent Logs
```bash
# Show 10 most recent logs (default)
python view_llm_logs.py

# Show 5 most recent logs
python view_llm_logs.py --recent 5
```

### View Logs for a Specific Conversation
```bash
python view_llm_logs.py --conversation abc-123-def-456
```

### View a Specific Log by ID
```bash
python view_llm_logs.py --id 42
```

### View Full Content (No Truncation)
By default, long content is truncated. Use `--full` to see everything:
```bash
python view_llm_logs.py --recent 3 --full
```

## Example Output

```
================================================================================
Log ID: 1
Time: 2024-01-15 20:18:23
Conversation ID: abc-123-def-456
Iteration: 0
Provider: openai | Model: gpt-4o
--------------------------------------------------------------------------------
SYSTEM PROMPT:
--------------------------------------------------------------------------------
You are Yusuf's personal AI assistant...
--------------------------------------------------------------------------------
MESSAGES SENT TO LLM:
--------------------------------------------------------------------------------

[1] Role: SYSTEM
You are Yusuf's personal AI assistant...

[2] Role: USER
ok it's the third one. which folders and files are in it?
--------------------------------------------------------------------------------
RESPONSE FROM LLM:
--------------------------------------------------------------------------------
THOUGHT: The user is asking about the contents of the third folder...
ACTION: search_drive
ACTION_INPUT: {"folder_id": "xyz789"}
--------------------------------------------------------------------------------
RESPONSE METADATA:
--------------------------------------------------------------------------------
{
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801
  }
}
================================================================================
```

## Use Cases

1. **Debugging unexpected behavior**: See exactly what prompt was sent and what the LLM responded
2. **Understanding agent reasoning**: Track the full conversation flow through multiple iterations
3. **Optimizing prompts**: Review what prompts work best
4. **Cost analysis**: Check token usage across conversations
5. **Error investigation**: See what went wrong when API calls fail

## Database Schema

The `llm_logs` table structure:
- `id`: Primary key
- `conversation_id`: Links to conversation (nullable)
- `iteration`: Iteration number in agent loop
- `provider`: 'openai' or 'anthropic'
- `model`: Model name used
- `system_prompt`: Full system prompt (TEXT)
- `messages`: Complete message history (JSONB)
- `response`: LLM response (TEXT)
- `response_metadata`: Token usage, etc. (JSONB)
- `error`: Error message if failed (TEXT, nullable)
- `created_at`: Timestamp

## Notes

- Logging happens automatically and doesn't affect performance significantly
- If logging fails, it won't break your application (errors are caught and printed as warnings)
- Logs are stored in Supabase, so they persist across restarts
- Consider setting up retention policies if you have high volume

