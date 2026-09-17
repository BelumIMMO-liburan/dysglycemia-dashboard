# Phase D2.10 Data Integrity Audit

**Phase:** D2.10 — Research Analytics + Human–AI Decision Flow  
**Auditor:** Antigravity AI  
**Execution Date:** 2026-09-05  
**Audit Scope:** Service Invariants, Denominator Boundaries, Legacy Table Isolation, and Division-by-Zero Safety.

---

## 1. Mathematical Invariant Verification

| Invariant ID | Formulation | Enforcement Point | Status | Test Coverage |
| :--- | :--- | :--- | :--- | :--- |
| **INV-01** | $N_{\text{reviewed}} \le N_{\text{review\_eligible}}$ | `research_analytics.py:277` | **PASS** | `test_review_completion_rate_denominator` |
| **INV-02** | $N_{\text{accepted}} + N_{\text{overridden}} == N_{\text{reviewed}}$ | `research_analytics.py:282` | **PASS** | `test_agreement_plus_override_invariant` |
| **INV-03** | $\sum(\text{Transition Cells}) == N_{\text{reviewed}}$ | `research_analytics.py:287` | **PASS** | `test_decision_transition_matrix_invariants` |
| **INV-04** | $\text{Transition Diagonal} == N_{\text{accepted}}$ | `research_analytics.py:292` | **PASS** | `test_decision_transition_matrix_invariants` |
| **INV-05** | $\text{Transition Off-Diagonal} == N_{\text{overridden}}$ | `research_analytics.py:297` | **PASS** | `test_decision_transition_matrix_invariants` |
| **INV-06** | $N_{\text{stage2\_completed}} \le N_{\text{stage2\_eligible}}$ | `research_analytics.py:302` | **PASS** | `test_stage2_completion_rate_denominator` |
| **INV-07** | $\sum(\text{Stage-2 Ranges}) == N_{\text{stage2\_completed}}$ | `research_analytics.py:307` | **PASS** | `test_stage2_laboratory_range_distribution` |
| **INV-08** | $\sum(\text{Structured Reasons}) == N_{\text{overridden}}$ | `research_analytics.py:313` | **PASS** | `test_override_structured_reasons` |

---

## 2. Division-by-Zero Safeguard Audit
- **Requirement:** Undefined rates (where denominator is zero) must strictly return `None` rather than `0.0%` or raising `ZeroDivisionError`.
- **Implementation:**
  ```python
  def safe_rate(numerator: int, denominator: int) -> Optional[float]:
      if denominator <= 0:
          return None
      return round((numerator / denominator) * 100.0, 1)
  ```
- **Template Handling:** `{% if rate is not None %}{{ rate|floatformat:1 }}%{% else %}—{% endif %}`.
- **Audit Verification:** `ResearchAnalyticsServiceUnitTests.test_division_by_zero_safety` tested on empty queryset; all 9 rates returned `None` and template safely rendered without unhandled exceptions.

---

## 3. Legacy Entity & Development Data Isolation
- Active analytics query **only** active domain entities (`ScreeningRecord`, `ScreeningExplanation`, `HumanReview`, `Stage2Assessment`).
- `Prediction` and `Override` tables from legacy prototypes are completely unreferenced.
- `final_test_predictions.csv` and development training splits are completely unreferenced by D2.10.
- Verified by `test_legacy_records_exclusion`: adding dummy rows to `Prediction` leaves operational analytics metrics 100% unaltered.
