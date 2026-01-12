-- Add tool_observations column to llm_logs table
-- This stores the tool observations collected during each agent run for easier debugging

ALTER TABLE llm_logs 
ADD COLUMN IF NOT EXISTS tool_observations JSONB DEFAULT '[]';

-- Update the view to include tool_observations
CREATE OR REPLACE VIEW llm_logs_readable AS
SELECT 
    id,
    created_at,
    original_user_message,
    current_task_brief,
    iteration,
    response,
    tool_observations,
    system_prompt,
    messages,
    provider,
    model,
    response_metadata,
    error,
    conversation_id
FROM llm_logs
ORDER BY id DESC;

-- Add a comment describing the column
COMMENT ON COLUMN llm_logs.tool_observations IS 'Tool observations collected during the agent run (contains file IDs, search results, etc.)';
 