# Webflow Implementation Guide — PatientPartner Comparison Pages

## Files Delivered

| File | URL Path | Purpose |
|------|----------|---------|
| `compare.html` | `/compare` | Hub page — overview of all competitors |
| `patientpartner-vs-snow-companies.html` | `/compare/snow-companies` | Head-to-head: PatientPartner vs. Snow |
| `patientpartner-vs-reverba.html` | `/compare/reverba` | Head-to-head: PatientPartner vs. Reverba |
| `patientpartner-vs-internal-programs.html` | `/compare/internal-programs` | Head-to-head: PatientPartner vs. Internal |

---

## Brand Design System (Verified from Live Site)

### Colors
| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#314D69` | Nav, footer, dark sections, hero backgrounds |
| Accent | `#72CBCF` | CTAs, highlights, stats, links, teal accents |
| Accent Hover | `#5FBCC0` | Button hover states |
| Text Primary | `#183857` | All headings, body text |
| Text Light | `#4A6B8A` | Paragraph text, descriptions |
| Text Muted | `#6B8CAD` | Labels, captions, table headers |
| Background | `#FFFFFF` | Default page background |
| Background Light | `#F7FAFA` | Alternating sections, cards |
| Background Section | `#F0F7F7` | Highlighted sections |
| Border | `#DCEAEA` | Card borders, table borders, dividers |
| Border Light | `#E8F3F3` | Subtle separators, table row borders |

### Typography
| Element | Font | Weight | Size |
|---------|------|--------|------|
| H1 | Manrope | 700 | `clamp(36px, 5vw, 54px)` |
| H2 | Manrope | 700 | `clamp(26px, 3.5vw, 38px)` |
| H3 | Manrope | 700 | `clamp(20px, 2.5vw, 26px)` |
| H4 | Manrope | 700 | 20px |
| Body | Manrope | 400 | 18px, line-height 1.65 |
| Button | Manrope | 600 | 16px |
| Small/Label | Manrope | 600–700 | 13–14px |

### Spacing & Radii
- Border radius: `12px` (standard), `16px` (cards/tables)
- Section padding: `clamp(60px, 8vw, 100px)` vertical
- Container max-width: `1200px`
- Button padding: `14px 28px`

---

## Webflow Build Instructions

### Option A: Custom Code Pages (Fastest)

1. In Webflow, create 4 new pages:
   - `/compare`
   - `/compare/snow-companies`
   - `/compare/reverba`
   - `/compare/internal-programs`

2. For each page, use a full-page **Embed** element and paste the complete HTML contents.

3. In Page Settings > Custom Code (Before `</head>`), add:
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
   ```

4. Remove the `<header>` and `<footer>` sections from each HTML file — use Webflow's global nav/footer symbols instead.

### Option B: Native Webflow Build (Recommended for Maintenance)

Build each section as a Webflow component using the HTML as a pixel-perfect reference:

#### Hub Page (`/compare`) — Section Map

| Section | Webflow Structure |
|---------|-------------------|
| **Hero** | Section (dark bg gradient), Container, Div (centered), Label span, H1, Paragraph, Link Block x2 |
| **Competitor Selector** | Sticky Section, Container, Flex Div with buttons/links |
| **Trust Bar** | Section, Container, Flex Div with badge Divs (icon + text) |
| **Problem Framing** | Section, Container, 2-col Grid (text + stat cards) |
| **Comparison Table** | Section (alt bg), Container, Rich Text or HTML Embed for table |
| **Deep-Dive Tabs** | Section, Container, Tab component (Webflow Tabs element) |
| **Features Grid** | Section (alt bg), Container, 3-col Grid of cards |
| **Testimonials** | Section, Container, 3-col Grid of testimonial cards |
| **FAQ** | Section (alt bg), Container, Accordion (Webflow Interactions) |
| **Final CTA** | Section (dark bg), Container, centered text + buttons |

#### Webflow Classes to Create

```
.pp-hero                  → Background: linear-gradient(170deg, #314D69, #1E3A54)
.pp-hero__label           → Pill: #72CBCF bg at 12% opacity, border, uppercase
.pp-btn--primary          → Background: #72CBCF, color: white, 12px radius
.pp-btn--secondary        → Background: #FBFFFF, border: 1px #DCEAEA, 12px radius
.pp-trust-badge           → Flex, bg: #F7FAFA, border: 1px #DCEAEA, 8px radius
.pp-stat-card             → Border: 1px #DCEAEA, 16px radius, centered
.pp-stat-card__number     → 48px, 800 weight, color: #72CBCF
.pp-compare-table         → Use HTML Embed — complex table layout
.pp-tab-btn               → 15px, 600 weight, 3px bottom border on active
.pp-feature-card          → Border: 1px #DCEAEA, 16px radius, 28px padding
.pp-testimonial-card      → Border: 1px #DCEAEA, 16px radius, 32px padding
.pp-faq-item              → Border: 1px #DCEAEA, 12px radius, accordion
.pp-section--alt           → Background: #F7FAFA
.pp-section--dark          → Background: gradient matching hero
```

### Interactions (Webflow IX2)

1. **FAQ Accordion**: Use Webflow's built-in Dropdown or build with Interactions:
   - Trigger: Click on question
   - Action: Toggle height of answer div (0 → auto), rotate plus icon 45°

2. **Tab Switching**: Use Webflow's native Tabs element, styled to match

3. **Sticky Competitor Selector**: Set position: sticky, top: 0, z-index: 100

4. **Scroll Animations** (optional): Fade-up on stat cards, feature cards, testimonial cards

---

## SEO Configuration

### Hub Page (`/compare`)
- **Title**: Compare Patient Engagement Platforms | PatientPartner
- **Meta Description**: See how PatientPartner compares to Snow Companies, Reverba, and internal programs. Real-time peer-to-peer mentorship vs. legacy agency models — side by side.
- **H1**: See Why Pharma Teams Choose PatientPartner

### Snow Page (`/compare/snow-companies`)
- **Title**: PatientPartner vs. Snow Companies | Compare Patient Engagement
- **Meta Description**: Compare PatientPartner to Snow Companies. Real-time SaaS platform vs. legacy agency model. See differences in speed, compliance, scalability, and ROI.
- **Target Keywords**: PatientPartner vs Snow Companies, Snow Companies alternative, patient ambassador platform

### Reverba Page (`/compare/reverba`)
- **Title**: PatientPartner vs. Reverba | Compare Patient Engagement Platforms
- **Meta Description**: Compare PatientPartner to Reverba. Instant peer connection vs. coordinator-managed engagement. See the data on connection rates, compliance, and outcomes.
- **Target Keywords**: PatientPartner vs Reverba, Reverba alternative, patient mentorship platform

### Internal Programs Page (`/compare/internal-programs`)
- **Title**: PatientPartner vs. Internal Ambassador Programs | PatientPartner
- **Meta Description**: Why enterprise pharma teams productize their internal ambassador programs with PatientPartner. Deploy once, scale everywhere, prove ROI in real time.
- **Target Keywords**: patient ambassador program software, patient mentorship platform enterprise

### Schema Markup (add to each page's custom code)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "Compare Patient Engagement Platforms",
  "description": "Side-by-side comparison of patient engagement platforms for enterprise pharma and med-tech",
  "publisher": {
    "@type": "Organization",
    "name": "PatientPartner",
    "url": "https://www.patientpartner.com"
  }
}
</script>
```

---

## Internal Linking Strategy

From these pages, link to:
- `/pharma-engagement-software` — For Pharma vertical page
- `/med-device-engagement-software` — For Med-Tech vertical page
- `/clinical-trial-engagement-software` — For Clinical Trials vertical page
- `/faq` — Full FAQ page
- `/2026-patient-support-benchmark-report` — Lead magnet

From other pages, link to:
- Add "See How We Compare" CTA in the nav or on vertical pages
- Link from blog posts about patient engagement, competitor mentions
- Link from FAQ answers that reference competitive questions

---

## CTA Configuration

All "Book a Demo" buttons should trigger the same demo form modal already on the site.
"Download the Comparison Guide" should link to a gated PDF (to be created) or the benchmark report.
"Back to Full Comparison" links should point to `/compare`.

---

## QA Checklist

- [ ] All 4 pages live at correct URLs
- [ ] Global nav/footer consistent with rest of site
- [ ] Manrope font loading correctly
- [ ] Colors match brand system exactly
- [ ] Comparison tables scroll horizontally on mobile
- [ ] FAQ accordions open/close correctly
- [ ] Tab switching works on hub page
- [ ] All CTAs trigger demo form or link correctly
- [ ] Meta titles and descriptions set
- [ ] Schema markup added
- [ ] Internal links working
- [ ] Mobile responsive at 375px, 768px, 1024px, 1440px
- [ ] Page speed under 3 seconds on mobile
- [ ] Sticky competitor selector works on scroll
