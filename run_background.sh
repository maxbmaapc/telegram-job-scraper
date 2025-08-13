#!/bin/bash

# Telegram Job Scraper Background Runner
# This script runs the scraper in the background and restarts it if it crashes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/scraper.log"
PID_FILE="$SCRIPT_DIR/scraper.pid"

echo "Starting Telegram Job Scraper in background..."
echo "Log file: $LOG_FILE"
echo "PID file: $PID_FILE"

# Function to cleanup on exit
cleanup() {
    echo "Stopping scraper..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID 2>/dev/null
        rm -f "$PID_FILE"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the scraper in background
cd "$SCRIPT_DIR"
nohup python run.py --mode continuous > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "Scraper started with PID: $(cat $PID_FILE)"
echo "To stop: kill $(cat $PID_FILE)"
echo "To view logs: tail -f $LOG_FILE"

# Wait for the process
wait $(cat "$PID_FILE")
