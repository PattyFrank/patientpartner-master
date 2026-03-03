#!/bin/bash
# Open PatientPartner Master in Cursor
# Usage: ./open-in-cursor.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cursor "$SCRIPT_DIR" 2>/dev/null || open -a "Cursor" "$SCRIPT_DIR"
