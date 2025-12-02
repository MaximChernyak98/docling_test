#!/usr/bin/env bash

set -e

echo "PDF Semantic Search - Teardown Script"
echo ""

# Determine docker-compose command
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

echo "Do you want to preserve the vector database data?"
echo "  y - Stop containers but keep data (recommended)"
echo "  n - Stop containers and remove all data"
echo ""
read -p "Choice [y/n]: " -n 1 -r
echo ""
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping Docker containers..."
    $COMPOSE_CMD down

    echo "Cleaning up networks..."
    docker network prune -f > /dev/null 2>&1 || true

    echo ""
    echo "Teardown completed (data preserved in ./qdrant_storage)"
    echo "Run ./setup.sh to restart with existing data"
else
    echo "Stopping Docker containers..."
    $COMPOSE_CMD down -v

    echo "Removing storage directories..."
    if [ -d "qdrant_storage" ]; then
        rm -rf qdrant_storage
    fi

    echo "Cleaning up networks..."
    docker network prune -f > /dev/null 2>&1 || true

    echo "Cleaning up volumes..."
    docker volume prune -f > /dev/null 2>&1 || true

    echo ""
    echo "Teardown completed (full cleanup)"
    echo "Run ./setup.sh to start fresh"
fi
