-- Guidelines table with version history
CREATE TABLE guidelines (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    diff_from_previous TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for version lookups
CREATE INDEX idx_guidelines_version ON guidelines(version DESC);

-- Interactions table for conversation history
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for conversation lookups
CREATE INDEX idx_interactions_conversation ON interactions(conversation_id, created_at);