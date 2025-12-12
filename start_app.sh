#!/bin/bash

cleanup() {
    echo "Stopping all services..."
    kill $(jobs -p)
    exit
}

trap cleanup SIGINT

echo "🚀 Starting Ai_Dash Services..."

echo "Starting Backend Server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Celery Worker..."
celery -A backend.celery_app.celery_app worker --loglevel=info &
CELERY_PID=$!

echo "Starting Frontend..."
streamlit run frontend/streamlit_app.py &
FRONTEND_PID=$!

wait $BACKEND_PID $CELERY_PID $FRONTEND_PID
