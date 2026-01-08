#!/bin/bash
# Phase 7: Test Execution Helper Script
# Runs tests in Docker container with all dependencies available

set -e

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  PHASE 7: TEST EXECUTION HELPER"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to run backend tests in Docker
run_backend_tests() {
    echo "🔧 Running backend tests in Docker container..."
    echo ""
    
    # Start backend container if not running
    if ! docker ps | grep -q cerebro-backend; then
        echo "Starting backend container..."
        docker compose up -d cerebro-backend
        sleep 5
    fi
    
    # Check if test file exists in container
    TEST_PATH="$1"
    echo "Checking test file: $TEST_PATH"
    if ! docker compose exec cerebro-backend test -f "$TEST_PATH" 2>/dev/null; then
        echo "⚠️  Test file not found in container: $TEST_PATH"
        echo "Listing available test files:"
        docker compose exec cerebro-backend find tests -name "*.py" -type f 2>/dev/null || echo "No tests directory found"
        return 1
    fi
    
    # Run tests
    echo "Running: $TEST_PATH"
    docker compose exec cerebro-backend pytest "$TEST_PATH" -v -s
}

# Function to run frontend tests
run_frontend_tests() {
    echo "🎨 Running frontend E2E tests..."
    echo ""
    cd frontend
    npx playwright test "$1"
    cd ..
}

# Parse command line arguments
case "${1:-all}" in
    payload)
        run_backend_tests "tests/test_payload_coverage.py"
        ;;
    enum)
        run_backend_tests "tests/test_enum_sync.py"
        ;;
    rotation)
        run_backend_tests "tests/test_strategy_rotation.py"
        ;;
    integration)
        run_backend_tests "tests/test_integration_strategy_rotation.py"
        ;;
    mutator)
        run_backend_tests "tests/test_mutator_all_strategies.py"
        ;;
    frontend)
        run_frontend_tests "test_all_strategies.spec.ts"
        ;;
    backend)
        echo "Running all Phase 7 backend tests..."
        run_backend_tests "tests/test_payload_coverage.py"
        run_backend_tests "tests/test_enum_sync.py"
        ;;
    all)
        echo "Running all Phase 7 tests..."
        run_backend_tests "tests/test_payload_coverage.py"
        run_backend_tests "tests/test_enum_sync.py"
        run_frontend_tests "test_all_strategies.spec.ts"
        ;;
    *)
        echo "Usage: $0 [payload|enum|rotation|integration|mutator|frontend|backend|all]"
        echo ""
        echo "Options:"
        echo "  payload      - Run payload coverage tests"
        echo "  enum         - Run enum synchronization tests"
        echo "  rotation     - Run strategy rotation tests"
        echo "  integration  - Run integration tests"
        echo "  mutator      - Run mutator tests"
        echo "  frontend     - Run frontend E2E tests"
        echo "  backend      - Run all backend Phase 7 tests"
        echo "  all          - Run all Phase 7 tests (default)"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  TEST EXECUTION COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════════"
