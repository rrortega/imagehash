#!/bin/bash
set -e

echo "Starting Image Hash Service..."

# Execute main application using Gunicorn for production
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 main:app
