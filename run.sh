#!/bin/sh
# Run Marlinspike from this local install directory, but don't lose where this was called from.

# Where were we called from?
PREVIOUS_PATH="$(pwd)"

# Go to the Marlinespike install
cd "$(dirname "$0")"
# Get the path
MAR_PATH="$(pwd)"

# Go back to where we were called from
cd "$PREVIOUS_PATH"

# Add the Marlinespike path to Python Path
PYTHONPATH="$MAR_PATH:$PYTHONPATH"

# Call the .virtualenv python with marlinspike.
"$MAR_PATH/.virtualenv/bin/python" "$MAR_PATH/bin/marlinespike.py"
