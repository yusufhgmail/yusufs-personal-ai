-- Memory system tables for vector-based context retrieval
-- Requires pgvector extension in Supabase

-- Enable vector extension (may already be enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Memory table: stores all messages with embeddings for semantic search
CREATE TABLE IF NOT EXISTS memory (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for vector similarity search (cosine distance)
-- Using ivfflat for good balance of speed and accuracy
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'memory_embedding_idx') THEN
        CREATE INDEX memory_embedding_idx ON memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    END IF;
END $$;

-- Index for efficient user + time queries (for get_recent)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_memory_user_time') THEN
        CREATE INDEX idx_memory_user_time ON memory(user_id, created_at DESC);
    END IF;
END $$;

-- Focus table: one-line current focus per user
CREATE TABLE IF NOT EXISTS current_focus (
    user_id TEXT PRIMARY KEY,
    focus TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_focus_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on row update
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_focus_updated_at') THEN
        CREATE TRIGGER trigger_focus_updated_at
            BEFORE UPDATE ON current_focus
            FOR EACH ROW
            EXECUTE FUNCTION update_focus_updated_at();
    END IF;
END $$;

-- Function for vector similarity search
-- This is a helper function to search memory by embedding similarity
CREATE OR REPLACE FUNCTION search_memory(
    p_user_id TEXT,
    p_embedding vector(1536),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    user_id TEXT,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.user_id,
        m.role,
        m.content,
        m.created_at,
        1 - (m.embedding <=> p_embedding) AS similarity
    FROM memory m
    WHERE m.user_id = p_user_id
    ORDER BY m.embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

