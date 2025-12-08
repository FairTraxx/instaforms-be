#!/bin/bash
# Vercel Build Hook
# This runs during deployment

echo "Starting build process..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"

