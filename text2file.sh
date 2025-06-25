#!/bin/bash
# Wrapper script to run text2file through Poetry

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Run the command through Poetry
poetry run python -m text2file "$@"
