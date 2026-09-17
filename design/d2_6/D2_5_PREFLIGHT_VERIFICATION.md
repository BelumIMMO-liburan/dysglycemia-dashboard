# Phase D2.6 — Preflight Verification of Phase D2.5 Findings
**Date:** September 2026  
**Auditor:** Antigravity Pairing Agent  
**Status:** VERIFIED & RESOLVED  
**Governing Skill:** `research-governance`

---

## 1. Preflight Check A: Explanation Failure Semantics

### Invariant Under Verification
A valid `ScreeningRecord` must survive if explanation generation fails.

```
successful frozen GAM inference
        ↓
ScreeningRecord persists
        ↓
explanation generation attempted
        ↓
if success:
    ScreeningExplanation generated
if failure:
    ScreeningRecord remains valid
    explanation-unavailable state remains visible
```

### Forbidden Pattern
Any transaction architecture where an XAI calculation or persistence failure rolls back or deletes an otherwise valid `ScreeningRecord`.

### Code Audit & Architectural Refinement
- **Prior Implementation (D2.5):** In `run_screening_view`, `record = ScreeningRecord.objects.create(...)` and `ScreeningExplanation.objects.create(...)` were nested within the same outer `with transaction.atomic():` block. Although an inner `try...except` caught explanation errors to persist `status='failed'`, any unhandled exception in explanation persistence could theoretically cause the outer transaction to roll back `ScreeningRecord`.
- **Preflight Correction (D2.6):** The database persistence of `ScreeningRecord` is explicitly completed in its own `with transaction.atomic():` block before explanation generation is attempted.
- **Resilience Guarantee:**
  - `ScreeningRecord` is committed to disk first.
  - Explanation generation and persistence are executed in a secondary resilient block.
  - If explanation generation fails, a failed `ScreeningExplanation` record is created.
  - If saving the failed explanation fails, `ScreeningRecord` remains intact and unaffected.
  - Zero deletion or rollback of `ScreeningRecord` can occur due to downstream explanation failures.

---

## 2. Preflight Check B: Spline Terminology Audit

### Invariant Under Verification
The frozen GAM specification is:
$$n\_splines = 10, \quad \lambda = 10.0$$

Do not describe this as "10 knots" unless the fitted pyGAM object and methodology explicitly establish that terminology. The preferred terminology is:
`"10-spline basis / n_splines=10"`

### Code & Documentation Audit
- A codebase search for `"10 knots"` identified 4 instances in `design/d2_5/D2_5_IMPLEMENTATION_REPORT.md` (lines 59, 61, 64, 65).
- In B-splines, a basis of $n\_splines=10$ uses a set of internal and boundary knots whose total count depends on spline degree (for cubic splines, $n\_knots = n\_splines + \text{order}$). Describing the model as having "10 knots" was technically imprecise.
- All 4 instances in `D2_5_IMPLEMENTATION_REPORT.md` were corrected to:
  `Spline (10-spline basis / n_splines=10)`
- No model re-fitting was performed; the frozen model artifact `gam_final.pkl` remains bitwise identical.

---

## 3. Preflight Gate Sign-Off

Both preflight checks are verified and closed. The codebase is cleared for implementing the `HumanReview` entity and Accept Recommendation workflow.
