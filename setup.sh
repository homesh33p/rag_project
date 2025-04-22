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

echo "Setting up database..."

# Run the SQL commands using PSQL with admin credentials and pass RAG_USER and RAG_PASSWORD
# Get RAG user credentials from .env or set defaults
RAG_USER=${RAG_USER:-raguser}
RAG_PASSWORD=${RAG_PASSWORD:-Forragproject}

PGPASSWORD=$POSTGRES_PASSWORD psql -U $POSTGRES_USER -h localhost -v RAG_USER="'$RAG_USER'" -v RAG_PASSWORD="'$RAG_PASSWORD'" -f setup_db.sql

# Check if the command executed successfully
if [ $? -eq 0 ]; then
    echo "Database setup completed successfully."
else
    echo "Error: Database setup failed."
    exit 1
fi