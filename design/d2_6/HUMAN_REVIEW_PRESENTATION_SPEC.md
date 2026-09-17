# Human Review Presentation Specification: UI/UX & Interaction Design

**Document Version:** 1.0  
**Phase:** D2.6  
**Status:** Approved  
**Governing Skills:** `dashboard-design`, `frontend-quality`, `research-governance`  

---

## 1. Information Architecture & Layout Placement

In the Screening Result experience, information hierarchy follows the **Evidence-First Guided Review** philosophy:
1. **Primary AI Output:** The Stage-1 Non-Laboratory Screening Result card (`#screening-result-card`), displaying the risk tier badge, percentage probability meter, locked threshold (`13.89%`), and AI recommendation.
2. **Local Interpretability Evidence:** The GAM-Native "Why this result?" card (`#explanation-card`), decomposing the net log-odds prediction into exact additive term contributions.
3. **Human Review Governance (Phase D2.6):** The Human Review Card (`#human-review-card`), positioned immediately below the explanation evidence and directly above the collapsible raw screening inputs.
4. **Collapsible Inputs & Auditing:** The verified baseline participant inputs and technical research provenance details.

Placing Human Review *after* the local explanation ensures that the reviewing clinician or researcher inspects both the global prediction and the individual risk factor contributions before recording a governance decision.

---

## 2. Visual States Specification

The Human Review interface implements three mutually exclusive states:

### State A: Reviewed / Finalized State
Rendered when a valid `HumanReview` record exists for the current `ScreeningRecord`.

- **Container:** `<div id="human-review-card" class="bg-card border border-border rounded-xl p-6 shadow-sm">`
- **Header:**
  - Section Title: `"Human Review"` (`text-lg font-semibold tracking-tight text-foreground`)
  - Status Badge: `<span id="review-status-badge" class="badge-reviewed bg-green-100 text-green-800 border-green-200">Reviewed</span>`
- **Decision Display Grid:**
  - **Original AI Recommendation:** Displays the original AI output (`"Refer for Stage-2 HbA1c"` or `"No Referral Recommended"`) with muted styling.
  - **Final Referral Decision:** `<span id="final-decision-badge">`
    - If `final_referral_recommended == True`: Amber badge (`bg-amber-100 text-amber-800 border-amber-200`) labeled `"Refer for Stage-2 HbA1c (Accepted)"`.
    - If `final_referral_recommended == False`: Slate/blue badge (`bg-blue-100 text-blue-800 border-blue-200`) labeled `"No Referral Recommended (Accepted)"`.
  - **Reviewer Identifier:** `<span id="reviewer-code-display" class="font-mono text-sm font-medium">` displaying the anonymous reviewer code (e.g., `DOC-808`).
  - **Review Timestamp:** `<span id="review-timestamp-display" class="text-xs text-muted-foreground">` formatted as `YYYY-MM-DD HH:MM:SS UTC`.
- **Audit Immutability Notice:**
  - Container: `<div id="review-immutable-notice" class="bg-muted/50 border border-border/50 rounded-lg p-3 text-xs text-muted-foreground flex items-center gap-2">`
  - Copy: `"This screening has been reviewed and finalized. Decisions are permanently locked to ensure an immutable audit trail."`
- **Form State:** Form and action buttons are completely omitted from the DOM.

---

### State B: Review Unavailable (Explanation Prerequisite Failure)
Rendered when the screening record has no human review, but `ScreeningExplanation.status != 'generated'` or no explanation entity exists.

- **Container:** `<div id="review-unavailable-card" class="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/40 rounded-xl p-6">`
- **Alert Icon & Title:** Alert triangle icon with `"Human Review Unavailable"` in bold amber-900 / amber-200 text.
- **Explanatory Copy:**
  - `"Human review cannot be recorded because the model explanation for this screening could not be generated. To maintain clinical auditability, human reviews require complete local factor decomposition."`
- **Form State:** Form submission is disabled; no input fields or action buttons are rendered.

---

### State C: Pending Review (Interactive Acceptance Workflow)
Rendered when no `HumanReview` exists and the explanation is available and faithful (`explanation.status == 'generated'`).

- **Container:** `<div id="human-review-card" class="bg-card border border-border rounded-xl p-6 shadow-sm">`
- **Header:**
  - Section Title: `"Human Review"`
  - Pending Badge: `<span id="review-pending-badge" class="badge-pending bg-amber-100 text-amber-800 border-amber-200">Pending Review</span>`
- **Guidance Banner:**
  - Explains the purpose of the review: `"Verify the screening inputs and model explanation above before accepting the AI recommendation for Stage-2 protocol referral."`
- **Recommendation Summary Card:**
  - Displays the proposed AI recommendation with visual parity to the primary result card:
    - Elevated signal: `"AI Recommendation: Refer for Stage-2 Diagnostic HbA1c"` (amber alert theme).
    - Lower signal: `"AI Recommendation: No Referral Recommended at this operating point"` (blue/neutral alert theme).
- **Form Controls (`#review-action-form`):**
  - **CSRF Token:** Included via standard Django `{% csrf_token %}`.
  - **Reviewer Code Field (`#id_reviewer_code`):**
    - Label: `<label for="id_reviewer_code" class="text-sm font-medium text-foreground">Reviewer Code / ID</label>`
    - Helper Text (`#reviewer-code-help`): `"Enter your anonymous reviewer or clinician ID (alphanumeric, e.g. DOC-808). Do not enter patient names or personal information."`
    - Input element: `<input type="text" name="reviewer_code" id="id_reviewer_code" required maxlength="32" class="input-text font-mono" placeholder="e.g. DOC-808" autocomplete="off" aria-describedby="reviewer-code-help">`
    - Validation error block (`#reviewer-code-error`): Rendered conditionally with `aria-live="polite"`.
  - **Action Button (`#accept-recommendation-btn`):**
    - Style: High-contrast primary action button (`bg-primary text-primary-foreground hover:bg-primary/90 min-h-[44px] px-6 py-2.5 rounded-lg font-medium shadow-sm transition-colors`).
    - Copy: `"Accept AI Recommendation"`
  - **Governance Warning:**
    - Small muted notice: `"Acceptance permanently commits this review decision to the research audit trail. This action cannot be undone."`

---

## 3. Design Tokens & Styling Details

The Human Review components strictly adhere to the project's design token palette and shadcn/ui visual standards:

| UI Element | CSS / Tailwind Tokens |
| :--- | :--- |
| **Card Surface** | `bg-card text-card-foreground border border-border rounded-xl shadow-sm` |
| **Primary Typography** | Font family: Inter, system-ui; Title: `text-lg font-semibold tracking-tight` |
| **Monospace Identifiers** | Font family: `font-mono text-sm` (`ui-monospace, SFMono-Regular, Menlo`) |
| **Reviewed Badge** | `bg-green-500/10 text-green-700 dark:text-green-400 border border-green-500/20 px-2.5 py-0.5 rounded-full text-xs font-semibold` |
| **Pending Badge** | `bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20 px-2.5 py-0.5 rounded-full text-xs font-semibold` |
| **Input Focus State** | `focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-input` |
| **Accept Button** | `bg-primary text-primary-foreground hover:bg-primary/90 min-h-[44px] rounded-lg font-medium` |

---

## 4. Prohibited UI Patterns

In accordance with Phase D2.6 scope boundaries:
1. **No Override Controls:** No "Override", "Reject", "Change Decision", or alternate choice radio buttons are displayed (strictly Phase D2.7).
2. **No Free-Text Clinical Notes:** No clinical justification textareas or note boxes are provided.
3. **No HbA1c Data Entry:** No Stage-2 HbA1c input or laboratory result fields are rendered (Phase D2.8).
4. **No Re-infer Buttons:** No actions that recompute or alter the locked GAM inference output.
