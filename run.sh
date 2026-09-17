#!/bin/bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODE="${1:-modern}"

if [ "$MODE" = "streamlit" ]; then
    echo "🚀 Starting HireLens.AI Classic Streamlit App on http://127.0.0.1:8501..."
    "$DIR/.venv/bin/streamlit" run "$DIR/app.py"
elif [ "$MODE" = "dev" ]; then
    echo "⚡ Starting HireLens.AI in Full-Stack Developer Mode (FastAPI + Vite Dev Server)..."
    echo "   Backend:  http://127.0.0.1:8000"
    echo "   Frontend: http://127.0.0.1:5173 (with Hot Module Replacement)"
    "$DIR/.venv/bin/uvicorn" api:app --host 127.0.0.1 --port 8000 --reload &
    BACKEND_PID=$!
    trap "kill $BACKEND_PID" EXIT INT TERM
    cd "$DIR/frontend" && npm run dev
else
    echo "✨ Launching HireLens.AI Senior UI/UX Application on http://127.0.0.1:8000..."
    if [ ! -d "$DIR/frontend/dist" ]; then
        echo "📦 Building optimized React SPA bundle..."
        (cd "$DIR/frontend" && npm run build)
    fi
    "$DIR/.venv/bin/uvicorn" api:app --host 127.0.0.1 --port 8000
fi
