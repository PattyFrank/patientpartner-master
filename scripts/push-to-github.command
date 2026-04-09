#!/bin/bash
cd "$(dirname "$0")/.."
echo "Pushing to GitHub..."
echo "Enter your GitHub username and token when prompted."
echo ""
git push origin main
echo ""
echo "Press any key to close..."
read -n 1
