# PatientPartner Master Project

Enterprise B2B SaaS. Mentor-driven patient engagement for pharma, med-tech, and clinical trials.

---

## Setup

### Cursor
1. **File → Open Folder** → Select `~/projects/patientpartner-master`
2. The `.cursor/rules/patientpartner-brand.mdc` rule applies automatically.
3. Vibe Marketing Skills load from `~/.claude/skills/` (if installed).
4. Run `/start-here` in Agent chat to begin.

### Claude Code (Desktop or CLI)
1. Open Claude Code: `claude` (terminal) or launch Claude Code Desktop app.
2. Navigate to project:
   ```bash
   cd ~/projects/patientpartner-master
   ```
3. Read `CLAUDE.md` for context.
4. Run `/start-here` or any skill: `/brand-voice`, `/positioning-angles`, etc.

### Claude Code Terminal
1. In terminal:
   ```bash
   cd ~/projects/patientpartner-master
   claude
   ```
2. At the Claude prompt, type `/start-here` to orchestrate.
3. Skills use `./brand/` and project PDFs as context.

---

## Project Contents

- **23 PDF assets** (original) — Branding, Clinical Trials, Commercial Pharma, Competitor Analysis, ICP, Medical Device, PerfectPatient, Positioning, Research Reports & Case Studies
- **23 Markdown extracts** in `./reference-extracted/` — AI-optimized. **Agents: read these, not PDFs.**
- **Brand memory** — ./brand/ (voice, positioning, audience, competitors, stack, assets, learnings)
- **Vibe Marketing Skills** — Install to ~/.claude/skills/ via skills-v2 install script

---

## PDF → Markdown Conversion

All PDFs are converted to Markdown for AI context. To re-convert after updating PDFs:

```bash
cd ~/projects/patientpartner-master
.venv/bin/python scripts/convert-pdfs-to-markdown.py
```

Output: `./reference-extracted/` (mirrors folder structure)

---

## Quick Start

1. Open project in Cursor or Claude Code.
2. Run `/start-here` — Project scan, brand foundation, skill routing.
3. Use PDFs to refine brand files — Extract content, update voice-profile, positioning, audience.
4. Run execution skills — /direct-response-copy, /lead-magnet, /email-sequences, etc.

---

## Accessing This Project in Claude & Claude Code

**Claude doesn't auto-discover projects.** You must point it at this folder.

### Terminal (Claude Code CLI)
```bash
cd ~/projects/patientpartner-master
claude
```
**Quick launch:** Run `claude-pp` from terminal (script at `~/bin/claude-pp`). If `claude-pp` not found, add to `~/.zshrc`:
```bash
export PATH="$HOME/bin:$PATH"
alias claude-pp='~/projects/patientpartner-master/open-in-claude.sh'
```

### Claude Code Inside Cursor
**File → Open Folder** → select `~/projects/patientpartner-master`. Claude Code uses Cursor's open workspace.

### Claude Desktop App
Use **Project folder** selector when starting a session, or run `/add-dir /Users/patrickfrank/projects/patientpartner-master` mid-session.

### Workspace File (Cursor)
**File → Open Workspace from File** → `~/projects/patientpartner-master/patientpartner.code-workspace`

---

## Skills Install (if not already done)

```bash
cd ~/Desktop/skills-v2
./_system/scripts/install.sh
```

This installs Vibe Marketing Skills to `~/.claude/skills/` for Claude Code and Cursor.
