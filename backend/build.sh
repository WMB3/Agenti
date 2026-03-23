#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Install Playwright and its system dependencies (CRITICAL for Render)
playwright install chromium
playwright install-deps chromium
