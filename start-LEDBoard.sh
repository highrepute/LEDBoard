#!/bin/bash
# ------------------------------------------------------------------
# start-LEDBoard.sh
# Fully updated to work with virtualenv and system sudo
# Logs output to logfile.txt in the same folder as the script
# ------------------------------------------------------------------

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create logfile.txt in the same folder
LOGFILE="$SCRIPT_DIR/logfile.txt"

# Redirect all output (stdout + stderr) to logfile
exec &> "$LOGFILE"

# Activate your virtual environment
VENV_PATH="$HOME/my-venv"
source "$VENV_PATH/bin/activate"

# Run the main Python script with sudo for GPIO access
sudo "$VENV_PATH/bin/python" "$SCRIPT_DIR/DiscoMain.py"
