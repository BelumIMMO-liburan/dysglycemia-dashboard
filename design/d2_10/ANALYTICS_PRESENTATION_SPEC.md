# Research Analytics Presentation Specification

**Phase:** D2.10 — Research Analytics + Human–AI Decision Flow  
**Target View:** `/analytics/` (`dashboard/predictor/templates/predictor/analytics.html`)  
**Design System:** shadcn/ui Inspired Design Tokens (`predictor/css/design_system.css`)

---

## 1. Information Architecture & Page Layout
The `/analytics/` workspace is organized into six functional zones:

```
[ 1. Page Header & Active Date Filter Scope ]
[ 2. Research Governance & Verification Bias Alert ]
[ 3. Date Range Filter Controls (Intake Date From / To) ]
[ 4. Top 5 Headline Summary Cards (with explicit denominators) ]
[ 5. Two-Stage Workflow Funnel (Branched Cascade) ]
[ 6. 2-Column Analytical Deck ]:
     ├── Human–AI Decision Transition Matrix (2×2 Semantic Table)
     └── Override Patterns & Structured Rationale Bars
[ 7. Observed Stage-2 Laboratory Range Distribution Deck ]
[ 8. Methodology Specification & Metric Denominator Reference Table ]
```

---

## 2. Top 5 Summary Cards Rule
To prevent "SaaS metric overload" and maintain clinical focus, top-level KPI cards are strictly capped at **five cards**. Every card displaying a percentage must expose its exact numerator and denominator in immediately adjacent subtitle text:

1. **Total Screenings:** Displays absolute integer $N_{\text{screenings}}$. Helper: `Intake population (N = X)`.
2. **AI Referral Rate:** Displays `X.X%` (or `"Not available"`). Helper: `A of B screenings`.
3. **Human–AI Agreement:** Displays `X.X%` (or `"Not available"`). Helper: `A of B reviewed screenings`.
4. **Human Override Rate:** Displays `X.X%` (or `"Not available"`). Helper: `A of B reviewed screenings`.
5. **Stage-2 Completion:** Displays `X.X%` (or `"Not available"`). Helper: `A of B eligible referrals`.

---

## 3. Neutral Moral Palette (No Green "Good" / Red "Bad")
In decision-support ergonomics:
- Agreement is **not** inherently "good" (blind agreement could indicate automation bias).
- Override is **not** inherently "bad" (clinician override is an intended safety barrier).
- Referral rate is **not** a score of clinical effectiveness.

### Palette Implementation:
- **Zero Saturated Red/Green Success Coding:** Summary cards and transition matrix cells use neutral border, background, and foreground tokens (`hsl(var(--foreground))`, `hsl(var(--muted))`).
- **Semantic Badges:** Concordant and override cells use neutral badges with clear text labels (`"Agreement"`, `"Override"`).
- **Proportional Bars:** Distribution bars use neutral primary brand tokens (`hsl(var(--primary))`) with calibrated opacity tiers (e.g., 50%, 75%, 100%) rather than moralized traffic-light colors.

---

## 4. Semantic Tables & Accessibility
- **Decision Transition Matrix:** Rendered as an HTML `<table>` with `<caption class="sr-only">`, `<th scope="col">` for column headers, `<th scope="row">` for row headers, and summary `<tfoot>`.
- **Screen Reader Parity:** All visual bar distributions have equivalent text tables, exact counts, percentages, and `aria-label` text describing the full distribution.
- **Empty State Behavior:** When counts are zero, cards display `"Not available"` or `" — "` instead of `"0%"`. Dedicated empty state callouts provide actionable explanatory copy.
