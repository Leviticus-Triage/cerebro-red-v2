#!/bin/bash
# Monitor experiment with automatic terminal recording
# Usage: ./monitor_experiment.sh [experiment_id]

set -e

EXPERIMENT_ID="${1:-}"
RECORDING_DIR="${RECORDING_DIR:-recordings}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${RECORDING_DIR}/experiment_${EXPERIMENT_ID:-unknown}_${TIMESTAMP}.log"

# Create recordings directory if it doesn't exist
mkdir -p "$RECORDING_DIR"

echo "=========================================="
echo "Experiment Monitoring & Recording"
echo "=========================================="
echo "Experiment ID: ${EXPERIMENT_ID:-'Not specified'}"
echo "Recording to: $LOG_FILE"
echo "Start Time: $(date)"
echo ""
echo "Press Ctrl+C to stop recording"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "=========================================="
    echo "Stopping recording..."
    echo "End Time: $(date)"
    echo "Log saved to: $LOG_FILE"
    echo "=========================================="
    
    # Kill background processes
    kill $BACKEND_LOG_PID $FRONTEND_LOG_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start recording with script
if command -v script &> /dev/null; then
    # Use script with tee for live viewing
    script -f >(tee "$LOG_FILE") << SCRIPT_END

# Log experiment info
echo "=== Experiment Information ==="
if [ -n "$EXPERIMENT_ID" ]; then
    echo "Experiment ID: $EXPERIMENT_ID"
    echo ""
    echo "=== Current Status ==="
    curl -s -H "X-API-Key: test" "http://localhost:9000/api/scan/status/$EXPERIMENT_ID" | jq . || echo "Status check failed"
    echo ""
fi

echo "=== Starting Backend Logs ==="
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
docker compose logs -f cerebro-backend &
BACKEND_LOG_PID=\$!

echo "=== Starting Frontend Logs ==="
docker compose logs -f cerebro-frontend &
FRONTEND_LOG_PID=\$!

echo ""
echo "=== Monitoring Active ==="
echo "Backend PID: \$BACKEND_LOG_PID"
echo "Frontend PID: \$FRONTEND_LOG_PID"
echo ""
echo "Waiting for experiment to complete..."
echo "Press Ctrl+C to stop monitoring"
echo ""

# Wait for user interrupt
wait

SCRIPT_END
else
    # Fallback: Simple tee logging
    echo "Warning: 'script' not found, using basic logging"
    echo "Install with: sudo apt-get install bsdutils"
    echo ""
    
    exec > >(tee -a "$LOG_FILE") 2>&1
    
    echo "=== Experiment Monitoring ==="
    if [ -n "$EXPERIMENT_ID" ]; then
        echo "Experiment ID: $EXPERIMENT_ID"
        curl -s -H "X-API-Key: test" "http://localhost:9000/api/scan/status/$EXPERIMENT_ID" | jq .
    fi
    
    echo "=== Backend Logs ==="
    cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2
    docker compose logs -f cerebro-backend
fi
