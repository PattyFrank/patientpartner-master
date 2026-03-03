#!/bin/bash
# Push PatientPartner Master to GitHub
# Run this from your terminal (where your GitHub credentials work)

set -e
cd "$(dirname "$0")/.."

REPO_URL="https://github.com/new?name=patientpartner-master&description=Enterprise+B2B+SaaS.+Mentor-driven+patient+engagement+platform+for+pharma,+med-tech,+and+clinical+trials."

echo "Opening GitHub to create the repository..."
open "$REPO_URL"

echo ""
echo "Create the repo on GitHub (Private, no README/.gitignore)."
echo "Then press Enter to push..."
read -r

git push -u origin main

echo ""
echo "Done. Repo: https://github.com/PattyFrank/patientpartner-master"
