#!/bin/bash

echo "=== Wilsons-Raiders Test Hunt Execution ==="

# Ensure DB_ENCRYPTION_KEY is set
if [ -z "$DB_ENCRYPTION_KEY" ]; then
    echo "[ERROR] DB_ENCRYPTION_KEY is not set. Please run debug_setup.sh first or set it manually."
    exit 1
fi

# Run the orchestrator with a test target
TEST_PROGRAM_NAME="DebugTestProgram"
TEST_TARGET="scanme.nmap.org"

echo "\n--- Running Orchestrator for Program: $TEST_PROGRAM_NAME, Target: $TEST_TARGET ---"

python3 orchestrator/orchestrator.py

# Note: The orchestrator.py script's __main__ block already calls run_hunt
# with a test target. This script simply executes the orchestrator.

echo "\n=== Test Hunt Execution Complete ==="
echo "Review the output above for any errors or warnings."
echo "You can also check the database (wilsons_raiders.db) for new assessments and vulnerabilities."
