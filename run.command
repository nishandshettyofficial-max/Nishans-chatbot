#!/bin/bash
# Move to project directory
cd "$(dirname "$0")"

# Activate the local virtual environment
source .venv/bin/activate
export HOME="$(pwd)"

# Start the Streamlit application and open the browser
streamlit run app.py --browser.gatherUsageStats=false
