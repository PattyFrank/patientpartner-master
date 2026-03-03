# PatientPartner — Master Project Context

> **Single source of truth** for all PatientPartner marketing work.  
> Use with Vibe Marketing Skills in Cursor, Claude Code, and Claude Code Terminal.

---

## Business Snapshot

- **What:** Enterprise B2B SaaS. Mentor-driven patient engagement platform for pharma, med-tech, and clinical trials.
- **How:** Connects patients to prior patients (mentors) for real-time peer-to-peer support.
- **Website:** patientpartner.com

---

## Project Structure

```
patientpartner-master/
├── PROJECT.md              ← You are here (master context)
├── CLAUDE.md                ← Claude Code project context
├── .cursor/
│   └── rules/
│       └── patientpartner-brand.mdc   ← Cursor rule (always apply)
├── brand/                   ← Brand memory (Vibe Skills read/write)
│   ├── voice-profile.md
│   ├── positioning.md
│   ├── audience.md
│   ├── competitors.md
│   ├── stack.md
│   ├── assets.md
│   ├── learnings.md
│   └── reference-index.md
├── campaigns/               ← Campaign assets
├── reference-extracted/     ← **Markdown (AI-optimized)** — READ THESE, not PDFs
│   ├── Branding /
│   ├── Clinical Trials /
│   ├── Commercial Pharma /
│   ├── Competitor Analysis /
│   ├── Ideal Customer Profiles (ICP) /
│   ├── Medical Device /
│   ├── PerfectPatient/
│   ├── Positioning /
│   └── Research Reports & Case Studies /
├── Branding/                ← PDF (original)
├── Clinical Trials/         ← PDF (original)
├── Commercial Pharma/       ← PDF (original)
├── Competitor Analysis/     ← PDF (original)
├── Ideal Customer Profiles (ICP)/  ← PDF (original)
├── Medical Device/          ← PDF (original)
├── PerfectPatient/          ← PDF (original)
├── Positioning/             ← PDF (original)
└── Research Reports & Case Studies/  ← PDF (original)
```

---

## Brand Memory Map

| File | Purpose | Owner |
|------|---------|-------|
| ./brand/voice-profile.md | Tone, vocabulary, personality | /brand-voice |
| ./brand/positioning.md | Market angles, hooks | /positioning-angles |
| ./brand/audience.md | ICPs, pains, triggers | Research |
| ./brand/competitors.md | Landscape, white space | Research |
| ./brand/stack.md | Tools, APIs | /start-here |
| ./brand/assets.md | Asset registry | All skills |
| ./brand/learnings.md | What works/doesn't | All skills |
| ./brand/reference-index.md | PDF asset index | Manual |

---

## Quick Reference (for AI)

- **Voice:** Evidence-based, professional. Lead with data (68%, 71%, 90%, 29%, 133.5 days). CEO warmth in letters.
- **Primary angle:** Peer-to-Peer Beats Everything. "They get patients to the door. We get them through it."
- **Competitive wedges:** "Stories build belief. Mentorship changes behavior." (vs Snow) / "Instant peer connection, not just engagement programs." (vs Reverba)
- **ICPs:** Director Patient Support (pharma), Director Patient Engagement (med-tech), Clinical Ops (trials), CCO, Innovation, Compliance, Market Access.
- **Key proof:** 68% more starts, 71% decision impact, 73% connection rate, 90% confidence boost, 29% adherence, 133.5 days on therapy.
- **Differentiator:** Real-time mentorship (not coordinator-driven). The "missing middle"—psychological barriers (fear, doubt) that hubs don't solve.
- **PerfectPatient:** AI mentor for brand.com. Same voice. "Technology amplifies empathy, not replaces it."

---

## PDF Asset Library (23 files)

| Category | Count | Key files |
|----------|-------|-----------|
| Branding | 1 | Brand Guidelines 2021 |
| Clinical Trials | 3 | Mentor program, capabilities deck |
| Commercial Pharma | 1 | 2026 Capabilities Deck |
| Competitor Analysis | 3 | Executive summary, matrix, differentiator |
| ICP | 3 | Overview, role list, roles outline |
| Medical Device | 1 | GEN CAP 25 |
| PerfectPatient | 3 | FAQ, one-pager, AI engagement |
| Positioning | 1 | Re-Positioning Document |
| Research & Case Studies | 8 | Benchmark, case studies, white papers |

**Use:** Read `./reference-extracted/` Markdown files (not PDFs). Markdown is token-efficient and fully searchable. See ./brand/reference-index.md for full inventory.

---

## Vibe Marketing Skills

Run `/start-here` to orchestrate. Skills:

- /brand-voice — Voice profile
- /positioning-angles — Market angles
- /direct-response-copy — Landing pages, sales copy
- /keyword-research — Keyword strategy
- /seo-content — Blog, long-form
- /email-sequences — Email automations
- /lead-magnet — Lead magnets
- /newsletter — Newsletter editions
- /content-atomizer — Repurpose across platforms
- /creative — Images, video, ads

**Skills location:** ~/.claude/skills/ (shared with Claude Code and Cursor)
