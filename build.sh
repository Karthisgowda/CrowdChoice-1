#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r pyproject.toml

# Run database migrations
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created successfully!')"