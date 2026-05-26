#!/bin/bash

# Check if the 'env' directory already exists
if [ -d "env" ]; then
    echo "The virtual environment 'env' already exists. Installation is canceled."
    sleep 10
    exit 1
fi

# Check if the 'requirements.txt' file exists
if [ ! -f "requirements.txt" ]; then
    echo "'requirements.txt' file not found! Please make sure the file exists in the current directory."
    sleep 10
    exit 1
fi

# Step 1: Create a virtual environment in the 'env' directory
echo "Creating a virtual environment in the 'env' directory..."
python3 -m venv env

# Step 2: Activate the virtual environment
echo "Activating the virtual environment..."
# shellcheck disable=SC1091
source env/bin/activate

# Step 3: Install the dependencies from 'requirements.txt'
echo "Installing dependencies from 'requirements.txt'..."
pip3 install -r requirements.txt

# Notify that the environment is set up
echo "Virtual environment created and dependencies installed successfully."
