-- Facts table for storing objective information about Yusuf
-- This stores facts like: who his friends are, life circumstances, goals, events, etc.

CREATE TABLE IF NOT EXISTS facts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups by creation date
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_facts_created') THEN
        CREATE INDEX idx_facts_created ON facts(created_at DESC);
    END IF;
END $$;

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_facts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on row update
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_facts_updated_at') THEN
        CREATE TRIGGER trigger_facts_updated_at
            BEFORE UPDATE ON facts
            FOR EACH ROW
            EXECUTE FUNCTION update_facts_updated_at();
    END IF;
END $$;


