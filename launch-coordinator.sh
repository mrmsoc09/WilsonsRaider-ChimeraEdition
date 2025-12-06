#!/bin/bash
# Kaison Zero-SOC Master Coordinator Launcher
# Automatically handles virtual environment and dependencies

set -e

PROJECT_DIR="/home/user023/agent-zero"
cd "$PROJECT_DIR"

echo "🚀 Launching Kaison Zero-SOC Master Coordinator..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate venv
source venv/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q aiohttp python-dotenv 2>/dev/null || true
echo "✅ Dependencies ready"

# Create logs directory
mkdir -p logs

# Check environment variables
echo ""
echo "🔍 Checking configuration..."
MISSING=0

for var in HACKERONE_PAT BUGCROWD_API_KEY BUGCROWD_API_SECRET INTIGRITI_CLIENT_ID INTIGRITI_CLIENT_SECRET; do
    if ! grep -q "^${var}=" .env.osint 2>/dev/null; then
        echo "   ⚠️  $var not configured"
        MISSING=$((MISSING + 1))
    else
        echo "   ✅ $var configured"
    fi
done

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "⚠️  Missing $MISSING environment variables!"
    echo "   Edit .env.osint and add them, then run this script again"
    echo ""
    echo "   Example:"
    echo "   HACKERONE_PAT=your_actual_token"
    echo "   BUGCROWD_API_KEY=your_key"
    echo ""
    exit 1
fi

echo ""
echo "✅ Configuration verified!"
echo ""

# Run the coordinator
echo "Starting coordinator..."
./venv/bin/python3 master_coordinator.py
