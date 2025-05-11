#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create a .env file with POSTGRES_USER and POSTGRES_PASSWORD variables."
    exit 1
fi

# Source environment variables from .env file
source .env

# Check if required variables are set
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Error: POSTGRES_USER and POSTGRES_PASSWORD must be set in the .env file."
    exit 1
fi

# Check PostgreSQL connection and authentication
echo "Checking PostgreSQL connection..."
PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -c "SELECT 1" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Error: Failed to connect to PostgreSQL. Please check your POSTGRES_USER and POSTGRES_PASSWORD in .env file."
    echo "Make sure PostgreSQL is running and the credentials are correct."
    exit 1
else
    echo "Successfully connected to PostgreSQL."
fi

# Check if pgvector extension is already installed
echo "Checking if pgvector extension is already installed..."
PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -t -c "SELECT count(*) FROM pg_available_extensions WHERE name = 'vector';" | grep -q "1"

# If pgvector is not installed (grep returns non-zero exit code), then install it
if [ $? -ne 0 ]; then
    echo "Installing pgvector extension..."
    # Install pgvector extension
    sudo apt-get update
    sudo apt-get install -y postgresql-server-dev-all
    cd /tmp
    git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
    cd pgvector
    make
    make install # may need sudo
    cd ..
    rm -rf pgvector
    echo "pgvector extension installed."
else
    echo "pgvector extension is already installed. Skipping installation."
fi

echo "Setting up database..."

# Run the SQL commands using PSQL with admin credentials and pass RAG_USER and RAG_PASSWORD
# Get RAG user credentials from .env or set defaults
RAG_USER=${RAG_USER:-raguser}
RAG_PASSWORD=${RAG_PASSWORD:-Forragproject}

# Make sure schema variables are set
USERGUIDE_SCHEMA=${USERGUIDE_SCHEMA:-userguide}
CUSTOM_SCHEMA=${CUSTOM_SCHEMA:-custom_documents}

# Check if the user exists
echo "Checking if user $RAG_USER exists..."
USER_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -t -c "SELECT 1 FROM pg_roles WHERE rolname='$RAG_USER';" | grep -c 1)

if [ "$USER_EXISTS" -eq "0" ]; then
    echo "Creating user $RAG_USER..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -c "CREATE USER $RAG_USER WITH PASSWORD '$RAG_PASSWORD' LOGIN;"
else
    echo "User $RAG_USER already exists."
fi

# Check if the database exists
echo "Checking if database 'rag' exists..."
DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -t -c "SELECT 1 FROM pg_database WHERE datname='rag';" | grep -c 1)

if [ "$DB_EXISTS" -eq "0" ]; then
    echo "Creating database 'rag'..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -c "CREATE DATABASE rag;"
    PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -c "ALTER DATABASE rag OWNER TO $RAG_USER;"
else
    echo "Database 'rag' already exists."
    PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -c "ALTER DATABASE rag OWNER TO $RAG_USER;"
fi

# Create extension, schemas, and set privileges
echo "Setting up schemas and privileges..."
PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -d rag -v RAG_USER="$RAG_USER" -v USERGUIDE_SCHEMA="$USERGUIDE_SCHEMA" -v CUSTOM_SCHEMA="$CUSTOM_SCHEMA" << EOF
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the schemas
CREATE SCHEMA IF NOT EXISTS $USERGUIDE_SCHEMA;
CREATE SCHEMA IF NOT EXISTS $CUSTOM_SCHEMA;

-- Grant privileges on the public schema
GRANT ALL ON SCHEMA public TO $RAG_USER;

-- Grant privileges on the schemas
GRANT ALL ON SCHEMA $USERGUIDE_SCHEMA TO $RAG_USER;
GRANT ALL ON SCHEMA $CUSTOM_SCHEMA TO $RAG_USER;

-- Set default privileges for future tables in public schema
ALTER DEFAULT PRIVILEGES FOR USER $RAG_USER IN SCHEMA public
GRANT ALL ON TABLES TO $RAG_USER;

-- Set default privileges for future tables in schemas
ALTER DEFAULT PRIVILEGES FOR USER $RAG_USER IN SCHEMA $USERGUIDE_SCHEMA
GRANT ALL ON TABLES TO $RAG_USER;

ALTER DEFAULT PRIVILEGES FOR USER $RAG_USER IN SCHEMA $CUSTOM_SCHEMA
GRANT ALL ON TABLES TO $RAG_USER;
EOF

# Check if the command executed successfully
if [ $? -eq 0 ]; then
    echo "Database setup completed successfully."
else
    echo "Error: Database setup failed."
    exit 1
fi