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

# Use virtualenv if present (Pi 4), otherwise fall back to system python3 (Pi 3)
VENV_PATH="$HOME/my-venv"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    sudo "$VENV_PATH/bin/python" "$SCRIPT_DIR/DiscoMain.py"
else
    sudo python3 "$SCRIPT_DIR/DiscoMain.py"
fi
