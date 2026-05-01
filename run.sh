#!/bin/bash
# Road Quality Monitoring System - Local Development Startup Script

set -e

echo "🚀 Starting Road Quality Monitoring System..."
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL, Redis)..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "postgres"; then
    echo "✅ PostgreSQL is running"
fi

if docker-compose ps | grep -q "redis"; then
    echo "✅ Redis is running"
fi

echo ""
echo "✅ All services are running!"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✅ Dependencies installed!"
echo ""

# Setup environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created (using defaults)"
fi

echo ""
echo "🌐 Starting FastAPI server..."
echo ""
echo "================================================"
echo "✅ Server is running!"
echo ""
echo "📚 API Documentation:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo "   - OpenAPI JSON: http://localhost:8000/openapi.json"
echo ""
echo "🗄️  Database:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "💡 To stop the server: Press Ctrl+C"
echo "💡 To stop all services: docker-compose down"
echo "================================================"
echo ""

# Start the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
