#!/bin/bash

# Download and install Python
echo "Downloading and installing Python..."
curl -o python-installer.exe https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

# Verify Python installation
echo "Verifying Python installation..."
python --version

# Set up a virtual environment
echo "Setting up a virtual environment..."
python -m venv venv

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/Scripts/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

echo "Setup completed successfully."
