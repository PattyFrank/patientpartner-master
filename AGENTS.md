# Agent Instructions — PatientPartner Master

**For Cursor and Claude agents working on this project.**

---

## Reference Content: Use Markdown, Not PDFs

All 23 PDFs have been converted to Markdown in `./reference-extracted/`. 

| Do | Don't |
|----|-------|
| Read `./reference-extracted/**/*.md` | Read or parse PDF files |
| Use .md for context, search, summarization | Assume PDF content is accessible |

**Why:** Markdown is token-efficient, fully searchable, and natively supported by both Cursor and Claude. PDFs require extraction; the work is already done.

---

## Folder Structure

- `./reference-extracted/` — **Primary source** for all reference content. Mirrors original PDF folders.
- `./brand/` — Brand memory (voice, positioning, audience, competitors). Vibe Skills read/write here.
- `./campaigns/` — Campaign assets and copy.

---

## When Refining Brand Files

1. **voice-profile.md** — Read: `reference-extracted/Branding /`, `reference-extracted/Commercial Pharma /`, `reference-extracted/Positioning /`
2. **positioning.md** — Read: `reference-extracted/Positioning /`, `reference-extracted/Competitor Analysis /`, `reference-extracted/Commercial Pharma /`
3. **audience.md** — Read: `reference-extracted/Ideal Customer Profiles (ICP) /`, `reference-extracted/Commercial Pharma /`
4. **competitors.md** — Read: `reference-extracted/Competitor Analysis /`
5. **Proof blocks** — Read: `reference-extracted/Research Reports & Case Studies /`

---

## Re-converting PDFs

If PDFs are updated, re-run:

```bash
cd ~/projects/patientpartner-master
.venv/bin/python scripts/convert-pdfs-to-markdown.py
```

Requires: `pip install pymupdf4llm` (already in .venv)

---

## Content Platforms: LinkedIn Only

Social and atomized content for PatientPartner is **LinkedIn only**. Do not create Twitter/X, Instagram, TikTok, Threads, Bluesky, or Reddit content. See `.cursor/rules/content-platforms.mdc`.

---

## Pushing to GitHub

The agent **cannot** run `git push` (no interactive credentials). After the agent commits:

- **Source Control:** `Ctrl+Shift+G` → `...` → Push
- **Terminal:** `` Ctrl+` `` → `git push origin main`

See `.cursor/rules/git-push.mdc` for auth setup and options.
