#!/bin/bash
set -e

echo "Starting Image Hash Service..."

# Execute main application
exec python3 main.py
