-- Migration: 001_add_timestamp_defaults
-- Description: Add server-side default timestamps to users and tasks tables
-- Date: 2026-02-09
--
-- This migration adds CURRENT_TIMESTAMP defaults so that direct SQL inserts
-- (without specifying timestamps) will automatically populate created_at and updated_at.

-- Add timestamp defaults to users table
ALTER TABLE users
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- Add timestamp defaults to tasks table
ALTER TABLE tasks
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- Verification: Test with direct SQL insert
-- INSERT INTO users (id, email, password_hash) VALUES (gen_random_uuid(), 'test@example.com', 'hash');
-- SELECT created_at, updated_at FROM users WHERE email = 'test@example.com';
