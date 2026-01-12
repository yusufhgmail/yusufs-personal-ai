-- Update interactions table to allow 'tool' role for storing tool observations
-- This enables persisting tool results (containing file IDs, etc.) in conversation history

-- Drop the existing constraint
ALTER TABLE interactions DROP CONSTRAINT IF EXISTS interactions_role_check;

-- Add the new constraint that includes 'tool'
ALTER TABLE interactions ADD CONSTRAINT interactions_role_check 
    CHECK (role IN ('user', 'agent', 'tool'));
