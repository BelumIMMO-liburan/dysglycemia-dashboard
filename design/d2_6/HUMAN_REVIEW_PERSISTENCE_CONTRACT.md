# Human Review Persistence Contract: Data Architecture & Audit Trail Specification

**Document Version:** 1.0  
**Phase:** D2.6  
**Status:** Frozen & Approved  
**Governing Skill:** `research-governance`  

---

## 1. Purpose & Architectural Principles

This document formalizes the persistence contract for the **Human Review Foundation & Accept Recommendation Workflow** in the Stage-1 Dysglycemia Screening System.

### Core Architectural Mandate
> **"Human Review must exist as a distinct, relational entity referencing the immutable Screening Record. The original AI screening output is never overwritten or mutated."**

In clinical decision-support systems and medical research governance:
1. The AI model output (`ScreeningRecord`) represents historical computational truth—what the frozen GAM inferred from the non-laboratory inputs at the time of intake.
2. The Human Review (`HumanReview`) represents professional oversight—an explicit action taken by an authorized clinician or researcher.
3. Decoupling AI inference from human governance ensures full auditability, regulatory compliance, and retrospective agreement-rate analysis without compromising data provenance.

---

## 2. Schema Specification: `HumanReview`

**Database Table:** `predictor_humanreview`  
**Django Model:** `predictor.models.HumanReview`  

| Column Name | Django Field Type | Null / Blank | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUIDField` | `False / False` | `primary_key=True`, default=`uuid.uuid4`, `editable=False` | Cryptographically random, non-sequential unique identifier. |
| `screening_record` | `OneToOneField(ScreeningRecord)` | `False / False` | `on_delete=models.PROTECT`, `related_name='human_review'` | Strict 1-to-1 linkage to the evaluated screening record. Prevents deletion of screening records with review records. |
| `reviewer_code` | `CharField(max_length=32)` | `False / False` | Validated by regex `^[a-zA-Z0-9_-]+$` | Anonymous, non-PII reviewer/investigator identifier (e.g., `CLINICIAN-01`, `REV_42`). |
| `review_action` | `CharField(max_length=20)` | `False / False` | Locked to `'accepted'` in Phase D2.6 | Action taken by reviewer. Human Override (`'overridden'`) is deferred to Phase D2.7. |
| `final_referral_recommended` | `BooleanField` | `False / False` | Server-derived from `screening_record.ai_referral_recommended` | Final referral decision after review. Derived strictly on server; client payload cannot override this in D2.6. |
| `created_at` | `DateTimeField` | `False / False` | `auto_now_add=True`, UTC timestamp | Immutable timestamp marking when review was submitted and accepted. |

---

## 3. Strict Immutability Guarantees

1. **Zero Mutation of `ScreeningRecord`:**
   - Under no circumstances does a human review modify any attribute of `ScreeningRecord` (`screening_probability`, `ai_referral_recommended`, `model_sha256`, etc.).
   - Database level: Updates to `ScreeningRecord` remain prohibited by system policy.
2. **Single-Review Invariant (`OneToOneField`):**
   - Each `ScreeningRecord` may have at most **one** `HumanReview`.
   - Repeated POST requests targeting an already-reviewed screening record are rejected at both the database constraint level (`UNIQUE` index on `screening_record_id`) and application layer (idempotent redirect or HTTP 400).
   - Existing review timestamps (`created_at`) and decisions are preserved unconditionally.
3. **No Deletion Cascades (`on_delete=PROTECT`):**
   - Attempting to delete a `ScreeningRecord` that has an associated `HumanReview` raises a database/Django `ProtectedError`.

---

## 4. Server-Side Derivation & Anti-Tampering Defense

To defend against client-side payload tampering and unauthorized parameter injection:
- The POST endpoint `/screening/<uuid>/review/accept/` **never reads the final decision from the client request body**.
- The server logic retrieves the target `ScreeningRecord` by `screening_id` and derives:
  $$\text{final\_referral\_recommended} \leftarrow \text{screening\_record.ai\_referral\_recommended}$$
- Even if a malicious client injects form fields such as `final_referral_recommended=false` or `override=true`, the server completely ignores client decision flags and strictly persists the AI recommendation concordance.

---

## 5. Reviewer Code Specification & Data Minimization

To uphold clinical research privacy and eliminate Personally Identifiable Information (PII):
- **Anonymous Reviewer Code:** Clinicians and researchers identify themselves using pseudonymized codes or institutional station IDs (e.g., `DOC-808`, `INV_04`).
- **Format Validation:**
  - Pattern: `^[a-zA-Z0-9_-]+$`
  - Minimum length: 1 character
  - Maximum length: 32 characters
  - Strictly disallows: Spaces, commas, HTML tags, script tags, special punctuation, or free-text narrative.
- **Strictly Prohibited Fields in D2.6:**
  - Clinician legal names, doctor names, staff emails, employee badge numbers.
  - HbA1c values, laboratory intake fields, blood draws, clinical diagnoses, diabetes classification tags.
  - Clinical override categories, override rationales, free-form text notes (deferred to D2.7).

---

## 6. Prerequisite Gate: Explanation Availability

In accordance with the **Evidence-First Guided Review** philosophy:
- A human review may only be performed if the GAM-native additive explanation has been successfully computed and persisted (`ScreeningExplanation.status == 'generated'`).
- If an explanation is missing or in a `'failed'` state:
  - The review interface is disabled and replaced by `#review-unavailable-card`.
  - Direct POST requests to `/screening/<uuid>/review/accept/` are rejected with HTTP 400 (`"Human review cannot be recorded because the model explanation is unavailable."`).
  - No blind reviews without local interpretability evidence are permitted.

---

## 7. Audit & Legacy Entity Classification

The codebase contains a legacy model `Override` in `dashboard/predictor/models.py`.
- **Classification:** **Class C: LEGACY — DO NOT USE / ARCHIVE LATER**.
- **Rationale:** The legacy `Override` model links to legacy `Prediction` (not `ScreeningRecord`), stores clinician names (`doctor_name` PII), stores binary disease class overrides (`override_value` 0 or 1 flipping), and lacks 1-to-1 unique integrity.
- **Isolation:** `HumanReview` is completely isolated from `Override`. The legacy model remains untouched to avoid breaking legacy migrations, but is not used in Phase D2.6 or subsequent screening pipelines.
