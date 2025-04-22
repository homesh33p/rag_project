-- This file uses variables from .env, which will be passed by the setup.sh script

-- Create a new user with login privileges
CREATE USER :RAG_USER WITH PASSWORD :RAG_PASSWORD LOGIN;

-- Create a new database called 'rag'
CREATE DATABASE rag;

-- Grant ownership of the database to the new user
ALTER DATABASE rag OWNER TO :RAG_USER;

-- Connect to the rag database
\c rag

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant privileges on the public schema
GRANT ALL ON SCHEMA public TO :RAG_USER;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES FOR USER :RAG_USER IN SCHEMA public
GRANT ALL ON TABLES TO :RAG_USER;