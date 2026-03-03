#!/bin/bash
# Open PatientPartner Master in Claude Code (Terminal)
# Usage: ./open-in-claude.sh
# Or add to ~/.zshrc: alias claude-pp='~/projects/patientpartner-master/open-in-claude.sh'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PatientPartner Master — Claude Code"
echo "  $(pwd)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Run /start-here to begin."
echo ""
exec claude
