
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
