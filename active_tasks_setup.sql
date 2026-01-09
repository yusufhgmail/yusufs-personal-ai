-- Active Tasks table for storing the current working task brief per user
-- This is the AI's "working memory" that persists across messages for long-running tasks

CREATE TABLE IF NOT EXISTS active_tasks (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    brief TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups by user_id
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_active_tasks_user_id') THEN
        CREATE INDEX idx_active_tasks_user_id ON active_tasks(user_id);
    END IF;
END $$;

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_active_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on row update
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_active_tasks_updated_at') THEN
        CREATE TRIGGER trigger_active_tasks_updated_at
            BEFORE UPDATE ON active_tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_active_tasks_updated_at();
    END IF;
END $$;

