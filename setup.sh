#!/usr/bin/env bash

set -e

echo "PDF Semantic Search - Setup Script"
echo ""

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Determine docker-compose command
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

echo "Creating storage directories..."
mkdir -p qdrant_storage

echo "Starting Docker Compose services..."
$COMPOSE_CMD up -d

# Wait for Qdrant to be ready (max 60 seconds)
echo "Waiting for Qdrant to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:6333/healthz > /dev/null 2>&1; then
        echo "Qdrant is ready"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "Error: Qdrant failed to start within expected time"
        echo "Check logs with: $COMPOSE_CMD logs qdrant"
        exit 1
    fi

    echo -n "."
    sleep 2
done
echo ""

if ! curl -sf http://localhost:6333/ > /dev/null 2>&1; then
    echo "Error: Could not connect to Qdrant"
    exit 1
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "Qdrant Web UI: http://localhost:6333/dashboard"
echo "Qdrant HTTP API: http://localhost:6333"
echo "Qdrant gRPC API: localhost:6334"
echo ""
echo "To stop services, run: ./teardown.sh"
