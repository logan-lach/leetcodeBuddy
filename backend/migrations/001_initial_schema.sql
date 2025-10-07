-- LeetCode Buddy - Initial Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table - stores GitHub user information
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    github_id INTEGER UNIQUE NOT NULL,
    github_username VARCHAR(255) NOT NULL,
    github_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- GitHub tokens table - encrypted storage for GitHub access tokens
CREATE TABLE IF NOT EXISTS github_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    encrypted_token TEXT NOT NULL,
    token_scopes TEXT[],  -- Array of scopes like ['repo', 'user']
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- GitHub tokens don't expire, but track for rotation
    UNIQUE(user_id)
);

-- Sessions table (optional - can use stateless JWT instead)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_github_tokens_user_id ON github_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_users_github_id ON users(github_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores GitHub user information from OAuth';
COMMENT ON TABLE github_tokens IS 'Stores encrypted GitHub access tokens with AES-256 encryption';
COMMENT ON TABLE sessions IS 'Optional session tracking (can use stateless JWT instead)';
COMMENT ON COLUMN github_tokens.encrypted_token IS 'AES-256 encrypted GitHub access token using Fernet';
COMMENT ON COLUMN github_tokens.token_scopes IS 'OAuth scopes granted for the token (e.g., repo, user)';
