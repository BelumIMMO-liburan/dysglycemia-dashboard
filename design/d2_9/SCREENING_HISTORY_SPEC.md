# Screening History & Case Ledger Specification (Phase D2.9)

## 1. Executive Purpose
The Screening History (`/history/`) serves as the permanent, auditable case ledger answering:
> **"What happened for this screening case across its entire lifecycle?"**

History provides an immutable, transparent record of every participant screening event, model inference output, human review disposition, and Stage-2 laboratory assessment.

---

## 2. Ledger Architecture: Exactly 1 Row per ScreeningRecord
Every row in the history table represents exactly one `ScreeningRecord`.
- Related entities (`ScreeningExplanation`, `HumanReview`, `Stage2Assessment`) are aggregated into the single case row through relational joins (`select_related`).
- Multiple rows are NEVER spawned for explanations, review steps, or laboratory entries.
- The case detail view (`/screening/<uuid>/result/`) exposes the full multi-part audit story.

---

## 3. Table Column Specification

| Column Header | Data Source | Formatting / Semantics |
| :--- | :--- | :--- |
| **Screening ID** | `record.id` | Shortened UUID prefix (`#<id[:8]>...`), full UUID in title. Links to case result. |
| **Created** | `record.created_at` | Timestamp in `YYYY-MM-DD HH:mm` format. |
| **Screening Signal** | `record.ai_referral_recommended` | `Elevated` (amber tint) or `Lower` (slate tint). Multi-modal (text + icon + tint). |
| **AI Recommendation** | `record.ai_referral_recommended` | `Refer` or `Do not refer`. Immutable baseline output. |
| **Review Action** | `human_review.review_action` | `Accepted` (emerald), `Overridden` (amber with structured reason in title), or `Pending` (secondary). |
| **Final Human Decision** | `human_review.final_referral_recommended` | `Refer` (emerald) or `Do not refer` (secondary) or `—` if review pending. |
| **Stage-2 Status** | Derived from lifecycle | `Not applicable` (slate), `Pending` (primary), `Completed` (emerald), or `—`. |
| **HbA1c Laboratory Range** | `stage2_assessment.laboratory_range` | `Normal-range`, `Prediabetes-range`, or `Diabetes-range`. Only displayed when completed; `—` otherwise. |
| **Workflow Status** | `lifecycle.label` | Multi-modal status badge reflecting derived lifecycle state. |
| **Action** | Route helper | `[ View Case ]` button linking to `/screening/<uuid>/result/`. |

### Mandatory Governance Rule: AI vs Human Decision Separation
The history ledger strictly maintains separate columns for **AI Recommendation** and **Final Human Decision**. The interface never collapses these into a single ambiguous "Decision" column. This visual distinction directly supports the research core: demonstrating the epistemic authority of human review.

---

## 4. Non-PII Filter Suite
The history interface provides server-side filtering via standard query parameters without client-side lag or PII collection:

1. `status`: Filter by derived workflow state (`pending_review`, `pending_stage2`, `reviewed_no_referral`, `completed_stage2`, `explanation_unavailable`).
2. `ai_rec`: Filter by machine recommendation (`refer`, `no_refer`).
3. `review_action`: Filter by reviewer action (`pending`, `accepted`, `overridden`).
4. `final_decision`: Filter by authoritative human decision (`refer`, `no_refer`, `pending`).
5. `stage2_status`: Filter by Stage-2 state (`not_applicable`, `pending`, `completed`).
6. `hba1c_range`: Filter by completed laboratory range (`normal_range`, `prediabetes_range`, `diabetes_range`).
7. `order`: Sort by intake evaluation timestamp (`newest` vs `oldest`).

---

## 5. Screening UUID Search
Search is strictly scoped to **Screening UUID** (full 36-character UUID or 8+ character prefix).
- Name, contact, or personal identifier search is prohibited because the screening intake schema collects zero participant PII.

---

## 6. Server-Side Pagination
- Default density: 25 rows per page.
- URL query parameters (filters, search, sort) are preserved across pagination links.
- Uses Django's `Paginator` with zero full-dataset memory dumps into the browser DOM.

---

## 7. Read-Only Invariant & Zero ML Execution
- GET requests perform **0 GAM inferences**, **0 preprocessing calls**, **0 XAI generation calls**, and **0 database writes**.
- Reads persisted values only.
