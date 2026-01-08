-- Guidelines table with version history
CREATE TABLE IF NOT EXISTS guidelines (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    diff_from_previous TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for version lookups (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_guidelines_version') THEN
        CREATE INDEX idx_guidelines_version ON guidelines(version DESC);
    END IF;
END $$;

-- Interactions table for conversation history
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for conversation lookups (only if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_interactions_conversation') THEN
        CREATE INDEX idx_interactions_conversation ON interactions(conversation_id, created_at);
    END IF;
END $$;

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