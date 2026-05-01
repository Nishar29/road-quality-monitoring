#!/bin/bash

# Road Quality Monitoring System - Local Setup Script
# This script automates the setup and startup process

set -e  # Exit on error

echo "================================"
echo "Road Quality Monitoring System"
echo "Local Setup & Run Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "${YELLOW}[1/7] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "${RED}Python 3 is not installed. Please install Python 3.11+${NC}"
    exit 1
fi
echo "${GREEN}✓ Python found: $(python3 --version)${NC}"
echo ""

# Check if Docker is installed
echo "${YELLOW}[2/7] Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo "${RED}Docker is not installed. Please install Docker and Docker Compose${NC}"
    exit 1
fi
echo "${GREEN}✓ Docker found: $(docker --version)${NC}"
echo ""

# Create virtual environment
echo "${YELLOW}[3/7] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "${GREEN}✓ Virtual environment created${NC}"
else
    echo "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "${YELLOW}[4/7] Activating virtual environment...${NC}"
source venv/bin/activate
echo "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo "${YELLOW}[5/7] Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Setup environment file
echo "${YELLOW}[6/7] Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "${GREEN}✓ .env file created from template${NC}"
else
    echo "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Start Docker services
echo "${YELLOW}[7/7] Starting Docker services (PostgreSQL, Redis)...${NC}"
docker-compose up -d
echo "${GREEN}✓ Docker services started${NC}"
echo ""

# Wait for services to be ready
echo "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

echo ""
echo "${GREEN}================================${NC}"
echo "${GREEN}Setup Complete!${NC}"
echo "${GREEN}================================${NC}"
echo ""
echo "${GREEN}Starting FastAPI Server...${NC}"
echo ""
echo "${YELLOW}Available URLs:${NC}"
echo "  📚 API Docs (Swagger):    http://localhost:8000/docs"
echo "  📖 API Docs (ReDoc):      http://localhost:8000/redoc"
echo "  🔌 OpenAPI Schema:        http://localhost:8000/openapi.json"
echo ""
echo "${YELLOW}Quick Commands:${NC}"
echo "  🧪 Run tests:             pytest tests/ -v"
echo "  📊 Coverage report:       pytest --cov=src tests/ -v"
echo "  🛑 Stop services:         docker-compose down"
echo ""

# Start the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
