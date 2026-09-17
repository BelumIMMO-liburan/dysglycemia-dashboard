# D3 Security, Integrity & Privacy Audit

**Audit Date:** 2026-09-05  
**Prototype Scope:** Academic Research Decision-Support Prototype (Pre-Study Evaluation)  
**Security Status:** VERIFIED SECURE & AUDITABLE

---

## 1. Request Method Verification

Every user-facing route enforces appropriate HTTP verb boundaries:

| Route | Allowed Methods | Non-Permitted Handling | Verification |
| :--- | :--- | :--- | :--- |
| `overview_view` | GET | Read-only | **PASSED** |
| `new_screening_view` | GET | Read-only | **PASSED** |
| `run_screening_view` | POST | GET redirects to `new_screening` | **PASSED** |
| `screening_result_view` | GET | Read-only (Zero mutations) | **PASSED** |
| `accept_review_view` | POST | GET redirects to `screening_result` | **PASSED** |
| `override_review_view` | POST | GET redirects to `screening_result` | **PASSED** |
| `stage2_view` | GET | Read-only | **PASSED** |
| `stage2_confirm_view` | POST | GET redirects to `stage2` | **PASSED** |
| `review_queue_view` | GET | Read-only | **PASSED** |
| `history_view` | GET | Read-only | **PASSED** |
| `analytics_view` | GET | Read-only (Filters via query params) | **PASSED** |
| `about_model_view` | GET | Read-only | **PASSED** |

Zero state mutations or database writes occur via GET requests.

---

## 2. CSRF & Form Protection

1. **CSRF Tokens:** All state-changing HTML forms (`run-screening-form`, `accept-review-form`, `override-review-form`, `stage2-confirm-form`) embed standard Django `{% csrf_token %}` tags.
2. **CSRF Middleware:** `django.middleware.csrf.CsrfViewMiddleware` remains active in `MIDDLEWARE`. Zero forms or views bypass CSRF via `@csrf_exempt`.

---

## 3. Client Authority & Tampering Defenses

The prototype rejects all attempts by client browsers to authoritatively dictate screening or review state:

- **AI Recommendation & Probability:** Computed exclusively server-side in `screening_inference.py`. Client payloads cannot supply or override probabilities or recommendations.
- **Decision Threshold:** Hardcoded constant `0.1389` on the server. Zero client sliders or config overrides accepted.
- **Human Review Semantics:** On Acceptance, `final_referral_recommended` is copied directly from `screening_record.ai_referral_recommended` server-side. On Override, it is inverted server-side.
- **Stage-2 Laboratory Range:** Categorized strictly server-side using Decimal comparison in `classify_hba1c_range`. Client-injected `laboratory_range` values are ignored.

---

## 4. Privacy & Participant Data Safeguards

1. **Zero PII Collection:** Database models (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`) do not store:
   - Patient names
   - Phone numbers or emails
   - Dates of birth (only integer age 18–85)
   - Residential addresses
   - Medical record numbers or National ID numbers
2. **Pseudonymous Identifiers:**
   - Case tracking utilizes random UUIDv4 (`ScreeningRecord.id`), preventing enumeration attacks.
   - Reviewer identity utilizes anonymous alphanumeric codes (`reviewer_code`, max 32 chars).
   - Form guidance explicitly warns: *"Use the reviewer code assigned for this study. Do not enter your name or other identifying information."*
3. **Safe Output Escaping:** Free-text fields (`override_note`, `reviewer_code`) are rendered through standard Django auto-escaping without `safe` filters.
4. **Log Sanitization:** Server logging in views outputs record UUIDs and exception summaries only. Full `request.POST` payloads, raw notes, and patient parameters are never dumped into application logs.
