# Phase D2.9 Preflight Documentation Corrections

**Status:** Completed & Reconciled  
**Date:** 2026-09-05  
**Scope:** Reconciling terminology, lifecycle state count, and query complexity wording prior to Phase D2.10 analytics implementation.

---

## 1. Issue A — Lifecycle State Count Reconciliation

### Audit Finding
Certain narrative summaries and test descriptions in Phase D2.9 documentation referenced "7 lifecycle states".

### Authoritative Code & Contract Inspection
Inspection of `dashboard/predictor/services/screening_lifecycle.py` and `design/d2_9/SCREENING_LIFECYCLE_CONTRACT.md` confirms that the lifecycle derivation engine defines and implements exactly **6 active lifecycle states**:

```python
ALL_LIFECYCLE_STATES = [
    STATE_EXPLANATION_UNAVAILABLE,  # 1. "explanation_unavailable" (Needs System Attention)
    STATE_PENDING_REVIEW,           # 2. "pending_review" (Pending Human Review)
    STATE_REVIEWED_NO_REFERRAL,     # 3. "reviewed_no_referral" (Reviewed — No Stage 2)
    STATE_PENDING_STAGE2,           # 4. "pending_stage2" (Pending Stage 2)
    STATE_COMPLETED_STAGE2,         # 5. "completed_stage2" (Completed Two-Stage)
    STATE_INTEGRITY_ERROR,          # 6. "integrity_error" (Data Integrity Issue)
]
```

There is no seventh active lifecycle state. The prior mention of "7 states" arose from conflating the 7 test fixture permutations (such as distinct acceptance vs override referral paths that both resolve to `pending_stage2`) with the number of unique discrete lifecycle state codes.

### Formal Correction
All documentation, specs, and references are formally corrected to state:
> **"6 lifecycle states"**

---

## 2. Issue B — Query Complexity Wording Reconciliation

### Audit Finding
Documentation in Phase D2.9 occasionally used phrasing such as:
- *"Constant $O(1)$ query execution"*
- *"PASS — Constant $O(1)$ query count"*

### Technical Precision & Governance Rationale
In relational database systems and Django ORM testing, `assertNumQueries(k)` verifies that the number of round-trip SQL queries executed to render a view is constant (e.g., exactly 1 query for Review Queue, exactly 2 queries for paginated Screening History), regardless of the number of items ($N$) displayed in the view.

However, in computational complexity theory:
- Constant SQL query count does **not** imply constant $O(1)$ computational cost or execution time for all database work. The database engine must still perform index lookups, filter evaluations, and relational joins whose internal cost scales with table size (e.g., $O(\log M)$ or $O(M)$).
- Conflating bounded SQL query count with computational complexity can be misleading during academic examination and software architecture defense.

### Formal Correction
All statements equivalent to *"O(1) query execution"* are replaced with:
> **"a bounded / constant number of SQL queries per rendered page"**

This precisely communicates the architectural property verified by the automated test suite (complete elimination of $N+1$ query loops via eager `select_related`) without asserting unverified asymptotic computational bounds for the underlying relational engine.

---

## 3. Reconciled Artifacts
- `design/d2_9/SCREENING_LIFECYCLE_CONTRACT.md`: Confirmed 6 active lifecycle states.
- `design/d2_9/D2_9_IMPLEMENTATION_REPORT.md`: Reconciled state count and query wording.
- `PROJECT_MASTER_RECAP.md` (and `docs/PROJECT_MASTER_RECAP.md`): Updated Section 33 to "6 lifecycle states" and "a bounded / constant number of SQL queries per rendered page".
