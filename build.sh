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

# Initialize database
python init_db.py

# Seed data if needed
python seed_data.py 