-- Add current_task_brief column to llm_logs table
-- This stores the task brief that was active during each LLM call for easier debugging

ALTER TABLE llm_logs 
ADD COLUMN IF NOT EXISTS current_task_brief TEXT;

-- Create a view with columns in a more logical order for debugging
CREATE OR REPLACE VIEW llm_logs_readable AS
SELECT 
    id,
    created_at,
    original_user_message,
    current_task_brief,
    iteration,
    response,
    system_prompt,
    messages,
    provider,
    model,
    response_metadata,
    error,
    conversation_id
FROM llm_logs
ORDER BY id DESC;

-- Add a comment describing the view
COMMENT ON VIEW llm_logs_readable IS 'LLM logs with columns reordered for easier debugging. Shows task brief prominently.';
