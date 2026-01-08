-- Migration: Add original_user_message column to llm_logs table
-- Run this SQL in your Supabase SQL Editor if you already have the llm_logs table

-- Add the column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'llm_logs' AND column_name = 'original_user_message'
    ) THEN
        ALTER TABLE llm_logs ADD COLUMN original_user_message TEXT;
        RAISE NOTICE 'Column original_user_message added successfully';
    ELSE
        RAISE NOTICE 'Column original_user_message already exists';
    END IF;
END $$;

