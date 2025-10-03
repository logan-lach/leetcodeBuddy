#!/bin/bash

# Test runner script for leetcodeBuddy backend
# This script sets up the environment and runs the test suite

set -e  # Exit on error

echo "========================================="
echo "LeetCode Buddy Backend Test Suite"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Running tests..."
echo ""

# Run tests with different options based on arguments
if [ "$1" = "coverage" ]; then
    echo "Running tests with coverage report..."
    python -m pytest --cov=routes --cov-report=html --cov-report=term
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
elif [ "$1" = "verbose" ]; then
    echo "Running tests in verbose mode..."
    python -m pytest -vv
elif [ "$1" = "quick" ]; then
    echo "Running tests in quick mode..."
    python -m pytest -q
else
    echo "Running tests in standard mode..."
    python -m pytest
fi

echo ""
echo "========================================="
echo "Test run complete!"
echo "========================================="
