
-- LLM logs table for debugging and tracing LLM API calls
CREATE TABLE IF NOT EXISTS llm_logs (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT,
    iteration INTEGER NOT NULL DEFAULT 0,
    provider TEXT NOT NULL CHECK (provider IN ('openai', 'anthropic')),
    model TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    messages JSONB NOT NULL,
    response TEXT NOT NULL,
    response_metadata JSONB DEFAULT '{}',
    error TEXT,
    original_user_message TEXT,  -- The actual user request that started this agent run
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for LLM logs (only if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_llm_logs_conversation') THEN
        CREATE INDEX idx_llm_logs_conversation ON llm_logs(conversation_id, iteration);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_llm_logs_created') THEN
        CREATE INDEX idx_llm_logs_created ON llm_logs(created_at DESC);
    END IF;
END $$;

-- Migration: Add original_user_message column if it doesn't exist (for existing installations)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'llm_logs' AND column_name = 'original_user_message'
    ) THEN
        ALTER TABLE llm_logs ADD COLUMN original_user_message TEXT;
    END IF;
END $$;
