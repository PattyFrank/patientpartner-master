# PRD: PatientPartner Competitor Comparison Landing Page

**Document Type:** Product Requirements Document  
**Status:** Draft v1.0  
**Date:** February 27, 2026  
**Owner:** Marketing / Growth  
**Audience:** Engineering, Design, Content, Marketing  

---

## Table of Contents

1. [Overview & Business Objective](#1-overview--business-objective)
2. [Research: Best-in-Class Benchmarks](#2-research-best-in-class-benchmarks)
3. [Competitive Context: Who We're Comparing Against](#3-competitive-context-who-were-comparing-against)
4. [URL Architecture & Page Structure](#4-url-architecture--page-structure)
5. [Hub Page: Full Page Specifications](#5-hub-page-patientpartnercomcompare)
6. [Individual Competitor Pages: Full Specifications](#6-individual-competitor-pages)
7. [Comparison Matrix Dimensions](#7-comparison-matrix-dimensions)
8. [Copy Strategy & Messaging Framework](#8-copy-strategy--messaging-framework)
9. [Design & UX Requirements](#9-design--ux-requirements)
10. [SEO Requirements](#10-seo-requirements)
11. [CTA Strategy](#11-cta-strategy)
12. [Technical Requirements](#12-technical-requirements)
13. [Analytics & Success Metrics](#13-analytics--success-metrics)
14. [Content Governance](#14-content-governance)
15. [Launch Checklist](#15-launch-checklist)

---

## 1. Overview & Business Objective

### What We're Building

A dedicated comparison section on patientpartner.com that lets enterprise pharma and med-tech decision-makers evaluate PatientPartner against alternative solutions — on our terms, with our data, in our voice.

This is not a feature checklist. It's a conversion engine built to intercept buyers at the highest-intent moment of their research cycle and move them to a demo request.

### Why Now

Interviews with prospects surface a consistent objection: *"Who else is doing this?"* Comparison pages are the evidence buyers look for when they're close to a decision. Without them, that research happens off-site, on G2, on analyst reports, or on Snow Companies' and Reverba's own websites — all of which frame the narrative in someone else's favor.

By building this infrastructure, PatientPartner:
- Controls the narrative during the competitor research phase
- Captures high-intent organic search traffic (searches like "PatientPartner vs Reverba", "Snow Companies alternative", "patient mentorship platform comparison")
- Reduces time-to-decision for prospects who have already done early research
- Gives the sales team shareable, credible comparison assets

### Business Goals

| Goal | Target |
|------|--------|
| Increase demo request conversion from comparison page visitors | ≥ 15% CVR |
| Capture organic traffic for competitor-intent keywords | Top 3 position for target terms within 6 months |
| Reduce sales cycle length by surfacing comparison content earlier | 15–20% reduction in days to first demo |
| Create sales-shareable assets from page content | 3 x 1-page PDF exports per competitor |

---

## 2. Research: Best-in-Class Benchmarks

Research was conducted on the highest-performing B2B SaaS comparison pages. The following patterns consistently appear on the top-converting examples.

### ClickUp (clickup.com/compare)

ClickUp's comparison section is the gold standard for scale and comprehensiveness.

**Structure:**
- Hub page (`/compare`) with an interactive competitor selector and tabbed feature comparison matrix
- Individual pages per competitor (`/compare/asana-vs-clickup`) with deep narrative content
- Feature matrix organized by category tabs: Views, Customization, Collaboration, Reporting
- "Included / Not Included / Included but see why ClickUp is better" system creates nuanced, credible comparisons
- FAQ section at the bottom of the hub page

**What makes it work:**
- The competitor selector is above the fold — visitors self-segment immediately
- Category tabs reduce cognitive load from a massive feature table
- "Included but see why we're better" phrasing is more believable than a binary win/loss chart
- Every feature links to a feature detail page — demonstrates depth and drives further engagement

### Notion (notion.com/compare-against)

Notion's comparison pages are narrative-first, data-reinforced.

**Structure:**
- Hero with a clear "why teams choose Notion" headline + dual CTA
- Trusted-by brand logos immediately below the hero
- Clean 2-column comparison table (competitor vs. Notion) with check/X icons
- G2 rating section with specific percentage scores (not vague claims)
- Benefit narrative section: 3 columns, each with an image + explanation
- Outcome stats bar (98% save time, 70% replaced 2+ tools, etc.)
- Customer testimonial
- Templates section
- Final CTA

**What makes it work:**
- Narrative-first approach works for B2B because it answers "why" not just "what"
- G2 data is a third-party trust signal — not PatientPartner claiming superiority
- Outcome stats are specific and attributed to research

### Monday.com (monday.com/alternative)

Monday's single hub page with tabbed competitor navigation stands out.

**Structure:**
- Hub page where you pick any competitor from tabs — no separate URLs
- Bar chart for review scores (visual, immediate, competitor-labeled)
- Feature carousel below that
- FAQs + links to related content

**What makes it work:**
- Single URL with all competitors means SEO consolidation
- Review bar chart is visually powerful and immediately credible

### ActiveCampaign (activecampaign.com/compare/mailchimp)

**What makes it work:**
- Side-by-side plan comparison showing more features for less money — value framing, not feature war
- Customer reviews from G2 embedded directly on page
- Case studies and user stories that demonstrate outcomes, not just capabilities

### BambooHR Comparison Pages

**What makes it work:**
- Text-block approach (no table) focused on customer pain points, not features
- Works especially well for B2B audiences buying solutions to problems, not specs

### Key Patterns Synthesized

The highest-converting B2B SaaS comparison pages share these elements:

1. **Narrative hero** — Why your solution wins, not just that it does
2. **Trust signals immediately** — Logos, G2 badges, certifications
3. **Side-by-side comparison table** — Organized by category, with nuanced verdicts
4. **Data-driven outcome stats** — Specific numbers, not vague benefits
5. **Customer evidence** — Quotes or case studies from companies in the buyer's peer group
6. **FAQ section** — Addresses objections before the prospect can raise them
7. **Persistent CTA** — Demo request or free trial, visible at multiple scroll points

---

## 3. Competitive Context: Who We're Comparing Against

Based on the competitive analysis in `./brand/competitors.md` and `./reference-extracted/Competitor Analysis /`, PatientPartner has four primary comparison targets:

### Primary Comparisons (individual pages)

| Competitor | Category | Narrative Wedge |
|-----------|----------|-----------------|
| **Snow Companies** | Patient ambassador & storytelling agency (Omnicom-owned) | Stories build belief. Mentorship changes behavior. PP = outcomes, Snow = campaigns. |
| **Reverba** | Tech-enabled peer-to-peer mentoring (VC-backed, reverbaBRIDGE) | "Instant peer connection vs. engagement programs." PP is faster, less operationally heavy, built for the commercial drop-off moment. |
| **Internal Ambassador Programs** | DIY pharma-built programs | "Stop rebuilding the same program every launch." PP = infrastructure, not a project. |
| **PerfectPatient AI vs. Competitive AI** | AI-powered patient engagement (Hippocratic AI, Ostro, Hyro) | Only AI solution built to both convert on brand.com AND retain through ongoing mentorship. |

### Secondary Comparisons (hub page matrix, no individual pages initially)

| Competitor | Category |
|-----------|----------|
| **ConnectiveRx / Lash Group** | Hub / PSP services (complementary, not direct — framing: "PP fills the gap they leave") |
| **TrialX / WCG / Mural Health** | Clinical trial recruitment platforms (for the clinical trials audience) |

### What We Are NOT Doing

We are not comparing against general patient support platforms or CRMs. The comparison page lives in the specific territory of: **peer-to-peer patient mentorship, ambassador programs, and AI patient engagement.**

---

## 4. URL Architecture & Page Structure

### URL Map

```
patientpartner.com/compare                                    → Hub Page
patientpartner.com/compare/patientpartner-vs-snow-companies  → Individual Page
patientpartner.com/compare/patientpartner-vs-reverba         → Individual Page
patientpartner.com/compare/patientpartner-vs-internal-programs → Individual Page
patientpartner.com/compare/patientpartner-vs-perfectpatient-ai → Individual Page (if PerfectPatient is positioned as separate offering)
```

### Navigation Integration

- Add "Compare" as a navigation item under a "Why PatientPartner" dropdown
- Internal link from the main homepage, the "How It Works" page, and any bottom-of-funnel assets
- Sales team gets direct shareable URLs per competitor page

---

## 5. Hub Page: patientpartner.com/compare

The hub page is the entry point. It serves visitors who are in research mode but haven't yet identified a specific competitor. It also serves as the SEO consolidation point.

---

### Section 1: Hero

**Purpose:** Establish the comparison frame immediately. The visitor should know within 3 seconds that this page will help them decide.

**Layout:** Full-width, centered content. Dark background (PatientPartner brand colors). Competitor logos faded/greyed in the background to reinforce the comparison context.

**Headline (H1):**
> "See Why Pharma Teams Choose PatientPartner"

**Subheadline:**
> The only enterprise-grade peer-to-peer mentorship platform built for real-time patient activation. Compare us to the alternatives — side by side.

**Competitor Selector:**
A horizontal tab bar with logos of each competitor. Clicking a tab scrolls to or opens that comparison section.

```
[ Snow Companies ] [ Reverba ] [ Internal Programs ] [ AI Platforms ]
```

**CTAs:**
- Primary: `Book a Demo`
- Secondary: `See How We Compare →` (scrolls down)

---

### Section 2: Trust Bar

**Purpose:** Establish credibility before the comparison begins. Reduces buyer skepticism.

**Layout:** Full-width horizontal band. Light background.

**Content:**
- "Trusted by leading pharma and med-tech brands" (generic client logos where approved for display)
- Certification badges: HIPAA Compliant | SOC 2 Certified | ISO 27001

**Note on implementation:** Only display client logos where written permission exists. Use certification badges regardless.

---

### Section 3: The Problem We All Agree On

**Purpose:** Frame the market context in PatientPartner's favor. Establish the "missing middle" narrative before any comparison data.

**Layout:** 2-column layout (left: problem statement, right: visual or quote)

**Headline (H2):**
> "Patients enroll. Patients get approved. Then nothing."

**Body Copy:**
> The pharma industry spends billions on access programs — prior auth, copay, hub services. But patients still don't start. Not because they can't. Because they're scared, confused, and have no one to talk to.
>
> That gap — between "approved" and "actually starting" — is where treatment dropout lives. It's also where PatientPartner operates.
>
> We connect hesitating patients with real people who've been through the same thing, in real time. The result: 71% improvement in adherence. 30% more new patient starts. 133.5 fewer days to treatment decision.

**Supporting stat callout (3 boxes):**
```
[ 71% ]             [ 30% ]                  [ 133.5 days ]
Adherence           Increase in new          Faster treatment
improvement         patient starts           decisions
```

---

### Section 4: Competitor Selector + Quick Overview Matrix

**Purpose:** Let visitors self-select their comparison and immediately see the headline-level differences.

**Layout:** Sticky competitor tab bar. Below it, a 5-column quick comparison table.

**Table: PatientPartner vs. The Alternatives**

| Dimension | PatientPartner | Snow Companies | Reverba | Internal Program |
|-----------|---------------|----------------|---------|-----------------|
| **Program Type** | SaaS Platform | Agency / Services | Agency + Platform | DIY / Manual |
| **Connection Model** | Real-time, on-demand | Coordinator-scheduled calls | Scheduled, coordinator-managed | Coordinator-managed |
| **Time to First Connection** | Same day | Days to weeks | 7–14 day cadence | Varies |
| **Compliance Automation** | Automated KMS (AI flagging) | Manual staff monitoring | Staff monitoring on all calls | Manual |
| **Scalability** | Multi-brand, enterprise SaaS | Rebuilt per program | Built per program | Limited by headcount |
| **ROI Measurement** | Real-time dashboard, outcome attribution | Activity metrics only | Activity metrics, Excel reports | Inconsistent |
| **Pricing Model** | Subscription + engagement-based | Agency SOW (~$1M/program) | Agency SOW (~$1M/program) | Internal headcount + overhead |
| **HIPAA / SOC 2** | ✓ Certified | Compliant via process | Compliant via process | Variable |
| **White-label Ready** | ✓ Built-in | ✗ Not available | Limited | N/A |

**Visual treatment:** Each "PatientPartner" cell gets a green/brand-colored background. Competitor cells are grey/neutral. No negative messaging — just facts.

---

### Section 5: Deep-Dive Comparison Tabs

**Purpose:** For buyers who want to go deeper. Organized by decision criteria that pharma buyers actually use.

**Tab structure:**

```
[ Speed & Activation ] [ Compliance ] [ Technology ] [ ROI & Data ] [ Scalability ]
```

#### Tab 1: Speed & Activation

**Headline:** "When hesitation is highest, who connects fastest?"

**Content:**
- PatientPartner: Patients matched in real time based on disease state, treatment experience, and demographics. Mentor responds same day. No coordinator overhead.
- Snow: Coordinator schedules calls between patient and ambassador. Average 3–7 day lag to first connection. Programs require "Mentor Program Specialists" to manage scheduling and post-call evaluations.
- Reverba: 3-touch cadence goal within 7–14 days of signup. High-touch coordination. Engagement rate degraded by complex onboarding.
- Internal: Dependent on internal team bandwidth. Quality and speed inconsistent as programs scale.

**Visual:** Timeline graphic showing "Patient hesitates → First connection" across all four options.

#### Tab 2: Compliance & Oversight

**Headline:** "Automated compliance at scale, not just a process."

**Content:**
- PatientPartner: Keyword Monitoring System (KMS) — automated flagging of adverse events, off-label discussions, and compliance triggers. Every conversation is monitored programmatically. AE escalation is automated to compliance teams. HIPAA, SOC 2, ISO 27001 certified.
- Snow: Manual compliance monitoring. Staff assigned to review ambassador content. MLR approval required for all materials. Scalability is the ceiling.
- Reverba: All calls monitored by staff for compliance. High-touch — "every call requires a Reverba employee on the line." Compliance is strong but operationally expensive.
- Internal: No standardized KMS. Compliance quality tied to whichever team member is running the program. Degrades with staff turnover.

**Callout quote (from competitive research):**
> *"They're still faxing forms. If someone comes in with tech, it's game over."*
> — Former Industry Executive (Source: PatientPartner Competitive Analysis, 2024)

#### Tab 3: Technology

**Headline:** "A platform vs. a process."

**Content:**
- PatientPartner: Purpose-built SaaS. Real-time mentor matching algorithm. In-platform messaging, compliance automation, reporting dashboard, LMS for mentor training, API integrations with Salesforce, HubSpot, Veeva. White-label deployment.
- Snow: No proprietary platform. Salesforce + Veeva Vault PromoMats for submissions. Manual program management.
- Reverba: reverbaBRIDGE platform exists but programs still run through "high-touch service delivery and coordination workflows." Manual Excel reporting acknowledged by former employees as "biggest weakness."
- Internal: Microsoft Dynamics, Excel, email chains. "She was stuck working with us if she wanted the program." (Former Reverba client quote describing the lock-in of manual systems.)

**Feature comparison table (condensed):**

| Feature | PatientPartner | Snow | Reverba | Internal |
|---------|---------------|------|---------|----------|
| Real-time mentor matching algorithm | ✓ | ✗ | ✗ | ✗ |
| Automated compliance monitoring | ✓ | ✗ | Partial | ✗ |
| In-platform asynchronous chat | ✓ | ✗ | ✗ | ✗ |
| Real-time ROI dashboard | ✓ | ✗ | ✗ | ✗ |
| API integrations (Salesforce, Veeva) | ✓ | Partial | ✗ | ✗ |
| White-label deployment | ✓ | ✗ | Limited | N/A |
| LMS for mentor training | ✓ | ✗ | ✗ | ✗ |
| AE automated flagging | ✓ | ✗ | ✗ | ✗ |

#### Tab 4: ROI & Data

**Headline:** "Activity metrics vs. outcome attribution."

**Content:**
- PatientPartner: Real-time dashboards showing mentee readiness, sentiment scores, conversion to therapy start, adherence over time. Outcome data tied to engagement through proprietary attribution model. Roadmap includes tokenized claims data linkage (Datavant/HealthVerity) for verified ROI.
- Snow: Monthly/quarterly reports from Salesforce exports. ROI modeled retrospectively using lifetime value assumptions. Self-reported or third-party validation.
- Reverba: Weekly/monthly Excel reports. "Inconsistent due to turnover." Clients frustrated by lack of automation.
- Internal: No standardized reporting. Attribution varies by brand team and tool stack.

**Proof stat block:**
```
PatientPartner results across deployed programs:

  68%        71%         90%         30%
Patients    Adherence   Mentor      New patient
felt more   improvement satisfaction  starts lift
confident              rate
```

#### Tab 5: Scalability

**Headline:** "Deploy once. Scale everywhere."

**Content:**
- PatientPartner: Modular platform. Deploy one brand, then replicate across disease states with minimal rebuild. Enterprise onboarding includes integration sprints. Supports multi-brand, multinational programs from a single platform instance.
- Snow: Labor-intensive program builds. New brands require new recruiting, training, approvals, staffing. Omnicom ownership creates additional approval layers.
- Reverba: Growth-capital pressure creates efficiency demands, but service model still requires rebuilding per program. Mentor recruitment takes 8+ months for rare disease.
- Internal: Hard ceiling on scale. "Limited by bandwidth and turnover." As programs expand, documentation, training, and compliance degrade.

---

### Section 6: Social Proof

**Purpose:** Third-party validation from clients and measurable outcomes.

**Layout:** 2–3 testimonial cards + a case study link.

**Testimonial format:**
> Quote that specifically mentions the outcome or problem solved. No generic praise.

**Case study CTA:**
> "See how [Brand/Case Study Title] increased new patient starts by 30% →"

---

### Section 7: FAQ

**Purpose:** Pre-emptively handle the top objections that appear in the sales cycle. This is a conversion element, not just a UX element.

**Based on internal intel from the Positioning document — "why we lose deals":**

**Q: We're worried about compliance. How do you handle adverse events?**
> PatientPartner's Keyword Monitoring System (KMS) automatically flags adverse event language, off-label discussions, and compliance triggers in every mentor conversation. Escalations route to your compliance team in real time. Every interaction is logged, auditable, and compliant with HIPAA, SOC 2, and ISO 27001 standards. Unlike agency models that rely on a staff member listening to every call, PatientPartner automates what competitors do manually.

**Q: We already have an internal patient ambassador program. Why change?**
> Internal programs scale with headcount, not with patient volume. When a brand manager leaves, the program wobbles. When you launch a new drug, you rebuild. PatientPartner is infrastructure: deployed once, repeatable across brands, with automated compliance and real-time reporting your team doesn't have to maintain manually.

**Q: How is PatientPartner different from Snow Companies or Reverba?**
> Snow and Reverba are agency models — they build programs for you, staffed by coordinators, measured through Excel reports. PatientPartner is a SaaS platform: you own the infrastructure, deploy it across your portfolio, and get real-time data without operational overhead. Think of it the difference between hiring an agency to run a website versus owning your CMS.

**Q: What proof exists that this actually works?**
> PatientPartner has published case studies showing 71% improvement in adherence, 30% increase in new patient starts, and a 68% improvement in patient confidence across deployed programs. Ask your sales contact for condition-specific case study data.

**Q: How long does implementation take?**
> Most programs go live within 6–8 weeks. PatientPartner's Enterprise Integration Team runs on-site implementation sprints to minimize transition costs. Mentor sourcing and training are handled on the platform. MLR approval workflows are built into the onboarding process.

**Q: What does PatientPartner cost vs. a Snow or Reverba SOW?**
> Agency programs typically run $300K–$1.5M per brand per year as an annual SOW. PatientPartner's subscription + engagement model is structured to deliver comparable — or superior — outcomes at meaningfully lower total cost, with less operational overhead for your team. Schedule a demo for program-specific pricing.

---

### Section 8: Final CTA Block

**Layout:** Full-width section. Dark/brand color background. Centered content.

**Headline:**
> "Stop rebuilding the same program every launch."

**Subheadline:**
> PatientPartner deploys in weeks, runs across your entire brand portfolio, and proves ROI in real time. See it live.

**CTAs:**
- Primary: `Book a Demo`
- Secondary: `Download the Comparison Guide` (PDF gated lead magnet)

---

## 6. Individual Competitor Pages

Each individual competitor page lives at its own URL and goes deeper than the hub page matrix. It's designed to intercept a specific search query and convert a visitor who is actively comparing PatientPartner vs. that specific competitor.

---

### Page Template: patientpartner.com/compare/patientpartner-vs-[competitor]

**Every individual page follows this structure:**

---

#### Section 1: Hero

**H1 format:** `PatientPartner vs. [Competitor Name]: The Real Difference`

**Subheadline:** 1–2 sentence positioning statement specific to this competitor.

**CTA:** `Book a Demo` + `See Full Comparison ↓`

---

#### Section 2: The One-Line Difference

**Purpose:** A single, memorable positioning line that frames the entire page.

- vs. Snow: *"Snow builds patient stories. PatientPartner changes patient behavior."*
- vs. Reverba: *"Reverba is a program. PatientPartner is a platform."*
- vs. Internal: *"Your team builds strategy. PatientPartner runs the engine."*

---

#### Section 3: At a Glance Comparison Table

A 2-column table (PatientPartner vs. Competitor), covering 8–10 dimensions from the master matrix. Same visual treatment as hub page.

---

#### Section 4: Where We Win (Narrative Sections)

3–4 narrative sections, each with:
- A bold subheadline stating the win
- 2–3 paragraphs of supporting content
- A supporting data point or quote where available
- A relevant screenshot or diagram (product UI, compliance workflow, dashboard visual)

**For Snow Companies page:**
1. Speed: Real-time vs. coordinator-scheduled
2. Scalability: SaaS platform vs. per-program agency builds
3. Outcome attribution: ROI dashboard vs. modeled activity metrics
4. Compliance: Automated KMS vs. manual staff monitoring

**For Reverba page:**
1. Time to value: Instant connection vs. 7–14 day cadence
2. Operational drag: Less coordination overhead, fewer handoffs
3. Technology: Built platform vs. platform + heavy service layer
4. ROI clarity: Real-time outcomes vs. Excel-based reporting

**For Internal Programs page:**
1. Scale without headcount: Deploy vs. hire
2. Consistency as teams turn over
3. Compliance built in, not bolted on
4. Measurement: Attribution by the platform, not by the team

---

#### Section 5: Proof Block

2–3 case study snippets with stats specific to the buying trigger for this comparison.

---

#### Section 6: FAQ (Competitor-Specific)

4–5 questions specific to this competitive decision. Example for Snow:

> *"Can PatientPartner handle the compliance complexity Snow has historically managed?"*
> *"How does PatientPartner's mentor quality compare to Snow's Patient Ambassador® programs?"*

---

#### Section 7: CTA

Same persistent CTA block as hub page.

---

## 7. Comparison Matrix Dimensions

These are the 10 dimensions that appear across the hub page and all individual pages. They were selected based on:
- What pharma buyers actually evaluate when choosing a patient engagement partner
- Where PatientPartner objectively wins or can reframe the conversation
- What questions come up repeatedly in the sales cycle

| Dimension | Why It Matters to Buyers |
|-----------|--------------------------|
| **1. Connection Model** | Real-time vs. scheduled is the core behavioral wedge |
| **2. Time to First Mentor Connection** | Patients who wait lose momentum; buyers know this |
| **3. Compliance Automation** | CCOs and regulatory teams are buyers; this is non-negotiable |
| **4. Technology Infrastructure** | Determines scalability and internal operational burden |
| **5. Scalability Across Brands** | Enterprise pharma has multiple brands; per-program builds don't work |
| **6. ROI Attribution** | "Who else is doing this?" = "Can you prove ROI?" |
| **7. Implementation Speed** | Internal champions need to show quick wins to stakeholders |
| **8. Pricing Model** | SOW vs. subscription has procurement and budget implications |
| **9. White-label / Customization** | Brand teams need to deploy under their brand identity |
| **10. Data & Reporting Depth** | Real-time dashboard vs. monthly Excel slides |

---

## 8. Copy Strategy & Messaging Framework

### Voice Principles (from brand/voice-profile.md)

- **Bold without attacking.** We state facts about ourselves and observable facts about competitors. We do not make unsubstantiated claims.
- **Lead with the buyer's problem**, not our features. Buyers don't care about our platform until they see their problem reflected back at them.
- **Data anchors everything.** Every superiority claim is backed by a stat: 71%, 30%, 133.5 days, 90%, 68%.
- **Differentiate on category, not just features.** The most powerful line we have is: "They're agencies. We're a platform."

### Headline Formulas

| Context | Formula | Example |
|---------|---------|---------|
| Hub hero | "See why [buyer ICP] choose [us]" | "See Why Pharma Teams Choose PatientPartner" |
| Problem framing | "Patients [do X]. Then [bad thing happens]." | "Patients enroll. Patients get approved. Then nothing." |
| Category differentiation | "[Competitor] is a [what they are]. [PP] is a [what we are]." | "Reverba is a program. PatientPartner is a platform." |
| Feature win | "When [moment of truth], who [delivers]?" | "When hesitation is highest, who connects fastest?" |
| CTA | Imperative that names the outcome | "Stop rebuilding the same program every launch." |

### Phrases to Use

- "Real-time" (not "fast" or "quick")
- "Platform" (not "solution" or "tool")
- "Behavior change" (not "awareness" or "education")
- "Outcome attribution" (not "reporting")
- "Less operational drag" (not "cheaper" or "easier")
- "When hesitation is highest" (not "early in the journey")
- "Missing middle" (the gap between enrollment and first dose)

### Phrases to Avoid

- "Best-in-class" (generic, unsubstantiated)
- "Comprehensive solution" (agency speak)
- "Innovative" (everyone says this)
- Any direct claim about competitor pricing without documented comps
- "10x cheaper" or specific price multiples without hard quotes

---

## 9. Design & UX Requirements

### Interaction Patterns

**Competitor Selector (Hub Page)**
- Sticky tab bar that stays visible on scroll
- Clicking a tab smooth-scrolls to the corresponding comparison content
- Selected tab is visually active (brand color underline or background)
- On mobile: horizontal scroll or dropdown selector

**Comparison Table**
- PatientPartner column has a persistent brand-color highlight (left border or background tint)
- Checkmark/X cells use accessible color combinations (not just color — use icon + color)
- "Included but PatientPartner does it better" cells: use a custom icon (checkmark with a star or upward arrow) to mirror ClickUp's nuanced approach
- Row labels are sticky on scroll for wide tables on desktop

**FAQ Section**
- Accordion/expandable format
- All closed by default
- Schema markup for FAQ rich snippets (see SEO section)

**Mobile Behavior**
- Comparison tables: horizontal scroll with frozen first column (the dimension labels)
- Tab bars: horizontal scroll on mobile
- CTA: sticky floating CTA button on mobile once user scrolls past hero

### Visual Language

- **PatientPartner column:** Brand teal/primary color highlight
- **Competitor columns:** Neutral grey (#F5F5F5)
- **✓ checkmarks:** Brand green
- **✗ or "Not available":** Mid-grey (not red — we don't want to attack, just state facts)
- **Data stat callouts:** Large number (72px), short label, white on brand color card
- **Quote blocks:** Indented, italic, with attribution — used for competitive intelligence quotes
- **Section dividers:** Subtle background color alternation between sections

### Typography Hierarchy

- H1 (hero): Large display weight
- H2 (section titles): Bold, slightly smaller
- H3 (subsection): Medium weight
- Table headers: Small caps or medium weight
- Table cells: Body regular, 14–16px

---

## 10. SEO Requirements

### Target Keywords

**Hub Page (`/compare`)**
- `patient mentor platform comparison`
- `patient engagement platform vs`
- `Snow Companies alternative`
- `Reverba alternative`
- `pharmaceutical patient mentorship software`

**Individual Pages**
- `PatientPartner vs Snow Companies`
- `PatientPartner vs Reverba`
- `Snow Companies competitor`
- `Reverba alternative pharma`
- `patient ambassador program software`
- `replace internal patient ambassador program`

### On-Page SEO Requirements

| Element | Requirement |
|---------|-------------|
| **Title tag** | `PatientPartner vs [Competitor]: [Key Differentiator] \| PatientPartner` |
| **Meta description** | 150–160 chars. Includes target keyword, primary benefit, CTA signal |
| **H1** | Contains primary keyword naturally |
| **H2s** | Cover secondary keywords and question-form queries |
| **Alt text** | All comparison table screenshots and feature images have descriptive alt text |
| **Internal links** | Link to relevant case studies, capabilities pages, blog posts |
| **Schema markup** | FAQ schema on all FAQ sections; BreadcrumbList schema for compare section |
| **Canonical tags** | Self-referencing canonical on all comparison pages |
| **Load speed** | Core Web Vitals: LCP < 2.5s, CLS < 0.1, FID < 100ms |

### Content Depth Targets

- Hub page: 2,000–3,000 words
- Individual competitor pages: 1,500–2,500 words each

---

## 11. CTA Strategy

### CTA Hierarchy

| Priority | CTA | Placement | Audience Signal |
|----------|-----|-----------|-----------------|
| **Primary** | Book a Demo | Hero, mid-page, final section, sticky mobile button | Ready to evaluate |
| **Secondary** | Download Comparison Guide (PDF) | Mid-page, near comparison table | Researching, not ready to demo |
| **Tertiary** | Read the Case Study | Near proof section | Wants more evidence |

### Demo CTA Copy Variants (A/B test)

- `Book a Demo`
- `See PatientPartner Live`
- `Get a Personalized Comparison`
- `Talk to Our Team`

### Lead Magnet: Comparison Guide

A downloadable PDF that packages the full comparison matrix, outcome stats, and case study highlights. Gated with name + email + company + role.

**Contents:**
- One-page visual: PatientPartner vs. Snow vs. Reverba vs. Internal
- Outcome stats with methodology
- 2-page case study summary
- FAQ page (the top compliance and ROI questions)

**CTA on form:** `Download the 2026 Patient Mentorship Platform Comparison`

---

## 12. Technical Requirements

### Platform & Stack

- Built on same CMS/stack as the rest of patientpartner.com
- Reusable comparison table component (parameterized for different competitors — don't hardcode)
- FAQ accordion uses semantic HTML (`<details>/<summary>` or ARIA-compliant JS)
- Comparison table is accessible: `<table>` with proper `<th scope>` attributes, not div-based

### Performance

- Lazy-load comparison table images and screenshots
- No third-party scripts loaded before LCP element renders
- All images in WebP format with fallback

### Tracking

- GTM or equivalent — fire events on:
  - Competitor tab clicks (event: `comparison_tab_click`, label: competitor name)
  - FAQ accordion opens (event: `faq_open`, label: question text)
  - CTA clicks (event: `cta_click`, label: CTA text, location: section name)
  - Lead magnet form submission (event: `lead_magnet_submit`)
  - Demo form submission (event: `demo_request_submit`, source: `comparison_page`)
- UTM parameters preserved through demo request form submission
- HubSpot/CRM: tag all leads from comparison pages with `source = comparison_page` + `competitor = [tab clicked]`

---

## 13. Analytics & Success Metrics

### Primary KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Demo requests from comparison pages | ≥ 15% of unique visitors | GA4 + CRM |
| Lead magnet downloads | ≥ 25% of unique visitors | Form tracking |
| Organic sessions (comparison pages) | 500+ / month within 6 months | GA4 |
| Keyword ranking for target terms | Top 3 within 6 months | SEMrush / Ahrefs |
| Average time on page | ≥ 3 minutes | GA4 |
| Scroll depth | ≥ 70% of visitors reach FAQ section | GA4 / Hotjar |

### Secondary Metrics

- Competitor tab click distribution (tells us which competitors visitors are most interested in)
- FAQ question open rate by question (tells us top objections)
- Source/medium breakdown of comparison page traffic
- Demo-to-opportunity conversion rate for leads sourced from comparison pages
- Sales cycle length: comparison page sourced vs. non-comparison sourced

### Reporting Cadence

- Weekly: Demo requests from comparison pages, organic sessions
- Monthly: Keyword rankings, full funnel conversion report
- Quarterly: A/B test results, content refresh decisions

---

## 14. Content Governance

### Accuracy Standards

Competitor claims must meet one of these standards before publication:
1. **Cited from public sources** (company website, job postings, press releases, G2 reviews)
2. **Attributed to original research** (competitive analysis interviews — cite as "PatientPartner Competitive Analysis, 2024")
3. **Internally verifiable** (pricing ranges from actual competitive quotes on file)

**Do not publish:**
- Unattributed "insider" claims about competitor financials or business status
- Claims that a competitor "has no technology" (Reverba has reverbaBRIDGE — acknowledge it, differentiate it)
- Any specific pricing multiple (e.g., "10x cheaper") without documented client quotes

### Review Process

1. Content author drafts comparison page content
2. Legal/compliance review: 5 business days for review of competitor claims
3. Sales team review: ensure accuracy against current field intelligence
4. Final approval: CMO/VP Marketing
5. Post-launch: Review competitor pages every 6 months or when a significant competitor announcement is made

### Maintenance Triggers

Update a competitor page when:
- Competitor launches a new platform feature
- Competitor announces a major partnership or acquisition
- New data points emerge from PatientPartner case studies
- G2 scores change materially
- New proof quotes become available from clients

---

## 15. Launch Checklist

### Pre-Launch

- [ ] All competitor claims reviewed by legal
- [ ] Client logos approved for display (confirmed written permissions)
- [ ] Case study data reviewed for accuracy and attribution
- [ ] All pages indexed and accessible (no robots.txt blocks)
- [ ] Schema markup validated (Google Rich Results Test)
- [ ] Core Web Vitals passing on all pages
- [ ] All CTAs connected to correct HubSpot forms
- [ ] UTM parameters tested end-to-end
- [ ] Lead magnet PDF designed and file link live
- [ ] 301 redirects set if replacing any existing pages
- [ ] Internal linking updated (homepage, nav, relevant blog posts)
- [ ] Social sharing meta tags (OG image, title, description) on all pages

### Launch

- [ ] Announce to sales team with individual shareable URLs per competitor
- [ ] Add comparison pages to email signature link rotation (for SDRs)
- [ ] Create LinkedIn posts for each competitor page launch
- [ ] Submit pages to Google Search Console for indexing

### Post-Launch (Week 1–4)

- [ ] Monitor Core Web Vitals in Search Console
- [ ] Check for crawl errors
- [ ] Review initial CTR data in Search Console
- [ ] Gather sales team feedback on which pages are most useful
- [ ] Begin A/B test on CTA copy (week 2+)

---

## Appendix A: Competitor One-Line Wedges (Sales Reference)

| Competitor | The Wedge |
|-----------|-----------|
| Snow Companies | "Stories build belief. Mentorship changes behavior." |
| Reverba | "Instant peer connection, not just engagement programs." |
| Internal Programs | "Stop rebuilding the same program every launch. Productize it once, deploy it everywhere." |
| AI Platforms (Hippocratic, Ostro) | "The only AI built to convert on brand.com AND retain through ongoing mentorship." |

---

## Appendix B: Key Proof Points to Feature on Page

| Stat | Source | Context |
|------|--------|---------|
| 71% | Adherence improvement | From PatientPartner deployed programs — adherence vs. non-mentored cohort |
| 68% | Patients felt more confident | Self-reported, post-mentor conversation survey |
| 90% | Mentor satisfaction rate | Mentor retention/satisfaction across programs |
| 30% | Increase in new patient starts | Mentored vs. non-mentored patient cohort |
| 133.5 days | Faster treatment decision | Time to therapy start: mentored vs. benchmark |
| 99% | Mentor retention rate | Platform-wide mentor retention across all programs |
| ~$1M | Typical Snow/Reverba program cost | Competitive analysis intel — note as "typical range" not as an absolute |
| 1 in 10 | Competitor conversion rate | "Only one in ten interested patients completes a mentorship connection" with legacy agencies |

---

*End of PRD v1.0*
