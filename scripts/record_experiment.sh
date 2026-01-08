#!/bin/bash
# Script to record terminal session during experiment execution
# Usage: ./record_experiment.sh [experiment_id] [output_file]

set -e

EXPERIMENT_ID="${1:-}"
OUTPUT_FILE="${2:-experiment_$(date +%Y%m%d_%H%M%S).log}"

echo "=========================================="
echo "Experiment Terminal Recording Script"
echo "=========================================="
echo "Output file: $OUTPUT_FILE"
echo "Experiment ID: ${EXPERIMENT_ID:-'Not specified'}"
echo ""
echo "Recording started at: $(date)"
echo "Press Ctrl+D or type 'exit' to stop recording"
echo "=========================================="
echo ""

# Method 1: Using 'script' command (built-in, most compatible)
if command -v script &> /dev/null; then
    echo "Using 'script' command for recording..."
    script -a "$OUTPUT_FILE" -c "bash"
    
# Method 2: Using 'asciinema' (modern, interactive)
elif command -v asciinema &> /dev/null; then
    echo "Using 'asciinema' for recording..."
    asciinema rec "$OUTPUT_FILE"
    
# Method 3: Fallback - simple tee logging
else
    echo "Using 'tee' for basic logging..."
    echo "Note: This only captures stdout/stderr, not full terminal interaction"
    exec > >(tee -a "$OUTPUT_FILE") 2>&1
    bash
fi

echo ""
echo "=========================================="
echo "Recording stopped at: $(date)"
echo "Output saved to: $OUTPUT_FILE"
echo "=========================================="
