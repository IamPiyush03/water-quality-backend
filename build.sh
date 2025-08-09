#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p models
mkdir -p data

# Copy model files if they exist
if [ -f "models/water_quality_model.joblib" ]; then
    echo "Model file found"
else
    echo "Training model..."
    python train_model.py
fi

# Database initialization will happen during application startup
echo "Database will be initialized during application startup" 