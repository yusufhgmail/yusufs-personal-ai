-- Add current_task_brief column to llm_logs table
-- This stores the task brief that was active during each LLM call for easier debugging

ALTER TABLE llm_logs 
ADD COLUMN IF NOT EXISTS current_task_brief TEXT;

-- Add a comment describing the column
COMMENT ON COLUMN llm_logs.current_task_brief IS 'The active task brief (if any) that was included in the system prompt for this LLM call';

